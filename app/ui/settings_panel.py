#!/usr/bin/env python3
"""
设置面板
"""

from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QStackedWidget, QFrame
from core.function_manager import FunctionManager
from core.base_module import BaseFunctionModule


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
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)
        
        # 标题
        self.title = QLabel("⚙️ 设置与进度")
        self.title.setStyleSheet("""
            font-size: 16px;
            font-weight: bold;
            margin-bottom: 10px;
            color: white;
        """)
        layout.addWidget(self.title)
        
        # 设置区域容器
        container = QFrame()
        container.setStyleSheet("""
            QFrame {
                background-color: #2d2d30;
                border: 1px solid #3f3f46;
                border-radius: 6px;
            }
        """)
        container_layout = QVBoxLayout(container)
        container_layout.setContentsMargins(0, 0, 0, 0)
        
        # 设置区域
        self.stacked_widget = QStackedWidget()
        container_layout.addWidget(self.stacked_widget)
        layout.addWidget(container)
        
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