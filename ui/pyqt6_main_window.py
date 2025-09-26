import sys
import os
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QSplitter, QFrame, QLabel, QSizePolicy,
                             QPushButton)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QPalette, QColor

from modules.pyqt6_base_module import PyQt6BaseFunctionModule, PyQt6FunctionManager
from modules.pyqt6_deduplication_module import PyQt6DeduplicationModule
from modules.pyqt6_avif_converter_module import PyQt6AVIFConverterModule


class PyQt6ModernApp(QMainWindow):
    """
    PyQt6版本现代化图片处理工具套件主程序
    - 采用PyQt6实现现代UI
    - 采用左右布局，左侧分为功能选择和设置区，右侧为操作区
    - 插件化架构，动态加载功能模块
    """
    def __init__(self):
        super().__init__()
        print("初始化主窗口...")
        self.setWindowTitle("图片处理工具套件 - PyQt6版本")
        self.setGeometry(100, 100, 1400, 900)
        self.setMinimumSize(1200, 700)
        print("窗口属性设置完成")

        # 初始化功能管理器
        print("初始化功能管理器...")
        self.function_manager = self.setup_function_manager()
        print("功能管理器初始化完成")

        # 设置自定义主题和颜色
        print("设置自定义主题...")
        self.setup_custom_theme()
        print("自定义主题设置完成")

        # 创建主布局 (左右布局，左栏分上下两部分)
        print("创建主布局...")
        self.create_main_layout()
        print("主布局创建完成")

        # 加载并显示功能模块
        print("加载功能模块...")
        self.populate_function_list()
        print("功能模块加载完成")

        # 默认激活去重功能模块
        print("激活默认功能模块...")
        if "pyqt6_deduplication" in self.function_manager.get_module_names():
            self.function_manager.activate_module("pyqt6_deduplication")
            dedup_module = self.function_manager.get_module("pyqt6_deduplication")
            self.update_ui_for_module(dedup_module)
            print("默认模块 '图片去重' 已激活")
        elif self.function_manager.get_module_names():
            # 如果去重模块不可用，则激活第一个可用模块
            first_module_name = self.function_manager.get_module_names()[0]
            self.function_manager.activate_module(first_module_name)
            self.update_ui_for_module(self.function_manager.get_module(first_module_name))
            print(f"默认模块 '{first_module_name}' 已激活")
        print("默认功能模块准备完成")
        print("主窗口初始化完成")

    def setup_custom_theme(self):
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
            
            QLabel#ModuleTitle {
                font-size: 12pt;
                font-weight: 600;
                color: #ffffff;
            }
            
            QLabel#ModuleDescription {
                font-size: 10pt;
                color: #cccccc;
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
            
            QPushButton#ModuleButton {
                text-align: left;
                padding: 12px 16px;
                background-color: #2d2d30;
                border: none;
                border-radius: 6px;
                font-weight: 600;
            }
            
            QPushButton#ModuleButton:hover {
                background-color: #333337;
            }
            
            QPushButton#ModuleButton:checked {
                background-color: #0078d7;
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
            
            QScrollBar::sub-line:vertical, QScrollBar::add-line:vertical {
                height: 0px;
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
            
            QScrollBar::sub-line:horizontal, QScrollBar::add-line:horizontal {
                width: 0px;
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
                image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' width='16' height='16'%3E%3Cpath fill='%23ffffff' d='M9 16.17L4.83 12l-1.42 1.41L9 19 21 7l-1.41-1.41z'/%3E%3C/svg%3E");
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

    def setup_function_manager(self):
        """Initialize function manager"""
        manager = PyQt6FunctionManager()
        
        # Register PyQt6 version of deduplication module
        try:
            pyqt6_dedup_module = PyQt6DeduplicationModule()
            manager.register_module(pyqt6_dedup_module)
            print("Successfully registered image deduplication module")
        except Exception as e:
            print(f"Failed to register image deduplication module: {e}")
            import traceback
            traceback.print_exc()
        
        # Register PyQt6 version of AVIF converter module
        try:
            pyqt6_avif_converter_module = PyQt6AVIFConverterModule()
            manager.register_module(pyqt6_avif_converter_module)
            print("Successfully registered AVIF converter module")
        except Exception as e:
            print(f"Failed to register AVIF converter module: {e}")
            import traceback
            traceback.print_exc()
            
        return manager

    def create_main_layout(self):
        """创建现代化左右布局，左栏分为上下两部分"""
        # 创建中央窗口部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # 创建主水平分割器，用于分隔左侧功能区和右侧操作区
        main_splitter = QSplitter(Qt.Orientation.Horizontal)
        main_splitter.setHandleWidth(1)  # 设置分割条宽度
        main_splitter.setObjectName("MainSplitter")
        
        # 左侧框架（功能选择 + 设置控制）
        self.left_frame = QFrame()
        self.left_frame.setObjectName("LeftFrame")
        
        # 创建左侧垂直分割器，用于分隔功能选择和设置
        left_splitter = QSplitter(Qt.Orientation.Vertical)
        left_splitter.setHandleWidth(1)  # 设置分割条宽度
        left_splitter.setObjectName("LeftSplitter")
        
        # 左上部分 (功能选择面板)
        self.function_selector_frame = QFrame()
        self.function_selector_frame.setObjectName("FunctionSelectorFrame")
        
        # 功能选择标题
        function_title = QLabel("🔧 Function Selection")
        function_title.setObjectName("FunctionTitle")
        
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
        function_layout.addWidget(function_title)
        function_layout.addWidget(self.function_buttons_frame)
        
        # 左下部分 (设置控制面板)
        self.settings_frame = QFrame()
        self.settings_frame.setObjectName("SettingsFrame")
        
        # 设置标题
        settings_title = QLabel("⚙️ Settings")
        settings_title.setObjectName("SettingsTitle")
        
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
        settings_layout.addWidget(settings_title)
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
        
        # 操作区标题
        self.right_title = QLabel("🎯 Operations & Results")
        self.right_title.setObjectName("WorkspaceTitle")
        
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
        right_layout.addWidget(self.right_title)
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

    def populate_function_list(self):
        """根据加载的模块创建功能按钮"""
        self.module_buttons = {}
        for name in self.function_manager.get_module_names():
            module = self.function_manager.get_module(name)
            
            # 创建功能卡片按钮
            card_button = QPushButton(f"{module.icon} {module.display_name}")
            card_button.setObjectName(f"ModuleButton_{name}")
            card_button.setStyleSheet(
                f"""
                QPushButton {{
                    text-align: left;
                    padding: 15px;
                    background-color: #1B1B1B;
                    color: white;
                    border: none;
                    border-radius: 5px;
                    font-size: 14px;
                    font-weight: bold;
                }}
                QPushButton:hover {{
                    background-color: #353535;
                }}
                """
            )
            card_button.setCursor(Qt.CursorShape.PointingHandCursor)
            card_button.clicked.connect(lambda checked, m=module: self.switch_module(m))
            
            # 添加描述标签
            desc_label = QLabel(module.description)
            desc_label.setStyleSheet("color: #CCCCCC; font-size: 12px; padding: 0 15px 15px 15px;")
            desc_label.setWordWrap(True)
            
            # 创建包含按钮和描述的容器
            card_container = QWidget()
            card_layout = QVBoxLayout(card_container)
            card_layout.setContentsMargins(5, 5, 5, 5)
            card_layout.addWidget(card_button)
            card_layout.addWidget(desc_label)
            
            # 添加到功能按钮框架
            self.function_buttons_frame.layout().addWidget(card_container)
            
            self.module_buttons[name] = {
                'button': card_button, 
                'container': card_container,
                'module': module
            }

    def switch_module(self, module: PyQt6BaseFunctionModule):
        """切换功能模块"""
        # 先停用当前模块
        if self.function_manager.active_module:
            self.function_manager.active_module.on_deactivate()
            
        # 激活新模块
        self.function_manager.activate_module(module.name)
        self.update_ui_for_module(module)

    def update_ui_for_module(self, module: PyQt6BaseFunctionModule):
        """Update UI to reflect current module"""
        # 更新高亮状态
        for name, widgets in self.module_buttons.items():
            if name == module.name:
                # 选中的卡片使用选中样式（带橙色边框）
                widgets['container'].setStyleSheet(
                    """
                    QWidget {
                        background-color: #353535;
                        border: 2px solid #FF8C00;
                        border-radius: 5px;
                    }
                    """
                )
            else:
                # 未选中的卡片使用默认样式
                widgets['container'].setStyleSheet(
                    """
                    QWidget {
                        background-color: #1B1B1B;
                        border: none;
                        border-radius: 5px;
                    }
                    """
                )

        # 清空现有UI
        self.clear_layout(self.settings_container.layout())
        self.clear_layout(self.workspace_container.layout())

        # 更新标题
        self.right_title.setText(f"🎯 {module.display_name} Operations & Results")

        # 加载新UI
        try:
            # 让模块自己创建并返回它的设置UI面板（放在左侧下部）
            settings_panel = module.create_settings_ui(self.settings_container)
            if settings_panel:
                self.settings_container.layout().addWidget(settings_panel)

            # 让模块创建工作区UI（放在右侧）
            workspace_panel = module.create_workspace_ui(self.workspace_container)
            if workspace_panel:
                self.workspace_container.layout().addWidget(workspace_panel)
            else:  # 如果模块没有单独的工作区UI，显示一个提示
                placeholder = QLabel(f"'{module.display_name}' function results will be displayed here.")
                placeholder.setStyleSheet("color: #CCCCCC; font-size: 14px; padding: 20px;")
                self.workspace_container.layout().addWidget(placeholder)

        except Exception as e:
            error_label = QLabel(f"Failed to load UI: {str(e)}")
            error_label.setStyleSheet("color: red; font-size: 14px; padding: 20px;")
            self.settings_container.layout().addWidget(error_label)
            print(f"[ERROR] Failed to load UI for module {module.name}: {e}")

    def clear_layout(self, layout):
        """清空布局中的所有控件"""
        if layout is not None:
            while layout.count():
                child = layout.takeAt(0)
                if child.widget():
                    # Instead of deleteLater(), we'll set the widget to None
                    # This allows modules to detect when their UI has been removed
                    widget = child.widget()
                    # Notify any modules that might be holding references to this widget
                    if hasattr(widget, 'setParent'):
                        widget.setParent(None)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = PyQt6ModernApp()
    window.show()
    sys.exit(app.exec())