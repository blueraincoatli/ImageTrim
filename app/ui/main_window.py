#!/usr/bin/env python3
"""
主窗口实现
"""

from PyQt6.QtWidgets import (QMainWindow, QWidget, QHBoxLayout, QVBoxLayout,
                             QSplitter, QFrame, QStatusBar, QLabel, QPushButton)
from PyQt6.QtCore import Qt, QPoint
from PyQt6.QtGui import QIcon, QCursor
from pathlib import Path
from core.function_manager import FunctionManager
from ui.function_panel import FunctionPanel
from ui.settings_panel import SettingsPanel
from ui.workspace_panel import WorkspacePanel
from ui.about_dialog import AboutDialog
from ui.theme import Theme, FontSize, Spacing
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

        # 用于窗口拖动的变量
        self.drag_position = QPoint()

        self.init_ui()
        self.register_modules()

    def init_ui(self):
        """初始化用户界面"""
        self.setWindowTitle("ImageTrim - 图片精简工具")
        self.setMinimumSize(1200, 700)

        # 设置窗口图标
        icon_path = Path(__file__).parent.parent / "resources" / "icons" / "imagetrim.ico"
        if icon_path.exists():
            self.setWindowIcon(QIcon(str(icon_path)))

        # 启用无边框窗口样式（保留阴影）
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, False)

        # 创建自定义标题栏
        self.create_title_bar()

        # 创建状态栏
        self.create_status_bar()

        # 创建主窗口部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # 创建主布局（垂直）
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # 添加标题栏
        main_layout.addWidget(self.title_bar)

        # 创建内容布局
        content_layout = QHBoxLayout()
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(0)

        # 创建分割器
        splitter = QSplitter(Qt.Orientation.Horizontal)
        content_layout.addWidget(splitter)
        
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

        # 将内容布局添加到主布局
        main_layout.addLayout(content_layout)
        
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

            # 更新状态栏
            self.status_message.setText(f"已切换到功能：{module.display_name}")

    def create_title_bar(self):
        """创建自定义标题栏"""
        self.title_bar = QFrame()
        self.title_bar.setObjectName("TitleBar")
        self.title_bar.setFixedHeight(32)
        self.title_bar.setStyleSheet(f"""
            #TitleBar {{
                background-color: {Theme.BG_CARD};
                border-bottom: 1px solid {Theme.BORDER_DARK};
            }}
        """)

        title_layout = QHBoxLayout(self.title_bar)
        title_layout.setContentsMargins(Spacing.SM, 0, Spacing.SM, 0)
        title_layout.setSpacing(Spacing.SM)

        # 应用图标和标题
        icon_path = Path(__file__).parent.parent / "resources" / "icons" / "imagetrim.ico"
        if icon_path.exists():
            icon_label = QLabel()
            icon = QIcon(str(icon_path))
            pixmap = icon.pixmap(16, 16)
            icon_label.setPixmap(pixmap)
            title_layout.addWidget(icon_label)

        title_label = QLabel("ImageTrim - 图片精简工具")
        title_label.setStyleSheet(f"""
            color: {Theme.TEXT_PRIMARY};
            font-size: {FontSize.BODY}pt;
            font-weight: normal;
        """)
        title_layout.addWidget(title_label)

        # 弹性空间
        title_layout.addStretch()

        # 窗口控制按钮
        # 最小化按钮
        min_btn = QPushButton("−")
        min_btn.setFixedSize(32, 26)
        min_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {Theme.BG_LIGHT};
                color: white;
                border: none;
                font-size: 18px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: {Theme.PRIMARY};
                color: white;
            }}
        """)
        min_btn.clicked.connect(self.showMinimized)
        title_layout.addWidget(min_btn)

        # 最大化/还原按钮
        self.max_btn = QPushButton("◱")  # 使用Unicode正方形字符
        self.max_btn.setFixedSize(32, 26)
        self.max_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {Theme.BG_LIGHT};
                color: white;
                border: none;
                font-size: 18px;
                font-weight: bold;
                font-family: Arial, sans-serif;
            }}
            QPushButton:hover {{
                background-color: {Theme.PRIMARY};
                color: white;
            }}
        """)
        self.max_btn.clicked.connect(self.toggle_maximize)
        title_layout.addWidget(self.max_btn)

        # 关闭按钮
        close_btn = QPushButton("×")
        close_btn.setFixedSize(32, 26)
        close_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {Theme.BG_LIGHT};
                color: white;
                border: none;
                font-size: 20px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: {Theme.ERROR};
                color: white;
            }}
        """)
        close_btn.clicked.connect(self.close)
        title_layout.addWidget(close_btn)

    def create_status_bar(self):
        """创建状态栏"""
        status_bar = self.statusBar()
        status_bar.setStyleSheet(f"""
            QStatusBar {{
                background-color: {Theme.BG_CARD};
                border-top: 1px solid {Theme.BORDER_DARK};
                color: {Theme.TEXT_SECONDARY};
                padding: {Spacing.SM}px;
            }}
        """)

        # 左侧状态消息
        self.status_message = QLabel("就绪")
        self.status_message.setStyleSheet(f"""
            color: {Theme.TEXT_SECONDARY};
            font-size: {FontSize.SMALL}pt;
        """)
        status_bar.addWidget(self.status_message)

        # 右侧关于信息（可点击）
        about_label = QLabel("小红书: 919722379 | © 2024 ImageTrim")
        about_label.setStyleSheet(f"""
            color: {Theme.TEXT_DISABLED};
            font-size: {FontSize.SMALL}pt;
            padding-right: {Spacing.SM}px;
        """)
        about_label.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        about_label.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        about_label.mousePressEvent = lambda e: self.show_about_dialog()
        status_bar.addPermanentWidget(about_label)

    def show_about_dialog(self):
        """显示关于对话框"""
        dialog = AboutDialog(self)
        dialog.exec()

    def toggle_maximize(self):
        """切换最大化/还原"""
        if self.isMaximized():
            self.showNormal()
            self.max_btn.setText("□")
        else:
            self.showMaximized()
            self.max_btn.setText("❐")

    def mousePressEvent(self, event):
        """鼠标按下事件 - 用于拖动窗口"""
        if event.button() == Qt.MouseButton.LeftButton:
            # 检查是否在标题栏区域
            if event.position().y() <= self.title_bar.height():
                self.drag_position = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
                event.accept()

    def mouseMoveEvent(self, event):
        """鼠标移动事件 - 拖动窗口"""
        if event.buttons() == Qt.MouseButton.LeftButton and not self.drag_position.isNull():
            # 如果窗口已最大化，先还原
            if self.isMaximized():
                self.showNormal()
                # 重新计算拖动位置
                self.drag_position = QPoint(int(self.width() / 2), int(self.title_bar.height() / 2))

            self.move(event.globalPosition().toPoint() - self.drag_position)
            event.accept()

    def mouseReleaseEvent(self, event):
        """鼠标释放事件"""
        self.drag_position = QPoint()

    def mouseDoubleClickEvent(self, event):
        """鼠标双击事件 - 最大化/还原"""
        if event.position().y() <= self.title_bar.height():
            self.toggle_maximize()