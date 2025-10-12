#!/usr/bin/env python3
"""
关于对话框
"""

from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel,
                             QPushButton, QFrame)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap, QIcon
from pathlib import Path
import sys
import os
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

        # 设置对话框窗口图标 - 使用高分辨率图标
        dialog_icon_path = self.get_resource_path("icons/imageTrim256px.ico")
        if dialog_icon_path and Path(dialog_icon_path).exists():
            self.setWindowIcon(QIcon(dialog_icon_path))
            print(f"关于对话框窗口图标设置成功: {dialog_icon_path}")
        else:
            # 备用图标
            fallback_icon_path = self.get_resource_path("icons/imagetrim.ico")
            if fallback_icon_path and Path(fallback_icon_path).exists():
                self.setWindowIcon(QIcon(fallback_icon_path))
                print(f"关于对话框窗口图标设置成功（备用）: {fallback_icon_path}")
            else:
                print("关于对话框无法设置窗口图标")

        # 主布局
        layout = QVBoxLayout(self)
        layout.setContentsMargins(Spacing.XXL, Spacing.XXL, Spacing.XXL, Spacing.XXL)
        layout.setSpacing(Spacing.LG)

        # 图标区域 - 使用高分辨率图标
        icon_label = QLabel()
        icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # 优先使用高分辨率PNG图标
        icon_paths = [
            "icons/imageTrim256px.png",  # 高分辨率PNG（首选）
            "icons/imagetrim.ico",       # 备用ICO图标
            "icons/imageTrim48px.png",   # 中等分辨率备用
        ]

        icon_loaded = False
        for icon_path in icon_paths:
            full_path = self.get_resource_path(icon_path)
            print(f"关于对话框尝试加载图标: {full_path}")

            if full_path and Path(full_path).exists():
                pixmap = QPixmap(str(full_path))
                if not pixmap.isNull():
                    # 减小到原来的一半大小
                    if "256px" in icon_path:
                        scaled_pixmap = pixmap.scaled(60, 60, Qt.AspectRatioMode.KeepAspectRatio,
                                                      Qt.TransformationMode.SmoothTransformation)
                    else:
                        scaled_pixmap = pixmap.scaled(40, 40, Qt.AspectRatioMode.KeepAspectRatio,
                                                      Qt.TransformationMode.SmoothTransformation)
                    icon_label.setPixmap(scaled_pixmap)
                    print(f"关于对话框图标加载成功: {icon_path}")
                    icon_loaded = True
                    break
                else:
                    print(f"关于对话框像素图无效: {icon_path}")
            else:
                print(f"关于对话框图标文件不存在: {full_path}")

        if not icon_loaded:
            icon_label.setText("🖼️")
            icon_label.setStyleSheet(f"font-size: 24px;")  # emoji备份图标
            print("关于对话框未找到任何图标文件，使用emoji")

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

    def get_resource_path(self, relative_path):
        """获取资源文件的绝对路径，支持PyInstaller打包环境"""
        try:
            # PyInstaller创建临时文件夹，将路径存储在_MEIPASS中
            base_path = sys._MEIPASS
            print(f"PyInstaller环境 - MEIPASS: {base_path}")
        except Exception:
            # 开发环境
            base_path = os.path.abspath(".")
            print(f"开发环境 - 基础路径: {base_path}")

        # 根据PyInstaller的datas配置调整路径查找顺序
        # spec中配置: datas=[('app\\resources', 'resources')]
        # 这意味着app/resources会被映射到resources/
        possible_paths = []

        if getattr(sys, 'frozen', False):
            # PyInstaller打包环境 - resources直接在根目录
            possible_paths = [
                os.path.join(base_path, "resources", relative_path),  # 主要路径
                os.path.join(base_path, relative_path),                # 备用路径
            ]
            print("使用PyInstaller路径查找策略")
        else:
            # 开发环境
            possible_paths = [
                os.path.join("app", "resources", relative_path),      # 开发环境主要路径
                os.path.join(base_path, "app", "resources", relative_path),
                os.path.join(base_path, "resources", relative_path),
                os.path.join(base_path, relative_path),
            ]
            print("使用开发环境路径查找策略")

        print(f"查找的相对路径: {relative_path}")
        print("尝试的路径:")
        for i, path in enumerate(possible_paths):
            print(f"  {i+1}. {path}")
            if os.path.exists(path):
                print(f"      ✅ 找到文件!")
                return path
            else:
                print(f"      ❌ 不存在")

        print(f"❌ 所有路径都未找到文件: {relative_path}")
        return None
