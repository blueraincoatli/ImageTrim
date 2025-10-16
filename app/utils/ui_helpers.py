#!/usr/bin/env python3
"""
UI辅助工具
"""

from PyQt6.QtWidgets import QMessageBox, QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QGraphicsDropShadowEffect
from PyQt6.QtCore import Qt, QPropertyAnimation, QEasingCurve
from PyQt6.QtGui import QColor
from app.ui.theme import Theme, Spacing, FontSize, BorderRadius, Shadow, Animation


class StyledMessageBox(QDialog):
    """
    统一样式的消息框 - 使用与 StatsDialog 相同的样式
    """

    def __init__(self, parent=None, title="", message="", icon_type="info", buttons=None):
        super().__init__(parent)
        self.setModal(True)
        self.setFixedWidth(400)

        # 去掉标题栏
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.Dialog)

        # 设置窗口样式 - 使用项目主题，添加细边框
        self.setStyleSheet(f"""
            QDialog {{
                background-color: {Theme.BG_CARD};
                border-radius: {BorderRadius.XL}px;
                border: 1px solid {Theme.BORDER_LIGHT};
            }}
        """)

        # 添加阴影效果
        shadow = QGraphicsDropShadowEffect()
        blur_radius, color_rgba, offset_x, offset_y = Shadow.card_shadow()
        shadow.setBlurRadius(blur_radius)
        shadow.setOffset(offset_x, offset_y)
        shadow.setColor(QColor(color_rgba))
        self.setGraphicsEffect(shadow)

        # 初始化UI
        self.init_ui(title, message, icon_type, buttons)

        # 添加动画效果
        self.setup_animations()

        self.result = None

    def init_ui(self, title, message, icon_type, buttons):
        """初始化UI"""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(Spacing.XL, Spacing.XL, Spacing.XL, Spacing.XL)
        main_layout.setSpacing(Spacing.LG)

        # 标题（如果有）
        if title:
            title_label = QLabel(title)
            title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            title_label.setStyleSheet(f"""
                QLabel {{
                    color: {Theme.TEXT_PRIMARY};
                    font-size: {FontSize.BODY + 2}pt;
                    font-weight: bold;
                    padding-bottom: {Spacing.SM}px;
                }}
            """)
            main_layout.addWidget(title_label)

        # 图标 + 消息内容
        icon_emoji = {
            "info": "ℹ️",
            "warning": "⚠️",
            "error": "❌",
            "question": "❓",
            "success": "✅"
        }.get(icon_type, "ℹ️")

        content_label = QLabel(f"{icon_emoji} {message}")
        content_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        content_label.setWordWrap(True)
        content_label.setStyleSheet(f"""
            QLabel {{
                color: {Theme.TEXT_PRIMARY};
                font-size: {FontSize.BODY}pt;
                line-height: 2.2;
                padding: {Spacing.MD}px;
            }}
        """)
        main_layout.addWidget(content_label)

        # 添加弹性空间
        main_layout.addStretch()

        # 按钮布局
        button_layout = QHBoxLayout()
        button_layout.setSpacing(Spacing.MD)
        button_layout.addStretch()

        # 默认按钮配置
        if buttons is None:
            buttons = ["OK"]

        for btn_text in buttons:
            btn = QPushButton(btn_text)
            btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: {Theme.BG_LIGHT};
                    color: {Theme.TEXT_PRIMARY};
                    border: 1px solid {Theme.BORDER_LIGHT};
                    padding: {Spacing.SM}px {Spacing.LG}px;
                    border-radius: {BorderRadius.SM}px;
                    font-size: {FontSize.SMALL}pt;
                    font-weight: bold;
                    min-width: 80px;
                }}
                QPushButton:hover {{
                    background-color: {Theme.BG_MEDIUM};
                    border-color: {Theme.PRIMARY};
                }}
                QPushButton:pressed {{
                    background-color: {Theme.BG_DARK};
                }}
            """)
            btn.clicked.connect(lambda checked, text=btn_text: self.on_button_clicked(text))
            button_layout.addWidget(btn)

        button_layout.addStretch()
        main_layout.addLayout(button_layout)

    def setup_animations(self):
        """设置动画效果"""
        self.opacity_animation = QPropertyAnimation(self, b"windowOpacity")
        self.opacity_animation.setDuration(Animation.NORMAL)
        self.opacity_animation.setStartValue(0.0)
        self.opacity_animation.setEndValue(1.0)
        self.opacity_animation.setEasingCurve(QEasingCurve.Type.OutCubic)

    def showEvent(self, event):
        """显示事件触发动画"""
        super().showEvent(event)
        self.opacity_animation.start()

    def on_button_clicked(self, button_text):
        """按钮点击处理"""
        self.result = button_text
        if button_text in ["OK", "确定", "是", "Yes"]:
            self.accept()
        else:
            self.reject()


class UIHelpers:
    """
    UI辅助工具类
    """

    # 统一的消息框最小宽度（已废弃，使用 StyledMessageBox 代替）
    MESSAGE_BOX_MIN_WIDTH = 400

    @staticmethod
    def set_message_box_width(msg_box: QMessageBox, min_width: int = None):
        """
        设置 QMessageBox 的最小宽度（已废弃，使用 show_styled_message 代替）

        Args:
            msg_box: QMessageBox 实例
            min_width: 最小宽度（像素），默认使用 MESSAGE_BOX_MIN_WIDTH
        """
        if min_width is None:
            min_width = UIHelpers.MESSAGE_BOX_MIN_WIDTH

        # 使用样式表设置最小宽度
        msg_box.setStyleSheet(f"""
            QMessageBox {{
                min-width: {min_width}px;
            }}
            QLabel {{
                min-width: {min_width - 100}px;
            }}
        """)

    @staticmethod
    def show_styled_message(parent, title: str, message: str, msg_type: str = "info", buttons=None):
        """
        显示统一样式的消息对话框

        Args:
            parent: 父窗口
            title: 标题
            message: 消息内容
            msg_type: 消息类型 (info, warning, error, question, success)
            buttons: 按钮列表，默认为 ["OK"]

        Returns:
            点击的按钮文本
        """
        if buttons is None:
            buttons = ["OK"]

        dialog = StyledMessageBox(parent, title, message, msg_type, buttons)
        dialog.exec()
        return dialog.result

    @staticmethod
    def show_message(parent, title: str, message: str, msg_type: str = "info"):
        """
        显示消息对话框（使用统一样式）

        Args:
            parent: 父窗口
            title: 标题
            message: 消息内容
            msg_type: 消息类型 (info, warning, error, question)
        """
        UIHelpers.show_styled_message(parent, title, message, msg_type, ["OK"])

    @staticmethod
    def show_confirmation(parent, title: str, message: str) -> bool:
        """
        显示确认对话框（使用统一样式）

        Args:
            parent: 父窗口
            title: 标题
            message: 消息内容

        Returns:
            bool: 用户是否点击了"是"
        """
        result = UIHelpers.show_styled_message(parent, title, message, "question", ["是", "否"])
        return result == "是"

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