#!/usr/bin/env python3
"""
图片处理工具套件 - PyQt6版本
"""

import sys
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from ui.main_window import MainWindow


def setup_theme(app):
    """设置应用程序主题"""
    # 设置应用程序字体
    font = QFont("Segoe UI", 9)
    app.setFont(font)
    
    # 设置全局样式表以实现深色主题
    app.setStyleSheet("""
        QMainWindow {
            background-color: #1e1e1e;
        }
        
        QWidget {
            background-color: #1e1e1e;
            color: #ffffff;
            font-family: "Segoe UI", sans-serif;
        }
        
        QFrame {
            background-color: #2d2d30;
            border: none;
        }
        
        QLabel {
            color: #ffffff;
            background-color: transparent;
        }
        
        QPushButton {
            background-color: #333337;
            color: #ffffff;
            border: 1px solid #454545;
            padding: 8px 16px;
            border-radius: 4px;
            font-weight: 500;
        }
        
        QPushButton:hover {
            background-color: #3f3f46;
            border: 1px solid #555555;
        }
        
        QPushButton:pressed {
            background-color: #0078d7;
            border: 1px solid #0078d7;
        }
        
        QPushButton:disabled {
            background-color: #2d2d30;
            color: #666666;
            border: 1px solid #3f3f46;
        }
        
        QLineEdit, QTextEdit, QSpinBox, QComboBox {
            background-color: #333337;
            border: 1px solid #454545;
            border-radius: 4px;
            padding: 5px;
            color: #ffffff;
        }
        
        QGroupBox {
            background-color: #2d2d30;
            border: 1px solid #3f3f46;
            border-radius: 6px;
            margin-top: 1ex;
            padding-top: 10px;
            font-weight: 600;
            color: #ffffff;
        }
        
        QGroupBox::title {
            subcontrol-origin: margin;
            subcontrol-position: top left;
            left: 10px;
            padding: 0 5px;
            color: #cccccc;
        }
        
        QProgressBar {
            border: 1px solid #454545;
            border-radius: 4px;
            text-align: center;
            background-color: #2d2d30;
        }
        
        QProgressBar::chunk {
            background-color: #0078d7;
            border-radius: 3px;
        }
        
        QScrollBar:vertical {
            background-color: #2d2d30;
            width: 15px;
            border: none;
        }
        
        QScrollBar::handle:vertical {
            background-color: #555555;
            border-radius: 7px;
            min-height: 20px;
        }
        
        QScrollBar::handle:vertical:hover {
            background-color: #666666;
        }
        
        QScrollBar:horizontal {
            background-color: #2d2d30;
            height: 15px;
            border: none;
        }
        
        QScrollBar::handle:horizontal {
            background-color: #555555;
            border-radius: 7px;
            min-width: 20px;
        }
        
        QScrollBar::handle:horizontal:hover {
            background-color: #666666;
        }
        
        QCheckBox {
            color: #ffffff;
            spacing: 5px;
        }
        
        QCheckBox::indicator {
            width: 18px;
            height: 18px;
        }
        
        QCheckBox::indicator:unchecked {
            border: 1px solid #454545;
            background-color: #333337;
        }
        
        QCheckBox::indicator:checked {
            border: 1px solid #0078d7;
            background-color: #0078d7;
        }
    """)


def main():
    app = QApplication(sys.argv)
    setup_theme(app)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()