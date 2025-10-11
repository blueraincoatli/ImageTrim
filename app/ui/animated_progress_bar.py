#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
带平滑动画的进度条组件
"""

from PyQt6.QtWidgets import QProgressBar
from PyQt6.QtCore import QPropertyAnimation, QEasingCurve, pyqtProperty
from ui.theme import ProgressBarStyle, Animation


class AnimatedProgressBar(QProgressBar):
    """
    带平滑动画效果的进度条
    继承自QProgressBar，添加了值变化的平滑过渡动画
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

    def setValueAnimated(self, value: int):
        """
        使用动画平滑设置进度条值

        Args:
            value: 目标值 (0-100)
        """
        # 停止当前动画（如果正在运行）
        if self.animation.state() == QPropertyAnimation.State.Running:
            self.animation.stop()

        # 设置动画起始值和结束值
        self.animation.setStartValue(self.value())
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
        更新进度（带动画）

        Args:
            value: 进度值 (0-100)
            message: 可选的进度消息
        """
        self.setValueAnimated(int(value))
        if message:
            self.setFormat(f"{message} ({int(value)}%)")
        else:
            self.setFormat(f"{int(value)}%")

    def reset(self):
        """重置进度条"""
        self.animation.stop()
        self.setValue(0)
        self.setFormat("准备就绪")
