#!/usr/bin/env python3
"""
UI辅助工具
"""

from PyQt6.QtWidgets import QMessageBox
from PyQt6.QtCore import Qt


class UIHelpers:
    """
    UI辅助工具类
    """

    @staticmethod
    def show_message(parent, title: str, message: str, msg_type: str = "info"):
        """
        显示消息对话框

        Args:
            parent: 父窗口
            title: 标题
            message: 消息内容
            msg_type: 消息类型 (info, warning, error, question)
        """
        msg_box = QMessageBox(parent)
        msg_box.setWindowTitle(title)
        msg_box.setText(message)
        
        if msg_type == "info":
            msg_box.setIcon(QMessageBox.Icon.Information)
        elif msg_type == "warning":
            msg_box.setIcon(QMessageBox.Icon.Warning)
        elif msg_type == "error":
            msg_box.setIcon(QMessageBox.Icon.Critical)
        elif msg_type == "question":
            msg_box.setIcon(QMessageBox.Icon.Question)
            
        msg_box.setStandardButtons(QMessageBox.StandardButton.Ok)
        msg_box.exec()

    @staticmethod
    def show_confirmation(parent, title: str, message: str) -> bool:
        """
        显示确认对话框

        Args:
            parent: 父窗口
            title: 标题
            message: 消息内容

        Returns:
            bool: 用户是否点击了"是"
        """
        reply = QMessageBox.question(
            parent, 
            title, 
            message,
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        return reply == QMessageBox.StandardButton.Yes

    @staticmethod
    def update_widget_selection_state(widget, is_selected: bool):
        """
        更新控件的选中状态

        Args:
            widget: 控件
            is_selected: 是否选中
        """
        if is_selected:
            widget.setStyleSheet("""
                border: 2px solid #FF8C00;
                background-color: #404040;
            """)
        else:
            widget.setStyleSheet("""
                border: 2px solid #333333;
                background-color: #353535;
            """)

    @staticmethod
    def format_file_size(size_bytes: int) -> str:
        """
        格式化文件大小

        Args:
            size_bytes: 字节大小

        Returns:
            str: 格式化后的文件大小
        """
        if size_bytes == 0:
            return "0 B"
            
        size_names = ["B", "KB", "MB", "GB", "TB"]
        i = 0
        while size_bytes >= 1024 and i < len(size_names) - 1:
            size_bytes /= 1024.0
            i += 1
            
        return f"{size_bytes:.1f} {size_names[i]}"