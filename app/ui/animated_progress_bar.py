#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
带平滑动画的进度条组件
"""

from PyQt6.QtWidgets import QProgressBar
from PyQt6.QtCore import QPropertyAnimation, QEasingCurve, pyqtProperty, QTimer
from ui.theme import ProgressBarStyle, Animation
import time


class AnimatedProgressBar(QProgressBar):
    """
    带平滑动画效果的进度条
    继承自QProgressBar，添加了值变化的平滑过渡动画
    使用智能节流机制避免快速更新时的卡顿
    """

    def __init__(self, parent=None):
        super().__init__(parent)

        # 创建动画对象
        self.animation = QPropertyAnimation(self, b"value")
        self.animation.setDuration(Animation.NORMAL)  # 300ms 动画时长
        self.animation.setEasingCurve(QEasingCurve.Type.OutCubic)  # 缓出曲线

        # 应用样式
        self.setStyleSheet(ProgressBarStyle.get_style())

        # 设置默认范围
        self.setRange(0, 100)
        self.setValue(0)
        self.setFormat("准备就绪")

        # 智能节流机制：用于处理快速更新
        self._last_update_time = 0  # 上次更新时间戳
        self._throttle_ms = 150  # 节流间隔（毫秒）
        self._pending_value = None  # 待处理的进度值
        self._pending_message = None  # 待处理的消息
        self._update_timer = QTimer()  # 延迟更新定时器
        self._update_timer.setSingleShot(True)
        self._update_timer.timeout.connect(self._apply_pending_update)

    def setValueAnimated(self, value: int):
        """
        使用动画平滑设置进度条值

        Args:
            value: 目标值 (0-100)
        """
        # 计算进度差值
        current_value = self.value()
        diff = abs(value - current_value)

        # 根据差值动态调整动画时长
        # 小差值使用短动画，大差值使用长动画
        if diff <= 5:
            duration = 100  # 小步进使用100ms
        elif diff <= 20:
            duration = 200  # 中等步进使用200ms
        else:
            duration = 300  # 大步进使用300ms

        # 停止当前动画（如果正在运行）
        if self.animation.state() == QPropertyAnimation.State.Running:
            self.animation.stop()

        # 设置动画时长和值
        self.animation.setDuration(duration)
        self.animation.setStartValue(current_value)
        self.animation.setEndValue(value)

        # 启动动画
        self.animation.start()

    def setValue(self, value: int):
        """
        重写setValue方法，默认不使用动画
        如需动画效果，请使用setValueAnimated()
        """
        super().setValue(value)

    def updateProgress(self, value: float, message: str = None):
        """
        更新进度（带智能节流的动画）

        使用节流机制：
        - 如果距离上次更新时间 < 节流间隔，则将更新挂起
        - 挂起的更新会在节流间隔后自动应用
        - 这样可以避免快速更新时动画频繁重启导致的卡顿

        Args:
            value: 进度值 (0-100)
            message: 可选的进度消息
        """
        current_time = time.time() * 1000  # 转换为毫秒
        time_since_last_update = current_time - self._last_update_time

        # 存储待处理的值和消息
        self._pending_value = int(value)
        self._pending_message = message

        # 如果距离上次更新时间足够长，立即应用
        if time_since_last_update >= self._throttle_ms:
            self._apply_update(int(value), message)
            self._last_update_time = current_time
            # 停止可能正在等待的延迟更新
            if self._update_timer.isActive():
                self._update_timer.stop()
        else:
            # 否则，启动或重置延迟更新定时器
            # 等待剩余的节流时间后再应用更新
            remaining_time = int(self._throttle_ms - time_since_last_update)
            if not self._update_timer.isActive():
                self._update_timer.start(remaining_time)
            else:
                # 如果定时器已在运行，重置它
                self._update_timer.stop()
                self._update_timer.start(remaining_time)

    def _apply_update(self, value: int, message: str = None):
        """
        实际应用进度更新

        Args:
            value: 进度值 (0-100)
            message: 可选的进度消息
        """
        # 对于小于等于1%的差值，直接设置不使用动画，避免动画卡顿
        current_value = self.value()
        diff = abs(value - current_value)

        if diff <= 1:
            # 小差值直接设置，无动画
            super().setValue(value)
        else:
            # 较大差值使用动画
            self.setValueAnimated(value)

        # 更新消息文本
        if message:
            self.setFormat(f"{message} ({value}%)")
        else:
            self.setFormat(f"{value}%")

    def _apply_pending_update(self):
        """
        应用挂起的更新（由定时器触发）
        """
        if self._pending_value is not None:
            self._apply_update(self._pending_value, self._pending_message)
            self._last_update_time = time.time() * 1000
            self._pending_value = None
            self._pending_message = None

    def reset(self):
        """重置进度条"""
        self.animation.stop()
        if self._update_timer.isActive():
            self._update_timer.stop()
        self._pending_value = None
        self._pending_message = None
        self._last_update_time = 0
        self.setValue(0)
        self.setFormat("准备就绪")
