#!/usr/bin/env python3
"""
统计结果弹窗组件
"""

from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
                             QGraphicsDropShadowEffect)
from PyQt6.QtCore import Qt, QPropertyAnimation, QEasingCurve, pyqtSignal
from PyQt6.QtGui import QColor
from app.ui.theme import Theme, Spacing, FontSize, BorderRadius, Shadow, Animation


class StatsDialog(QDialog):
    """
    统计结果弹窗 - 显示操作完成后的统计信息
    """

    # 自定义信号
    action_requested = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setModal(True)
        self.setFixedSize(400, 220)  # 增加高度以容纳新按钮和提示文字

        # 去掉标题栏
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.Dialog)

        # 存储转换结果数据（用于删除原图功能）
        self.result_data = None

        # 设置窗口样式 - 使用项目主题，添加细边框
        self.setStyleSheet(f"""
            QDialog {{
                background-color: {Theme.BG_CARD};
                border-radius: {BorderRadius.XL}px;
                border: 1px solid {Theme.BORDER_LIGHT};
            }}
        """)

        # 添加阴影效果 - 使用项目主题
        shadow = QGraphicsDropShadowEffect()
        blur_radius, color_rgba, offset_x, offset_y = Shadow.card_shadow()
        shadow.setBlurRadius(blur_radius)
        shadow.setOffset(offset_x, offset_y)
        shadow.setColor(QColor(color_rgba))
        self.setGraphicsEffect(shadow)

        # 初始化UI
        self.init_ui()

        # 添加动画效果
        self.setup_animations()

    def init_ui(self):
        """初始化UI"""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(Spacing.XL, Spacing.XL, Spacing.XL, Spacing.XL)
        main_layout.setSpacing(Spacing.LG)

        # 简洁的统计信息显示 - 使用项目主题
        self.content_label = QLabel()
        self.content_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.content_label.setWordWrap(True)
        self.content_label.setStyleSheet(f"""
            QLabel {{
                color: {Theme.TEXT_PRIMARY};
                font-size: {FontSize.BODY}pt;
                line-height: 2.2;
                padding: {Spacing.MD}px;
            }}
        """)
        main_layout.addWidget(self.content_label)

        # 添加弹性空间
        main_layout.addStretch()

        # 提示文字（仅在转换完成时显示）
        self.hint_label = QLabel("选择删除原图，将移动文件到回收站")
        self.hint_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.hint_label.setStyleSheet(f"""
            QLabel {{
                color: {Theme.TEXT_SECONDARY};
                font-size: {FontSize.SMALL - 1}pt;
                padding: 0px;
                margin-bottom: {Spacing.SM}px;
            }}
        """)
        self.hint_label.hide()  # 默认隐藏
        main_layout.addWidget(self.hint_label)

        # 按钮布局 - 使用项目主题
        button_layout = QHBoxLayout()
        button_layout.setSpacing(Spacing.MD)
        button_layout.addStretch()

        # 删除原图按钮（仅在转换完成时显示）
        self.delete_btn = QPushButton("🗑️ 删除原图")
        self.delete_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {Theme.BG_LIGHT};
                color: {Theme.TEXT_PRIMARY};
                border: 1px solid {Theme.BORDER_LIGHT};
                padding: {Spacing.SM}px {Spacing.LG}px;
                border-radius: {BorderRadius.SM}px;
                font-size: {FontSize.SMALL}pt;
                font-weight: bold;
                min-width: 100px;
            }}
            QPushButton:hover {{
                background-color: {Theme.BG_MEDIUM};
                border-color: #FF6B6B;
                color: #FF6B6B;
            }}
            QPushButton:pressed {{
                background-color: {Theme.BG_DARK};
            }}
        """)
        self.delete_btn.clicked.connect(self.on_delete_originals)
        self.delete_btn.hide()  # 默认隐藏
        button_layout.addWidget(self.delete_btn)

        # 完成按钮
        self.close_btn = QPushButton("完成")
        self.close_btn.setStyleSheet(f"""
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
        self.close_btn.clicked.connect(self.accept)
        button_layout.addWidget(self.close_btn)

        button_layout.addStretch()
        main_layout.addLayout(button_layout)

    def setup_animations(self):
        """设置动画效果"""
        # 窗口出现动画 - 使用项目主题
        self.opacity_animation = QPropertyAnimation(self, b"windowOpacity")
        self.opacity_animation.setDuration(Animation.NORMAL)
        self.opacity_animation.setStartValue(0.0)
        self.opacity_animation.setEndValue(1.0)
        self.opacity_animation.setEasingCurve(QEasingCurve.Type.OutCubic)

    def showEvent(self, event):
        """显示事件触发动画"""
        super().showEvent(event)
        self.opacity_animation.start()

    def set_deduplication_results(self, result_data):
        """设置去重统计结果"""
        total_groups = result_data.get('total_groups', 0)
        total_duplicates = result_data.get('total_duplicates', 0)

        if total_groups == 0:
            content = "太棒了！没有发现重复图片，\n你的相册已经很整洁了。"
        else:
            content = f"找到了{total_groups}组重复的图片，\n共{total_duplicates}幅重复文件。\n天地间顿时松快了许多~"

        self.content_label.setText(content)

    def show_deduplication_operation_results(self, operation_type, processed_count, space_saved):
        """显示去重操作结果（删除/移动）"""
        space_mb = space_saved / (1024 * 1024)  # 转换为MB

        if operation_type == 'delete':
            content = f"删除了{processed_count}幅重复图片，\n总共节省了{space_mb:.1f}MB的空间！\n天地间顿时松快了许多~"
        elif operation_type == 'move':
            content = f"移动了{processed_count}幅重复图片，\n文件夹现在更有条理了。\n天地间顿时松快了许多~"
        else:
            return

        self.content_label.setText(content)

    def set_conversion_results(self, result_data):
        """设置转换统计结果"""
        # 保存结果数据（用于删除原图功能）
        self.result_data = result_data

        success_count = result_data.get('success_count', 0)
        total_size_before = result_data.get('total_size_before', 0)
        total_size_after = result_data.get('total_size_after', 0)
        format_name = result_data.get('format', 'AVIF')

        # 计算节省空间
        space_saved = total_size_before - total_size_after
        space_mb = space_saved / (1024 * 1024)  # 转换为MB

        if success_count == 0:
            content = "转换失败，\n请检查文件格式是否支持。"
            # 转换失败时不显示删除按钮
            self.delete_btn.hide()
            self.hint_label.hide()
        elif space_mb > 0:
            compression_ratio = (space_saved / total_size_before * 100) if total_size_before > 0 else 0
            content = f"成功转换了{success_count}张图片为{format_name}格式，\n压缩了{space_mb:.1f}MB空间（{compression_ratio:.1f}%），\n图片更轻巧了！"
            # 转换成功时显示删除按钮和提示
            self.delete_btn.show()
            self.hint_label.show()
        else:
            content = f"成功转换了{success_count}张图片为{format_name}格式。\n图片格式优化完成！"
            # 转换成功时显示删除按钮和提示
            self.delete_btn.show()
            self.hint_label.show()

        self.content_label.setText(content)

    def on_delete_originals(self):
        """删除原图按钮点击事件"""
        if not self.result_data:
            return

        # 获取成功转换的原图路径列表
        original_files = self.result_data.get('original_files', [])
        if not original_files:
            from PyQt6.QtWidgets import QMessageBox
            QMessageBox.warning(self, "无法删除", "没有找到需要删除的原图文件。")
            return

        # 确认对话框
        from PyQt6.QtWidgets import QMessageBox
        reply = QMessageBox.question(
            self,
            "确认删除",
            f"确定要将 {len(original_files)} 个原图文件移动到回收站吗？\n\n此操作可以从回收站恢复。",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            # 发送删除原图的信号
            self.action_requested.emit("delete_originals")
            # 关闭对话框
            self.accept()

    def on_primary_clicked(self):
        """主按钮点击事件"""
        self.action_requested.emit("primary_action")