#!/usr/bin/env python3
"""
关于对话框
"""

from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel,
                             QPushButton, QFrame)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap, QIcon
from pathlib import Path
from app.ui.theme import Theme, FontSize, Spacing


class AboutDialog(QDialog):
    """
    关于对话框 - 显示应用程序信息
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()

    def init_ui(self):
        """初始化UI"""
        self.setWindowTitle("关于 ImageTrim")
        self.setFixedSize(500, 400)
        self.setModal(True)

        # 主布局
        layout = QVBoxLayout(self)
        layout.setContentsMargins(Spacing.XXL, Spacing.XXL, Spacing.XXL, Spacing.XXL)
        layout.setSpacing(Spacing.LG)

        # 图标区域
        icon_label = QLabel()
        icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        icon_path = Path(__file__).parent.parent / "resources" / "icons" / "imagetrim.ico"
        if icon_path.exists():
            pixmap = QPixmap(str(icon_path))
            # 缩放图标到合适大小
            scaled_pixmap = pixmap.scaled(80, 80, Qt.AspectRatioMode.KeepAspectRatio,
                                          Qt.TransformationMode.SmoothTransformation)
            icon_label.setPixmap(scaled_pixmap)
        else:
            icon_label.setText("🖼️")
            icon_label.setStyleSheet(f"font-size: 64px;")
        layout.addWidget(icon_label)

        # 应用名称
        app_name = QLabel("ImageTrim")
        app_name.setAlignment(Qt.AlignmentFlag.AlignCenter)
        app_name.setStyleSheet(f"""
            font-size: {FontSize.H1}pt;
            font-weight: bold;
            color: {Theme.TEXT_PRIMARY};
            padding: {Spacing.SM}px 0;
        """)
        layout.addWidget(app_name)

        # 应用副标题
        app_subtitle = QLabel("图片精简工具")
        app_subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        app_subtitle.setStyleSheet(f"""
            font-size: {FontSize.H2}pt;
            color: {Theme.TEXT_SECONDARY};
            padding-bottom: {Spacing.MD}px;
        """)
        layout.addWidget(app_subtitle)

        # 版本信息
        version_label = QLabel("版本 1.0.0")
        version_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        version_label.setStyleSheet(f"""
            font-size: {FontSize.BODY}pt;
            color: {Theme.TEXT_SECONDARY};
        """)
        layout.addWidget(version_label)

        # 分隔线
        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.HLine)
        separator.setFrameShadow(QFrame.Shadow.Sunken)
        separator.setStyleSheet(f"""
            background-color: {Theme.BORDER_LIGHT};
            border: none;
            min-height: 1px;
            max-height: 1px;
        """)
        layout.addWidget(separator)

        # 描述信息
        description = QLabel(
            "ImageTrim 是一款专业的图片处理工具，\n"
            "提供图片去重、格式转换等实用功能，\n"
            "帮助您高效管理图片资源。"
        )
        description.setAlignment(Qt.AlignmentFlag.AlignCenter)
        description.setWordWrap(True)
        description.setStyleSheet(f"""
            font-size: {FontSize.BODY}pt;
            color: {Theme.TEXT_SECONDARY};
            line-height: 1.6;
            padding: {Spacing.MD}px 0;
        """)
        layout.addWidget(description)

        # 版权信息
        copyright_label = QLabel("© 2025 ImageTrim. All rights reserved.")
        copyright_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        copyright_label.setStyleSheet(f"""
            font-size: {FontSize.SMALL}pt;
            color: {Theme.TEXT_DISABLED};
            padding-top: {Spacing.MD}px;
        """)
        layout.addWidget(copyright_label)

        # 添加弹性空间
        layout.addStretch()

        # 按钮区域
        button_layout = QHBoxLayout()
        button_layout.setSpacing(Spacing.MD)

        # 添加弹性空间使按钮居中
        button_layout.addStretch()

        # 确定按钮
        ok_button = QPushButton("确定")
        ok_button.setMinimumWidth(100)
        ok_button.setStyleSheet(f"""
            QPushButton {{
                background-color: {Theme.PRIMARY};
                color: white;
                border: none;
                padding: {Spacing.SM}px {Spacing.LG}px;
                border-radius: 4px;
                font-weight: bold;
                font-size: {FontSize.BODY}pt;
            }}
            QPushButton:hover {{
                background-color: {Theme.PRIMARY_HOVER};
            }}
            QPushButton:pressed {{
                background-color: {Theme.PRIMARY_ACTIVE};
            }}
        """)
        ok_button.clicked.connect(self.accept)
        button_layout.addWidget(ok_button)

        button_layout.addStretch()

        layout.addLayout(button_layout)

        # 设置对话框样式
        self.setStyleSheet(f"""
            QDialog {{
                background-color: {Theme.BG_MEDIUM};
                border-radius: 8px;
            }}
        """)
