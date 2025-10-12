#!/usr/bin/env python3
"""
关于信息组件 - 用于设置面板初始状态
"""

from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap
from pathlib import Path
from app.ui.theme import Theme, FontSize, Spacing


class AboutWidget(QWidget):
    """
    关于信息组件 - 显示在设置面板中
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()

    def init_ui(self):
        """初始化UI"""
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.setContentsMargins(Spacing.XL, Spacing.XL, Spacing.XL, Spacing.XL)
        layout.setSpacing(Spacing.SM)

        # Logo图标 - 使用较小尺寸，更清晰的显示
        icon_label = QLabel()
        icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # 尝试加载用户自己的logo图标
        icon_paths = [
            Path(__file__).parent.parent / "resources" / "icons" / "imageTrimbg-01.svg",
            Path(__file__).parent.parent / "resources" / "icons" / "imageTrim256px.png",
            Path(__file__).parent.parent / "resources" / "icons" / "imagetrim_final.svg"
        ]

        icon_loaded = False
        for icon_path in icon_paths:
            if icon_path.exists():
                try:
                    if icon_path.suffix.lower() == '.svg':
                        # SVG文件处理 - 这里简化处理为普通图标
                        pixmap = QPixmap(str(icon_path))
                    else:
                        pixmap = QPixmap(str(icon_path))

                    # 使用较小的尺寸
                    scaled_pixmap = pixmap.scaled(100, 100, Qt.AspectRatioMode.KeepAspectRatio,
                                                  Qt.TransformationMode.SmoothTransformation)
                    icon_label.setPixmap(scaled_pixmap)
                    icon_loaded = True
                    break
                except Exception as e:
                    print(f"加载图标失败 {icon_path}: {e}")
                    continue

        if not icon_loaded:
            icon_label.setText("🖼️")
            icon_label.setStyleSheet("font-size: 48px;")

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
