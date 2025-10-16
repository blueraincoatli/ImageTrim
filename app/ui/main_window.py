#!/usr/bin/env python3
"""
主窗口实现
"""

from PyQt6.QtWidgets import (QMainWindow, QWidget, QHBoxLayout, QVBoxLayout,
                             QSplitter, QFrame, QStatusBar, QLabel, QPushButton)
from PyQt6.QtCore import Qt, QPoint, QTimer
from PyQt6.QtGui import QIcon, QCursor, QPixmap
from pathlib import Path
import sys
import os
from app.core.function_manager import FunctionManager
from app.ui.function_panel import FunctionPanel
from app.ui.settings_panel import SettingsPanel
from app.ui.workspace_panel import WorkspacePanel
from app.ui.about_dialog import AboutDialog
from app.ui.startup_dialog import StartupDialog
from app.ui.theme import Theme, FontSize, Spacing
from app.modules.deduplication import DeduplicationModule
from app.modules.avif_converter import AVIFConverterModule


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
        self.startup_dialog = None

        # 用于窗口拖动的变量
        self.drag_position = QPoint()

        # 初始化时不显示窗口，等待图片加载完成
        self.setVisible(False)

        # 显示启动对话框
        self.show_startup_dialog()

        # 延迟初始化UI，给启动对话框显示时间
        QTimer.singleShot(1000, self.delayed_init)

    def init_ui(self):
        """初始化用户界面"""
        self.setWindowTitle("ImageTrim - 图片精简工具")
        self.setMinimumSize(1200, 700)

        # 设置窗口图标
        icon_path = self.get_resource_path("icons/imagetrim.ico")
        print(f"主窗口尝试加载图标: {icon_path}")

        if icon_path and Path(icon_path).exists():
            icon = QIcon(str(icon_path))
            if not icon.isNull():
                self.setWindowIcon(icon)
                print("主窗口图标加载成功")
            else:
                print("主窗口图标无效")
        else:
            print(f"主窗口图标文件不存在: {icon_path}")

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
        self.splitter = QSplitter(Qt.Orientation.Horizontal)
        content_layout.addWidget(self.splitter)
        
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
        
        self.splitter.addWidget(left_frame)
        
        # 创建右栏（工作区面板）
        self.workspace_panel = WorkspacePanel(self.function_manager)

        # 连接欢迎屏幕图片加载完成信号
        self.workspace_panel.welcome_image_loaded.connect(self.on_welcome_image_loaded)

        self.splitter.addWidget(self.workspace_panel)

        # 设置分割器比例将在窗口显示后进行

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
        """注册功能模块 - 懒加载版本"""
        # 使用模块构造函数注册，实现懒加载
        from app.modules.deduplication import DeduplicationModule
        from app.modules.avif_converter import AVIFConverterModule
        
        # 注册模块构造函数，而不是立即实例化
        self.function_manager.register_module_constructor("deduplication", DeduplicationModule, "图片去重")
        self.function_manager.register_module_constructor("avif_converter", AVIFConverterModule, "AVIF转换")
        
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
        icon_path = self.get_resource_path("icons/imagetrim.ico")
        print(f"标题栏尝试加载图标: {icon_path}")

        if icon_path and Path(icon_path).exists():
            icon_label = QLabel()
            icon = QIcon(str(icon_path))
            if not icon.isNull():
                pixmap = icon.pixmap(16, 16)
                if not pixmap.isNull():
                    icon_label.setPixmap(pixmap)
                    title_layout.addWidget(icon_label)
                    print("标题栏图标加载成功")
                else:
                    print("标题栏像素图无效")
            else:
                print("标题栏图标无效")
        else:
            print(f"标题栏图标文件不存在: {icon_path}")

        title_label = QLabel("ImageTrim - 图片精简工具")
        title_label.setStyleSheet(f"""
            color: {Theme.TEXT_PRIMARY};
            font-size: {FontSize.BODY}pt;
            font-weight: normal;
        """)
        title_layout.addWidget(title_label)

        # 弹性空间
        title_layout.addStretch()

        # 窗口控制按钮容器
        control_container = QWidget()
        control_container.setFixedSize(120, 32)
        control_layout = QHBoxLayout(control_container)
        control_layout.setContentsMargins(0, 0, 0, 0)
        control_layout.setSpacing(0)

        # 最小化按钮
        self.min_btn = QPushButton("")
        self.min_btn.setFixedSize(40, 32)
        self.min_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: transparent;
                color: {Theme.TEXT_PRIMARY};
                border: none;
                border-radius: 0;
                font-size: 16px;
                font-weight: normal;
            }}
            QPushButton:hover {{
                background-color: rgba(255, 255, 255, 0.1);
                color: {Theme.TEXT_PRIMARY};
            }}
            QPushButton:pressed {{
                background-color: rgba(255, 255, 255, 0.15);
                color: {Theme.TEXT_PRIMARY};
            }}
        """)
        self.min_btn.setToolTip("最小化")
        self.min_btn.clicked.connect(self.showMinimized)
        control_layout.addWidget(self.min_btn)

        # 最大化/还原按钮
        self.max_btn = QPushButton("")
        self.max_btn.setFixedSize(40, 32)
        self.max_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: transparent;
                color: {Theme.TEXT_PRIMARY};
                border: none;
                border-radius: 0;
                font-size: 16px;
                font-weight: normal;
            }}
            QPushButton:hover {{
                background-color: rgba(255, 255, 255, 0.1);
                color: {Theme.TEXT_PRIMARY};
            }}
            QPushButton:pressed {{
                background-color: rgba(255, 255, 255, 0.15);
                color: {Theme.TEXT_PRIMARY};
            }}
        """)
        self.max_btn.setToolTip("最大化")
        self.max_btn.clicked.connect(self.toggle_maximize)
        control_layout.addWidget(self.max_btn)

        # 关闭按钮
        self.close_btn = QPushButton("")
        self.close_btn.setFixedSize(40, 32)
        self.close_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: transparent;
                color: {Theme.TEXT_PRIMARY};
                border: none;
                border-radius: 0;
                font-size: 16px;
                font-weight: normal;
            }}
            QPushButton:hover {{
                background-color: {Theme.ERROR};
                color: white;
            }}
            QPushButton:pressed {{
                background-color: #E81123;
                color: white;
            }}
        """)
        self.close_btn.setToolTip("关闭")
        self.close_btn.clicked.connect(self.close)
        control_layout.addWidget(self.close_btn)

        # 设置按钮图标
        self.update_window_control_icons()

        title_layout.addWidget(control_container)

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

        # 右侧关于信息（可点击）- 包含图标
        about_container = QWidget()
        about_layout = QHBoxLayout(about_container)
        about_layout.setContentsMargins(0, 0, 0, 0)
        about_layout.setSpacing(Spacing.XS)

        # 添加小图标
        icon_label = QLabel()
        icon_path = self.get_resource_path("icons/imagetrim.ico")
        if icon_path and os.path.exists(icon_path):
            pixmap = QPixmap(icon_path)
            if not pixmap.isNull():
                # 缩放到16x16适合状态栏
                scaled_pixmap = pixmap.scaled(16, 16, Qt.AspectRatioMode.KeepAspectRatio,
                                              Qt.TransformationMode.SmoothTransformation)
                icon_label.setPixmap(scaled_pixmap)
            else:
                icon_label.setText("📋")
                icon_label.setStyleSheet(f"font-size: 12px;")
        else:
            icon_label.setText("📋")
            icon_label.setStyleSheet(f"font-size: 12px;")

        # 版权文本
        about_label = QLabel("小红书: 919722379 | © 2025 ImageTrim")
        about_label.setStyleSheet(f"""
            color: {Theme.TEXT_DISABLED};
            font-size: {FontSize.SMALL}pt;
            padding-right: {Spacing.SM}px;
        """)

        # 设置点击事件
        about_container.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        about_container.mousePressEvent = lambda e: self.show_about_dialog()

        about_layout.addWidget(icon_label)
        about_layout.addWidget(about_label)
        status_bar.addPermanentWidget(about_container)

    def show_about_dialog(self):
        """显示关于对话框"""
        dialog = AboutDialog(self)
        dialog.exec()

    def show_startup_dialog(self):
        """显示启动对话框"""
        self.startup_dialog = StartupDialog(self)
        self.startup_dialog.timeout.connect(self.on_startup_timeout)
        self.startup_dialog.show()  # 使用show()显示非模态对话框

    def on_startup_timeout(self):
        """启动超时处理"""
        print("启动超时，强制显示主窗口")
        if self.startup_dialog:
            self.startup_dialog.close()
        # 即使超时也要显示主窗口
        if not self.isVisible():
            self.show()
            self.center_window()

    def delayed_init(self):
        """延迟初始化UI"""
        try:
            self.init_ui()
            self.register_modules()
        except Exception as e:
            print(f"UI初始化失败: {e}")
            if self.startup_dialog:
                self.startup_dialog.close()
            # 即使初始化失败也要显示窗口
            self.show()
            self.center_window()

    def center_window(self):
        """居中显示窗口"""
        screen = self.screen().availableGeometry()
        x = (screen.width() - self.width()) // 2
        y = (screen.height() - self.height()) // 2
        self.move(x, y)

    def on_welcome_image_loaded(self):
        """欢迎屏幕图片加载完成，显示窗口"""
        print("主窗口收到欢迎屏幕图片加载完成信号，准备显示窗口")

        # 关闭启动对话框
        if self.startup_dialog and self.startup_dialog.isVisible():
            self.startup_dialog.set_complete()

        # 显示窗口
        self.show()

        # 确保窗口在屏幕中央
        self.center_window()

        print(f"窗口显示完成，最终大小: {self.width()}x{self.height()}")
        print("开始设置分割器比例...")

        # 设置正确的分割器比例（30/70）
        self.set_splitter_ratio()

        print("窗口已显示并居中，分割器比例已设置")

    def update_window_control_icons(self):
        """更新窗口控制按钮图标"""
        # 使用SVG图标样式的Unicode字符
        self.min_btn.setText("−")
        if self.isMaximized():
            self.max_btn.setText("❐")
            self.max_btn.setToolTip("还原")
        else:
            self.max_btn.setText("□")
            self.max_btn.setToolTip("最大化")
        self.close_btn.setText("×")

    def toggle_maximize(self):
        """切换最大化/还原"""
        if self.isMaximized():
            self.showNormal()
            self.max_btn.setText("□")
            self.max_btn.setToolTip("最大化")
        else:
            self.showMaximized()
            self.max_btn.setText("❐")
            self.max_btn.setToolTip("还原")

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

    def set_splitter_ratio(self):
        """设置分割器的30/70比例"""
        if hasattr(self, 'splitter'):
            # 设置30/70比例
            total_width = self.width()
            left_size = int(total_width * 0.3)
            right_size = int(total_width * 0.7)

            # 强制设置左侧面板的最小宽度，确保能够占据30%空间
            if hasattr(self, 'function_panel'):
                self.function_panel.setMinimumWidth(left_size)

            # 设置分割器比例，并禁止面板折叠
            self.splitter.setSizes([left_size, right_size])
            self.splitter.setCollapsible(0, False)  # 禁止左侧面板折叠
            self.splitter.setCollapsible(1, False)  # 禁止右侧面板折叠

            print(f"分割器比例已设置为30/70: {left_size}/{right_size}")
        else:
            print("分割器尚未初始化")

    def resizeEvent(self, event):
        """窗口大小改变时重新设置分割器比例"""
        old_size = event.oldSize()
        new_size = event.size()
        print(f"窗口大小改变: {old_size.width()}x{old_size.height()} -> {new_size.width()}x{new_size.height()}")

        super().resizeEvent(event)
        # 延迟重新设置比例，避免在初始化时干扰
        if hasattr(self, 'splitter') and self.isVisible():
            print("触发分割器比例重新设置...")
            # 使用单次定时器延迟执行，避免频繁调整
            QTimer.singleShot(100, self.set_splitter_ratio)

    def get_resource_path(self, relative_path):
        """获取资源文件的绝对路径，支持 PyInstaller 和 Nuitka 打包环境"""
        from app.utils.resource_path import get_resource_path as get_res_path
        return get_res_path(relative_path)