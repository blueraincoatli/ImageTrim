#!/usr/bin/env python3
"""
关于信息组件 - 用于设置面板初始状态
"""

from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap
import sys
import os
from pathlib import Path
from app.ui.theme import Theme, FontSize, Spacing


class AboutWidget(QWidget):
    """
    关于信息组件 - 显示在设置面板中
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()

    def get_resource_path(self, relative_path):
        """获取资源文件的绝对路径，支持 PyInstaller 和 Nuitka 打包环境"""
        from app.utils.resource_path import get_resource_path as get_res_path
        return get_res_path(relative_path)

    def init_ui(self):
        """初始化UI"""
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.setContentsMargins(Spacing.XL, Spacing.XL, Spacing.XL, Spacing.XL)
        layout.setSpacing(Spacing.SM)

        # Logo图标 - 使用较小尺寸，更清晰的显示
        icon_label = QLabel()
        icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # 尝试加载高精度logo图标
        icon_paths = [
            "icons/imageTrim256px.png",  # 高分辨率PNG（首选）
            "icons/imageTrim256px.ico",   # 高分辨率ICO备用
            "icons/imagetrim.ico",        # 标准ICO备用
            "icons/imageTrimbg-01.svg",   # SVG备用
            "icons/imagetrim_final.svg"   # SVG备用2
        ]

        icon_loaded = False
        for icon_path in icon_paths:
            full_path = self.get_resource_path(icon_path)
            if full_path:
                try:
                    pixmap = QPixmap(full_path)
                    if not pixmap.isNull():
                        # 减小到原来的一半大小 (50x50)
                        scaled_pixmap = pixmap.scaled(50, 50, Qt.AspectRatioMode.KeepAspectRatio,
                                                      Qt.TransformationMode.SmoothTransformation)
                        icon_label.setPixmap(scaled_pixmap)
                        icon_loaded = True
                        print(f"成功加载高精度logo图标: {full_path}")
                        break
                except Exception as e:
                    print(f"加载图标失败 {full_path}: {e}")
                    continue

        if not icon_loaded:
            icon_label.setText("🖼️")
            icon_label.setStyleSheet("font-size: 20px;")  # emoji备份图标
            print("未找到logo图标文件，使用emoji替代")

        layout.addWidget(icon_label)

        # 应用名称和功能
        app_name = QLabel("ImageTrim")
        app_name.setAlignment(Qt.AlignmentFlag.AlignCenter)
        app_name.setStyleSheet(f"""
            font-size: {int(FontSize.H1 * 0.8)}pt;
            font-weight: bold;
            color: {Theme.TEXT_PRIMARY};
        """)
        layout.addWidget(app_name)

        subtitle = QLabel("图片精简工具")
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        subtitle.setStyleSheet(f"""
            font-size: {int(FontSize.H2 * 0.8)}pt;
            color: {Theme.TEXT_SECONDARY};
        """)
        layout.addWidget(subtitle)

        # 版本信息
        version = QLabel("版本 1.0.0")
        version.setAlignment(Qt.AlignmentFlag.AlignCenter)
        version.setStyleSheet(f"""
            font-size: {int(FontSize.BODY * 0.8)}pt;
            color: {Theme.TEXT_SECONDARY};
        """)
        layout.addWidget(version)

        # 作者信息
        author = QLabel("小红书: 919722379")
        author.setAlignment(Qt.AlignmentFlag.AlignCenter)
        author.setStyleSheet(f"""
            font-size: {int(FontSize.BODY * 0.8)}pt;
            color: {Theme.TEXT_SECONDARY};
        """)
        layout.addWidget(author)

        # 版权信息
        copyright_info = QLabel("© 2025 ImageTrim")
        copyright_info.setAlignment(Qt.AlignmentFlag.AlignCenter)
        copyright_info.setStyleSheet(f"""
            font-size: {int(FontSize.SMALL * 0.8)}pt;
            color: {Theme.TEXT_DISABLED};
        """)
        layout.addWidget(copyright_info)


        # 添加弹性空间
        layout.addStretch()
