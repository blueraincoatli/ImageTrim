#!/usr/bin/env python3
"""
主窗口实现
"""

from PyQt6.QtWidgets import QMainWindow, QWidget, QHBoxLayout, QVBoxLayout, QSplitter, QFrame
from PyQt6.QtCore import Qt
from core.function_manager import FunctionManager
from ui.function_panel import FunctionPanel
from ui.settings_panel import SettingsPanel
from ui.workspace_panel import WorkspacePanel
from modules.deduplication import DeduplicationModule
from modules.avif_converter import AVIFConverterModule


class MainWindow(QMainWindow):
    """
    主窗口类
    """

    def __init__(self):
        super().__init__()
        self.function_manager = FunctionManager()
        self.function_panel = None
        self.settings_panel = None
        self.workspace_panel = None
        self.init_ui()
        self.register_modules()

    def init_ui(self):
        """初始化用户界面"""
        self.setWindowTitle("图片处理工具套件")
        self.setMinimumSize(1200, 700)
        
        # 创建主窗口部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # 创建主布局
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # 创建分割器
        splitter = QSplitter(Qt.Orientation.Horizontal)
        main_layout.addWidget(splitter)
        
        # 创建左栏框架
        left_frame = QFrame()
        left_frame.setObjectName("LeftFrame")
        left_layout = QVBoxLayout(left_frame)
        left_layout.setContentsMargins(0, 0, 0, 0)
        left_layout.setSpacing(0)
        
        # 创建左栏（功能选择面板）
        self.function_panel = FunctionPanel(self.function_manager)
        left_layout.addWidget(self.function_panel)
        
        # 创建左栏（设置面板）
        self.settings_panel = SettingsPanel(self.function_manager)
        left_layout.addWidget(self.settings_panel)
        
        splitter.addWidget(left_frame)
        
        # 创建右栏（工作区面板）
        self.workspace_panel = WorkspacePanel(self.function_manager)
        splitter.addWidget(self.workspace_panel)
        
        # 设置分割器比例
        splitter.setSizes([int(self.width() * 0.3), int(self.width() * 0.7)])
        
        # 连接信号
        self.function_panel.function_selected.connect(self.on_function_selected)
        self.function_manager.module_activated.connect(self.on_module_activated)
        
        # 设置样式
        self.setStyleSheet("""
            #LeftFrame {
                background-color: #252526;
                border-right: 1px solid #3f3f46;
            }
        """)
        
    def register_modules(self):
        """注册功能模块"""
        # 注册图片去重模块
        dedup_module = DeduplicationModule()
        self.function_manager.register_module(dedup_module)
        
        # 注册AVIF转换模块
        avif_module = AVIFConverterModule()
        self.function_manager.register_module(avif_module)
        
        # 更新功能面板
        self.function_panel.update_modules()
        
    def on_function_selected(self, module_name: str):
        """处理功能选择事件"""
        self.function_manager.activate_module(module_name)
        
    def on_module_activated(self, module_name: str):
        """处理模块激活事件"""
        module = self.function_manager.get_module(module_name)
        if module:
            # 更新设置面板
            self.settings_panel.update_ui(module)
            
            # 更新工作区面板
            self.workspace_panel.update_ui(module)