#!/usr/bin/env python3
"""
设置面板
"""

from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QLabel, QStackedWidget,
                             QFrame, QGraphicsDropShadowEffect)
from PyQt6.QtGui import QColor
from PyQt6.QtCore import Qt
from app.core.function_manager import FunctionManager
from app.core.base_module import BaseFunctionModule
from app.ui.theme import Theme, Spacing, Shadow, BorderRadius
from app.ui.about_widget import AboutWidget


class SettingsPanel(QWidget):
    """
    设置面板
    """

    def __init__(self, function_manager: FunctionManager):
        super().__init__()
        self.function_manager = function_manager
        self.stacked_widget = None
        self.module_settings = {}
        self.init_ui()

    def init_ui(self):
        """初始化UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(Spacing.LG, Spacing.LG, Spacing.LG, Spacing.LG)
        layout.setSpacing(Spacing.MD)

        # 标题
        self.title = QLabel("⚙️ 设置与进度")
        self.title.setObjectName("panel-title")
        self.title.setStyleSheet("""
            #panel-title {
                font-size: 16px;
                font-weight: bold;
                margin-bottom: 10px;
                color: white;
            }
        """)
        layout.addWidget(self.title)

        # 设置区域容器 - 简化边框，使用阴影效果
        container = QFrame()
        container.setMaximumHeight(300)  # 限制最大高度，避免遮挡功能卡片
        container.setStyleSheet(f"""
            QFrame {{
                background-color: {Theme.BG_MEDIUM};
                border: none;
                border-radius: {BorderRadius.LG}px;
            }}
        """)

        # 添加阴影效果到容器
        blur_radius, color_rgba, offset_x, offset_y = Shadow.panel_shadow()
        panel_shadow = QGraphicsDropShadowEffect()
        panel_shadow.setBlurRadius(blur_radius)
        panel_shadow.setColor(QColor(color_rgba))
        panel_shadow.setOffset(offset_x, offset_y)
        container.setGraphicsEffect(panel_shadow)

        container_layout = QVBoxLayout(container)
        container_layout.setContentsMargins(0, 0, 0, 0)

        # 设置区域
        self.stacked_widget = QStackedWidget()
        container_layout.addWidget(self.stacked_widget)
        layout.addWidget(container)

        # 添加关于信息作为默认显示
        about_widget = AboutWidget()
        self.stacked_widget.addWidget(about_widget)
        
    def update_ui(self, module: BaseFunctionModule):
        """更新UI以显示指定模块的设置"""
        # 检查是否已经为该模块创建了设置UI
        if module.name in self.module_settings:
            index = self.stacked_widget.indexOf(self.module_settings[module.name])
            self.stacked_widget.setCurrentIndex(index)
            return
            
        # 为模块创建设置UI
        settings_ui = module.create_settings_ui()
        if settings_ui:
            # 添加到堆叠部件
            index = self.stacked_widget.addWidget(settings_ui)
            self.module_settings[module.name] = settings_ui
            self.stacked_widget.setCurrentIndex(index)
        else:
            # 如果模块没有设置UI，显示默认消息
            default_widget = QWidget()
            default_layout = QVBoxLayout(default_widget)
            label = QLabel(f"模块 '{module.display_name}' 没有可用的设置选项")
            label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            label.setStyleSheet("color: white;")
            default_layout.addWidget(label)
            
            index = self.stacked_widget.addWidget(default_widget)
            self.module_settings[module.name] = default_widget
            self.stacked_widget.setCurrentIndex(index)