#!/usr/bin/env python3
"""
启动提示对话框 - 显示应用程序启动进度
"""

from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel,
                             QProgressBar, QPushButton, QFrame, QApplication)
from PyQt6.QtCore import Qt, QTimer, QPropertyAnimation, QRect, pyqtSignal
from PyQt6.QtGui import QIcon, QFont
from pathlib import Path
import sys
import os
from app.ui.theme import Theme


class StartupDialog(QDialog):
    """启动提示对话框"""

    # 定义信号
    timeout = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.progress_timer = None
        self.pulse_animation = None
        self.progress = 0
        self.init_ui()
        self.start_animation()

    def init_ui(self):
        """初始化UI"""
        self.setFixedSize(400, 200)
        self.setWindowFlags(Qt.WindowType.Dialog | Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        # 设置模态
        self.setModal(True)

        # 创建主布局
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)

        # 创建图标和标题布局
        header_layout = QHBoxLayout()
        header_layout.setSpacing(15)

        # 应用图标
        icon_label = QLabel()
        icon_path = self.get_resource_path("icons/imagetrim.ico")
        print(f"尝试加载图标: {icon_path}")

        if icon_path and Path(icon_path).exists():
            icon = QIcon(str(icon_path))
            if not icon.isNull():
                pixmap = icon.pixmap(48, 48)
                if not pixmap.isNull():
                    icon_label.setPixmap(pixmap)
                    print("图标加载成功")
                else:
                    icon_label.setText("🖼️")
                    icon_label.setStyleSheet("font-size: 48px;")
                    print("像素图无效")
            else:
                icon_label.setText("🖼️")
                icon_label.setStyleSheet("font-size: 48px;")
                print("图标无效")
        else:
            icon_label.setText("🖼️")
            icon_label.setStyleSheet("font-size: 48px;")
            print(f"图标文件不存在: {icon_path}")

        header_layout.addWidget(icon_label)

        # 标题和描述
        text_layout = QVBoxLayout()
        text_layout.setSpacing(5)

        title_label = QLabel("ImageTrim")
        title_label.setStyleSheet(f"""
            QLabel {{
                color: {Theme.TEXT_PRIMARY};
                font-size: 24px;
                font-weight: bold;
            }}
        """)

        desc_label = QLabel("图片精简工具正在启动...")
        desc_label.setStyleSheet(f"""
            QLabel {{
                color: {Theme.TEXT_SECONDARY};
                font-size: 14px;
            }}
        """)

        text_layout.addWidget(title_label)
        text_layout.addWidget(desc_label)
        header_layout.addLayout(text_layout)
        header_layout.addStretch()

        main_layout.addLayout(header_layout)

        # 创建进度条
        self.progress_bar = QProgressBar()
        self.progress_bar.setFixedHeight(6)
        self.progress_bar.setRange(0, 0)  # 无限进度条
        self.progress_bar.setTextVisible(False)
        self.progress_bar.setStyleSheet(f"""
            QProgressBar {{
                background-color: {Theme.BG_DARK};
                border: none;
                border-radius: 3px;
            }}
            QProgressBar::chunk {{
                background-color: {Theme.PRIMARY};
                border-radius: 3px;
            }}
        """)

        main_layout.addWidget(self.progress_bar)

        # 创建状态标签
        self.status_label = QLabel("正在初始化组件...")
        self.status_label.setStyleSheet(f"""
            QLabel {{
                color: {Theme.TEXT_SECONDARY};
                font-size: 12px;
            }}
        """)
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(self.status_label)

        # 创建按钮布局
        button_layout = QHBoxLayout()
        button_layout.addStretch()

        # 取消按钮
        self.cancel_button = QPushButton("取消")
        self.cancel_button.setFixedSize(80, 30)
        self.cancel_button.setStyleSheet(f"""
            QPushButton {{
                background-color: {Theme.BG_DARK};
                color: {Theme.TEXT_PRIMARY};
                border: 1px solid {Theme.BORDER_LIGHT};
                border-radius: 4px;
                padding: 5px 15px;
                font-size: 12px;
            }}
            QPushButton:hover {{
                background-color: {Theme.BG_LIGHT};
            }}
            QPushButton:pressed {{
                background-color: {Theme.PRIMARY};
            }}
        """)
        self.cancel_button.clicked.connect(self.reject)

        button_layout.addWidget(self.cancel_button)
        main_layout.addLayout(button_layout)

        # 设置背景样式
        self.setStyleSheet(f"""
            QDialog {{
                background-color: {Theme.BG_CARD};
                border: 1px solid {Theme.BORDER_LIGHT};
                border-radius: 8px;
            }}
        """)

        # 设置定时器更新状态
        self.status_timer = QTimer()
        self.status_timer.timeout.connect(self.update_status)
        self.status_timer.start(2000)  # 每2秒更新一次状态

        # 设置超时
        self.timeout_timer = QTimer()
        self.timeout_timer.setSingleShot(True)
        self.timeout_timer.timeout.connect(self.on_timeout)
        self.timeout_timer.start(30000)  # 30秒超时

        # 初始化状态列表
        self.status_messages = [
            "正在初始化组件...",
            "正在加载主题资源...",
            "正在检查依赖项...",
            "正在准备用户界面...",
            "正在连接网络资源...",
            "即将完成..."
        ]
        self.current_status_index = 0

    def start_animation(self):
        """开始动画效果"""
        # 创建脉冲动画效果
        self.pulse_animation = QPropertyAnimation(self, b"windowOpacity")
        self.pulse_animation.setDuration(1000)
        self.pulse_animation.setStartValue(0.0)
        self.pulse_animation.setEndValue(1.0)
        self.pulse_animation.start()

    def update_status(self):
        """更新状态信息"""
        self.current_status_index = (self.current_status_index + 1) % len(self.status_messages)
        self.status_label.setText(self.status_messages[self.current_status_index])

    def on_timeout(self):
        """超时处理"""
        self.status_label.setText("启动超时，请检查网络连接...")
        self.cancel_button.setText("强制退出")

    def closeEvent(self, event):
        """关闭事件处理"""
        if self.status_timer:
            self.status_timer.stop()
        if self.timeout_timer:
            self.timeout_timer.stop()
        if self.pulse_animation:
            self.pulse_animation.stop()
        super().closeEvent(event)

    def reject(self):
        """拒绝对话框（取消按钮点击）"""
        self.timeout.emit()  # 发送超时信号
        super().reject()

    def set_complete(self):
        """设置启动完成"""
        self.status_label.setText("启动完成！")
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(100)

        # 短暂延迟后自动关闭
        QTimer.singleShot(500, self.accept)

    def get_resource_path(self, relative_path):
        """获取资源文件的绝对路径，支持 PyInstaller 和 Nuitka 打包环境"""
        from app.utils.resource_path import get_resource_path as get_res_path
        return get_res_path(relative_path)

  