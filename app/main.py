#!/usr/bin/env python3
"""
图片处理工具套件 - PyQt6版本
"""

import sys
import os
# 添加当前目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QFontDatabase
from ui.main_window import MainWindow
from ui.theme import Theme, FontSize


def setup_font(app):
    """设置应用程序字体"""
    # 字体优先级列表（从高到低）
    font_families = [
        "Microsoft YaHei UI",     # 微软雅黑UI（Windows简体中文）
        "Microsoft YaHei",        # 微软雅黑（Windows简体中文备选）
        "PingFang SC",            # 苹方（macOS简体中文）
        "Segoe UI",               # Segoe UI（Windows英文）
        "SF Pro Display",         # SF Pro（macOS英文）
        "Noto Sans CJK SC",       # Noto Sans CJK（Linux）
        "Source Han Sans SC",     # 思源黑体（跨平台）
        "sans-serif"              # 系统默认无衬线字体
    ]

    # 获取系统可用字体
    available_fonts = QFontDatabase.families()

    # 选择第一个可用的字体
    selected_font = "sans-serif"
    for font_family in font_families:
        if font_family in available_fonts:
            selected_font = font_family
            break

    # 设置应用程序默认字体
    font = QFont(selected_font, FontSize.BODY)
    font.setHintingPreference(QFont.HintingPreference.PreferNoHinting)
    app.setFont(font)

    print(f"应用字体: {selected_font} (大小: {FontSize.BODY}pt)")

    return selected_font


def setup_theme(app, font_family):
    """设置应用程序主题"""
    # 设置全局样式表以实现深色主题
    app.setStyleSheet(f"""
        QMainWindow {{
            background-color: {Theme.BG_DARK};
        }}

        QWidget {{
            background-color: {Theme.BG_DARK};
            color: {Theme.TEXT_PRIMARY};
            font-family: "{font_family}", sans-serif;
            font-size: {FontSize.BODY}pt;
        }}

        QFrame {{
            background-color: {Theme.BG_MEDIUM};
            border: none;
        }}

        QLabel {{
            color: {Theme.TEXT_PRIMARY};
            background-color: transparent;
        }}

        QPushButton {{
            background-color: {Theme.BG_LIGHT};
            color: {Theme.TEXT_PRIMARY};
            border: 1px solid {Theme.BORDER_LIGHT};
            padding: 8px 16px;
            border-radius: 4px;
            font-weight: 500;
        }}

        QPushButton:hover {{
            background-color: {Theme.BG_CARD};
            border: 1px solid {Theme.BORDER_FOCUS};
        }}

        QPushButton:pressed {{
            background-color: {Theme.PRIMARY};
            border: 1px solid {Theme.PRIMARY};
        }}

        QPushButton:disabled {{
            background-color: {Theme.BG_MEDIUM};
            color: {Theme.TEXT_DISABLED};
            border: 1px solid {Theme.BORDER_DARK};
        }}

        QLineEdit, QTextEdit, QSpinBox, QComboBox {{
            background-color: {Theme.BG_LIGHT};
            border: 1px solid {Theme.BORDER_LIGHT};
            border-radius: 4px;
            padding: 5px;
            color: {Theme.TEXT_PRIMARY};
        }}

        QLineEdit:focus, QTextEdit:focus, QSpinBox:focus, QComboBox:focus {{
            border: 1px solid {Theme.PRIMARY};
        }}

        QGroupBox {{
            background-color: {Theme.BG_MEDIUM};
            border: 1px solid {Theme.BORDER_FOCUS};
            border-radius: 6px;
            margin-top: 1ex;
            padding-top: 10px;
            font-weight: 600;
            color: {Theme.TEXT_PRIMARY};
        }}

        QGroupBox::title {{
            subcontrol-origin: margin;
            subcontrol-position: top left;
            left: 10px;
            padding: 0 5px;
            color: {Theme.TEXT_SECONDARY};
        }}

        QScrollBar:vertical {{
            background-color: {Theme.BG_MEDIUM};
            width: 15px;
            border: none;
        }}

        QScrollBar::handle:vertical {{
            background-color: {Theme.BORDER_LIGHT};
            border-radius: 7px;
            min-height: 20px;
        }}

        QScrollBar::handle:vertical:hover {{
            background-color: {Theme.BORDER_FOCUS};
        }}

        QScrollBar:horizontal {{
            background-color: {Theme.BG_MEDIUM};
            height: 15px;
            border: none;
        }}

        QScrollBar::handle:horizontal {{
            background-color: {Theme.BORDER_LIGHT};
            border-radius: 7px;
            min-width: 20px;
        }}

        QScrollBar::handle:horizontal:hover {{
            background-color: {Theme.BORDER_FOCUS};
        }}

        QCheckBox {{
            color: {Theme.TEXT_PRIMARY};
            spacing: 5px;
        }}

        QCheckBox::indicator {{
            width: 18px;
            height: 18px;
        }}

        QCheckBox::indicator:unchecked {{
            border: 1px solid {Theme.BORDER_LIGHT};
            background-color: {Theme.BG_LIGHT};
        }}

        QCheckBox::indicator:checked {{
            border: 1px solid {Theme.PRIMARY};
            background-color: {Theme.PRIMARY};
        }}
    """)


def main():
    app = QApplication(sys.argv)

    # 设置字体并获取选中的字体家族
    font_family = setup_font(app)

    # 使用选中的字体设置主题
    setup_theme(app, font_family)

    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()