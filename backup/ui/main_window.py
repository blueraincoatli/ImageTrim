"""
PyQt6主窗口实现
"""

import sys
import os
from datetime import datetime
from typing import Dict, Any
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QSplitter, QFrame, QLabel, QSizePolicy)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QFont

from modules.function_manager import FunctionManager
from modules.deduplication_module import DeduplicationModule
from modules.avif_converter_module import AVIFConverterModule


class ModernApp(QMainWindow):
    """
    PyQt6版本现代化图片处理工具套件主程序
    - 采用PyQt6实现现代UI
    - 采用左右布局，左侧分为功能选择和设置区，右侧为操作区
    - 插件化架构，动态加载功能模块
    """
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("图片处理工具套件 - PyQt6版本")
        self.setGeometry(100, 100, 1400, 900)
        self.setMinimumSize(1200, 700)
        
        # 初始化功能管理器
        self.function_manager = self._setup_function_manager()
        
        # 设置自定义主题
        self._setup_custom_theme()
        
        # 创建主布局
        self._create_main_layout()
        
        # 加载并显示功能模块
        self._populate_function_list()
        
        # 默认激活去重功能模块
        self._activate_default_module()
        
        # 连接信号
        self._connect_signals()

    def _setup_function_manager(self) -> FunctionManager:
        """初始化功能管理器"""
        manager = FunctionManager()
        
        # 注册图片去重模块
        try:
            dedup_module = DeduplicationModule()
            manager.register_module(dedup_module)
            print("Successfully registered image deduplication module")
        except Exception as e:
            print(f"Failed to register image deduplication module: {e}")
        
        # 注册AVIF转换模块
        try:
            avif_module = AVIFConverterModule()
            manager.register_module(avif_module)
            print("Successfully registered AVIF converter module")
        except Exception as e:
            print(f"Failed to register AVIF converter module: {e}")
            
        return manager

    def _setup_custom_theme(self):
        """设置现代化深色主题"""
        # 设置应用程序字体
        font = QFont("Segoe UI", 10)
        QApplication.instance().setFont(font)

        # 应用现代化深色主题样式表
        modern_dark_stylesheet = """
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
            
            QFrame#LeftFrame {
                background-color: #252526;
                border-right: 1px solid #3f3f46;
            }
            
            QFrame#FunctionSelectorFrame {
                background-color: #252526;
            }
            
            QFrame#SettingsFrame {
                background-color: #252526;
            }
            
            QFrame#RightFrame {
                background-color: #1e1e1e;
            }
            
            QFrame#FunctionButtonsFrame {
                background-color: #2d2d30;
            }
            
            QFrame#SettingsContainer {
                background-color: #2d2d30;
            }
            
            QFrame#WorkspaceContainer {
                background-color: #1e1e1e;
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
                font-size: 10pt;
            }
            
            QPushButton:hover {
                background-color: #3f3f46;
                border: 1px solid #555555;
            }
            
            QPushButton:pressed {
                background-color: #0078d7;
                border: 1px solid #0078d7;
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
            
            QLineEdit {
                background-color: #333337;
                color: #ffffff;
                border: 1px solid #454545;
                border-radius: 4px;
                padding: 6px;
                selection-background-color: #0078d7;
            }
            
            QLineEdit:focus {
                border: 1px solid #0078d7;
            }
            
            QSlider::groove:horizontal {
                border: 1px solid #454545;
                height: 4px;
                background: #333337;
                border-radius: 2px;
            }
            
            QSlider::handle:horizontal {
                background: #0078d7;
                border: 1px solid #005a9e;
                width: 18px;
                height: 18px;
                margin: -7px 0;
                border-radius: 9px;
            }
            
            QSlider::sub-page:horizontal {
                background: #0078d7;
                border-radius: 2px;
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
            
            QProgressBar {
                border: 1px solid #454545;
                border-radius: 4px;
                text-align: center;
                background-color: #333337;
            }
            
            QProgressBar::chunk {
                background-color: #0078d7;
                border-radius: 3px;
            }
            
            QTextEdit {
                background-color: #333337;
                color: #ffffff;
                border: 1px solid #454545;
                border-radius: 4px;
                selection-background-color: #0078d7;
            }
            
            QListWidget {
                background-color: #333337;
                color: #ffffff;
                border: 1px solid #454545;
                border-radius: 4px;
                alternate-background-color: #2d2d30;
            }
            
            QListWidget::item {
                padding: 6px;
            }
            
            QListWidget::item:selected {
                background-color: #0078d7;
            }
            
            QSplitter::handle {
                background-color: #3f3f46;
            }
            
            QSplitter::handle:hover {
                background-color: #0078d7;
            }
        """
        
        QApplication.instance().setStyleSheet(modern_dark_stylesheet)

    def _create_main_layout(self):
        """创建现代化左右布局，左栏分为上下两部分"""
        # 创建中央窗口部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # 创建主水平分割器，用于分隔左侧功能区和右侧操作区
        main_splitter = QSplitter(Qt.Orientation.Horizontal)
        main_splitter.setHandleWidth(1)
        main_splitter.setObjectName("MainSplitter")
        
        # 左侧框架（功能选择 + 设置控制）
        self.left_frame = QFrame()
        self.left_frame.setObjectName("LeftFrame")
        
        # 创建左侧垂直分割器，用于分隔功能选择和设置
        left_splitter = QSplitter(Qt.Orientation.Vertical)
        left_splitter.setHandleWidth(1)
        left_splitter.setObjectName("LeftSplitter")
        
        # 左上部分 (功能选择面板)
        self.function_selector_frame = QFrame()
        self.function_selector_frame.setObjectName("FunctionSelectorFrame")
        
        # 功能按钮容器
        self.function_buttons_frame = QFrame()
        self.function_buttons_frame.setObjectName("FunctionButtonsFrame")
        
        # 为功能按钮容器设置布局
        function_buttons_layout = QVBoxLayout(self.function_buttons_frame)
        function_buttons_layout.setContentsMargins(10, 10, 10, 10)
        function_buttons_layout.setSpacing(8)
        
        # 布局功能选择面板
        function_layout = QVBoxLayout(self.function_selector_frame)
        function_layout.setContentsMargins(0, 0, 0, 0)
        function_layout.setSpacing(0)
        function_layout.addWidget(self.function_buttons_frame)
        
        # 左下部分 (设置控制面板)
        self.settings_frame = QFrame()
        self.settings_frame.setObjectName("SettingsFrame")
        
        # 设置容器
        self.settings_container = QFrame()
        self.settings_container.setObjectName("SettingsContainer")
        
        # 为设置容器设置布局
        settings_layout_container = QVBoxLayout(self.settings_container)
        settings_layout_container.setContentsMargins(10, 10, 10, 10)
        settings_layout_container.setSpacing(10)
        
        # 布局设置控制面板
        settings_layout = QVBoxLayout(self.settings_frame)
        settings_layout.setContentsMargins(0, 0, 0, 0)
        settings_layout.setSpacing(0)
        settings_layout.addWidget(self.settings_container)
        
        # 将左右部分添加到左侧分割器
        left_splitter.addWidget(self.function_selector_frame)
        left_splitter.addWidget(self.settings_frame)
        
        # 设置初始大小比例 (功能选择40%，设置60%)
        left_splitter.setSizes([400, 600])
        
        # 将左侧分割器添加到左侧框架
        left_layout = QVBoxLayout(self.left_frame)
        left_layout.setContentsMargins(0, 0, 0, 0)
        left_layout.addWidget(left_splitter)
        
        # 右侧部分 (操作区)
        self.right_frame = QFrame()
        self.right_frame.setObjectName("RightFrame")
        
        # 操作区容器
        self.workspace_container = QFrame()
        self.workspace_container.setObjectName("WorkspaceContainer")
        
        # 为操作区容器设置布局
        workspace_layout = QVBoxLayout(self.workspace_container)
        workspace_layout.setContentsMargins(10, 10, 10, 10)
        workspace_layout.setSpacing(10)
        
        # 布局操作区
        right_layout = QVBoxLayout(self.right_frame)
        right_layout.setContentsMargins(0, 0, 0, 0)
        right_layout.setSpacing(0)
        right_layout.addWidget(self.workspace_container)
        
        # 将左右部分添加到主分割器
        main_splitter.addWidget(self.left_frame)
        main_splitter.addWidget(self.right_frame)
        
        # 设置初始大小比例 (左栏30%，右栏70%)
        main_splitter.setSizes([350, 850])
        
        # 布局中央窗口部件
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(main_splitter)

    def _populate_function_list(self):
        """根据加载的模块创建功能按钮"""
        self.module_buttons = {}
        for name in self.function_manager.get_module_names():
            module = self.function_manager.get_module(name)
            
            # 创建一体化功能卡片
            card_container = QFrame()
            card_container.setStyleSheet(
                """
                QFrame {
                    background-color: #1B1B1B;
                    border: 1px solid #353535;
                    border-radius: 8px;
                    padding: 15px;
                }
                QFrame:hover {
                    background-color: #252525;
                }
                """
            )
            card_container.setCursor(Qt.CursorShape.PointingHandCursor)
            card_layout = QVBoxLayout(card_container)
            card_layout.setContentsMargins(0, 0, 0, 0)
            card_layout.setSpacing(10)
            
            # 功能标题
            title_label = QLabel(f"{module.icon} {module.display_name}")
            title_label.setStyleSheet("color: white; font-size: 16px; font-weight: bold; padding: 0px; border: none;")
            title_label.setWordWrap(True)
            
            # 功能描述
            desc_label = QLabel(module.description)
            desc_label.setStyleSheet("color: #CCCCCC; font-size: 12px; padding: 0px; border: none;")
            desc_label.setWordWrap(True)
            desc_label.setAlignment(Qt.AlignmentFlag.AlignTop)
            
            # 添加组件到卡片
            card_layout.addWidget(title_label)
            card_layout.addWidget(desc_label)
            card_layout.addStretch()
            
            # 连接点击事件（使用延迟处理避免绘制冲突）
            def make_click_handler(module):
                def click_handler(event):
                    self._handle_module_click(module)
                return click_handler
            
            card_container.mousePressEvent = make_click_handler(module)
            
            # 添加到功能按钮框架
            self.function_buttons_frame.layout().addWidget(card_container)
            
            self.module_buttons[name] = {
                'container': card_container,
                'module': module
            }

    def _handle_module_click(self, module):
        """处理模块点击事件"""
        # 使用定时器延迟处理，避免绘制冲突
        self.pending_module = module
        QTimer.singleShot(10, self._delayed_ui_update)

    def _delayed_ui_update(self):
        """延迟UI更新，避免绘制冲突"""
        if hasattr(self, 'pending_module') and self.pending_module:
            self._switch_module(self.pending_module)
            self.pending_module = None

    def _switch_module(self, module):
        """切换功能模块"""
        # 先停用当前模块
        if self.function_manager.active_module:
            self.function_manager.active_module.on_deactivate()
            
        # 激活新模块
        self.function_manager.activate_module(module.name)
        self._update_ui_for_module(module)

    def _update_ui_for_module(self, module):
        """更新UI以反映当前模块"""
        # 更新高亮状态
        for name, widgets in self.module_buttons.items():
            if name == module.name:
                # 选中的卡片使用选中样式（橙色边框）
                widgets['container'].setStyleSheet(
                    """
                    QFrame {
                        background-color: #2D2D2D;
                        border: 2px solid #FF8C00;
                        border-radius: 8px;
                        padding: 15px;
                    }
                    """
                )
            else:
                # 未选中的卡片使用默认样式
                widgets['container'].setStyleSheet(
                    """
                    QFrame {
                        background-color: #1B1B1B;
                        border: 1px solid #353535;
                        border-radius: 8px;
                        padding: 15px;
                    }
                    QFrame:hover {
                        background-color: #252525;
                    }
                    """
                )

        # 清空现有UI
        self._clear_layout(self.settings_container.layout())
        self._clear_layout(self.workspace_container.layout())

        # 连接模块信号
        self._connect_module_signals(module)

        # 加载新UI
        try:
            # 让模块自己创建并返回它的设置UI面板（放在左侧下部）
            settings_panel = module.create_settings_ui()
            if settings_panel:
                self.settings_container.layout().addWidget(settings_panel)

            # 让模块创建工作区UI（放在右侧）
            workspace_panel = module.create_workspace_ui()
            if workspace_panel:
                self.workspace_container.layout().addWidget(workspace_panel)
            else:  # 如果模块没有单独的工作区UI，显示一个提示
                placeholder = QLabel(f"'{module.display_name}' 功能结果将显示在这里。")
                placeholder.setStyleSheet("color: #CCCCCC; font-size: 14px; padding: 20px;")
                self.workspace_container.layout().addWidget(placeholder)

        except Exception as e:
            error_label = QLabel(f"加载UI失败: {str(e)}")
            error_label.setStyleSheet("color: red; font-size: 14px; padding: 20px;")
            self.settings_container.layout().addWidget(error_label)
            print(f"[ERROR] Failed to load UI for module {module.name}: {e}")

    def _activate_default_module(self):
        """激活默认功能模块"""
        if "deduplication" in self.function_manager.get_module_names():
            self.function_manager.activate_module("deduplication")
            dedup_module = self.function_manager.get_module("deduplication")
            self._update_ui_for_module(dedup_module)
            print("默认模块 '图片去重' 已激活")
        elif self.function_manager.get_module_names():
            # 如果去重模块不可用，则激活第一个可用模块
            first_module_name = self.function_manager.get_module_names()[0]
            self.function_manager.activate_module(first_module_name)
            self._update_ui_for_module(self.function_manager.get_module(first_module_name))
            print(f"默认模块 '{first_module_name}' 已激活")

    def _connect_signals(self):
        """连接信号"""
        # 连接功能管理器信号
        self.function_manager.module_activated.connect(self._on_module_activated)
        
        # 连接当前激活模块的信号
        if self.function_manager.active_module:
            self._connect_module_signals(self.function_manager.active_module)

    def _on_module_activated(self, module_name: str):
        """当模块被激活时的处理"""
        print(f"模块 '{module_name}' 被激活")
        module = self.function_manager.get_module(module_name)
        if module:
            self._connect_module_signals(module)

    def _connect_module_signals(self, module):
        """连接模块信号到UI更新方法"""
        # 断开之前可能连接的信号
        try:
            module.progress_updated.disconnect(self._on_progress_updated)
        except TypeError:
            pass  # 信号未连接
            
        try:
            module.log_message.disconnect(self._on_log_message)
        except TypeError:
            pass  # 信号未连接
            
        # 连接新信号
        module.progress_updated.connect(self._on_progress_updated)
        module.log_message.connect(self._on_log_message)

    def _on_progress_updated(self, progress: float, message: str):
        """处理进度更新"""
        if hasattr(self, 'progress_bar') and self.progress_bar:
            self.progress_bar.setValue(int(progress))
        if hasattr(self, 'stats_label') and self.stats_label:
            self.stats_label.setText(message)

    def _on_log_message(self, message: str, level: str):
        """处理日志消息"""
        if hasattr(self, 'log_text') and self.log_text:
            timestamp = datetime.now().strftime("%H:%M:%S")
            formatted_message = f"[{timestamp}] [{level.upper()}] {message}"
            self.log_text.append(formatted_message)

    def _clear_layout(self, layout):
        """清空布局中的所有控件"""
        if layout is not None:
            while layout.count():
                child = layout.takeAt(0)
                if child.widget():
                    widget = child.widget()
                    widget.setParent(None)


def main():
    """主程序入口"""
    print("启动 PyQt6 图片处理工具套件...")
    
    # 创建应用程序实例
    app = QApplication(sys.argv)
    
    # 创建主窗口
    window = ModernApp()
    
    # 显示窗口
    window.show()
    
    # 运行应用程序
    return app.exec()


if __name__ == "__main__":
    sys.exit(main())