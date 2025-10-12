#!/usr/bin/env python3
"""
工作区面板
"""

from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QStackedWidget,
                             QFrame, QPushButton, QTextEdit, QSplitter, QScrollArea,
                             QGridLayout, QSizePolicy, QProgressBar, QCheckBox)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QPixmap, QPainter, QColor, QImage
from core.function_manager import FunctionManager
from core.base_module import BaseFunctionModule
from utils.image_utils import ImageUtils
from ui.theme import Spacing
from ui.welcome_screen import WelcomeScreen


class DuplicateGroupWidget(QFrame):
    """
    重复图片组控件
    """
    
    def __init__(self, group_id, files, confidence):
        super().__init__()
        self.group_id = group_id
        self.files = files
        self.confidence = confidence
        self.selected = False
        self.init_ui()
        
    def init_ui(self):
        """初始化UI"""
        # 设置卡片样式
        self.setStyleSheet("""
            QFrame {
                background-color: #1B1B1B;
                border: 1px solid rgba(255, 255, 255, 0.1); /* 边线变为1px带透明度 */
                border-radius: 5px;
                padding: 8px;
                margin: 30px; /* 增加外边距 */
            }
            QFrame:hover {
                background-color: #2D2D30;
            }
            QFrame:selected {
                background-color: #404040;
            }
        """)
        self.setFixedHeight(120)
        
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)  # 清除内部边距
        layout.setSpacing(Spacing.XL)  # 使用主题间距规范
        
        # 显示第一张图片
        if len(self.files) >= 1:
            first_img_container = self.create_image_container(self.files[0])
            layout.addWidget(first_img_container)
        
        # 显示第二张图片
        if len(self.files) >= 2:
            second_img_container = self.create_image_container(self.files[1])
            layout.addWidget(second_img_container)
        
        layout.addStretch()
        
    def create_image_container(self, file_path):
        """创建图片容器"""
        img_container = QLabel()
        img_container.setStyleSheet("background-color: transparent; border: none;")
        img_container.setFixedSize(80, 80)  # 设置固定大小为80x80像素
        
        # 加载缩略图
        try:
            thumbnail = ImageUtils.get_thumbnail(file_path, (80, 80))
            # 将PIL图像转换为QImage
            thumbnail = thumbnail.convert("RGBA")
            data = thumbnail.tobytes("raw", "RGBA")
            qimage = QImage(data, thumbnail.width, thumbnail.height, QImage.Format.Format_RGBA8888)
            pixmap = QPixmap.fromImage(qimage)
            img_container.setPixmap(pixmap)
        except Exception as e:
            # 如果加载失败，显示错误图标
            img_container.setText("🚫")
            img_container.setAlignment(Qt.AlignmentFlag.AlignCenter)
            
        img_container.setAlignment(Qt.AlignmentFlag.AlignCenter)
            
        return img_container
        
    def toggle_selection(self):
        """切换选择状态"""
        self.selected = not self.selected
        if self.selected:
            self.setProperty("selected", True)
        else:
            self.setProperty("selected", False)
        self.style().unpolish(self)
        self.style().polish(self)

    def mousePressEvent(self, event):
        """处理鼠标点击事件"""
        self.toggle_selection()

class DeduplicationWorkspace(QWidget):
    """
    图片去重工作区
    """
    
    def __init__(self, module):
        super().__init__()
        self.module = module
        self.duplicate_groups = []
        self.init_ui()
        self.connect_signals()
        
    def init_ui(self):
        """初始化UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(Spacing.SM, Spacing.SM, Spacing.SM, Spacing.SM)
        layout.setSpacing(Spacing.SM)
        
        # # 顶部操作栏
        # top_bar = QHBoxLayout()
        
        # title = QLabel("🔍 重复图片结果")
        # title.setStyleSheet("font-size: 16px; font-weight: bold; color: white;")
        # top_bar.addWidget(title)
        # top_bar.addStretch()
        
        # self.select_all_btn = QPushButton("全选")
        # self.select_all_btn.setStyleSheet("""
        #     QPushButton {
        #         background-color: #007bff;
        #         color: white;
        #         border: none;
        #         padding: 8px 16px;
        #         border-radius: 4px;
        #         font-weight: bold;
        #     }
        #     QPushButton:hover {
        #         background-color: #0069d9;
        #     }
        # """)
        self.select_all_btn.clicked.connect(self.select_all)
        top_bar.addWidget(self.select_all_btn)
        
        self.unselect_all_btn = QPushButton("取消全选")
        self.unselect_all_btn.setStyleSheet("""
            QPushButton {
                background-color: #6c757d;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #5a6268;
            }
        """)
        self.unselect_all_btn.clicked.connect(self.unselect_all)
        top_bar.addWidget(self.unselect_all_btn)
        
        self.delete_btn = QPushButton("🗑️ 删除选中")
        self.delete_btn.setStyleSheet("""
            QPushButton {
                background-color: #dc3545;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #c82333;
            }
        """)
        top_bar.addWidget(self.delete_btn)
        
        self.move_btn = QPushButton("📂 移动到...")
        self.move_btn.setStyleSheet("""
            QPushButton {
                background-color: #ffc107;
                color: black;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #e0a800;
            }
        """)
        top_bar.addWidget(self.move_btn)
        
        # 日志按钮
        self.log_btn = QPushButton("📋 日志")
        self.log_btn.setCheckable(True)
        self.log_btn.setStyleSheet("""
            QPushButton {
                background-color: #333337;
                color: white;
                border: 1px solid #454545;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #3f3f46;
            }
            QPushButton:checked {
                background-color: #0078d7;
            }
        """)
        self.log_btn.clicked.connect(self.toggle_log)
        top_bar.addWidget(self.log_btn)
        
        layout.addLayout(top_bar)
        
        # 进度条
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        self.progress_bar.setFormat("准备就绪")
        self.progress_bar.setStyleSheet("""
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
        """)
        layout.addWidget(self.progress_bar)
        
        # 状态标签
        self.status_label = QLabel("准备就绪")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.status_label.setStyleSheet("color: white;")
        layout.addWidget(self.status_label)
        
        # 创建分割器用于结果区域和日志区域
        self.splitter = QSplitter(Qt.Orientation.Vertical)
        layout.addWidget(self.splitter)
        
        # 重复项显示区域
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setStyleSheet("""
            QScrollArea {
                border: none;
                background-color: transparent;
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
        """)
        
        self.scroll_widget = QWidget()
        self.scroll_widget.setStyleSheet("background-color: #1e1e1e;")
        self.grid_layout = QGridLayout(self.scroll_widget)
        self.grid_layout.setSpacing(Spacing.SM)
        
        self.scroll_area.setWidget(self.scroll_widget)
        self.splitter.addWidget(self.scroll_area)
        
        # 日志区域（默认隐藏）
        self.log_area = QFrame()
        self.log_area.setStyleSheet("""
            QFrame {
                background-color: #2d2d30;
                border: 1px solid #3f3f46;
                border-radius: 6px;
            }
        """)
        self.log_area.setVisible(False)
        
        log_layout = QVBoxLayout(self.log_area)
        log_layout.setContentsMargins(Spacing.SM, Spacing.SM, Spacing.SM, Spacing.SM)
        
        log_title = QLabel("📋 处理日志")
        log_title.setStyleSheet("font-weight: bold; color: white;")
        log_layout.addWidget(log_title)
        
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setStyleSheet("""
            QTextEdit {
                background-color: #1e1e1e;
                color: white;
                border: 1px solid #3f3f46;
                border-radius: 4px;
            }
        """)
        log_layout.addWidget(self.log_text)
        
        self.splitter.addWidget(self.log_area)
        
        # 设置分割器比例
        self.splitter.setSizes([400, 100])
        
    def connect_signals(self):
        """连接信号"""
        if self.module:
            self.module.progress_updated.connect(self.update_progress)
            self.module.log_message.connect(self.add_log_message)
            self.module.execution_finished.connect(self.show_results)
        
    def update_progress(self, value: float, message: str):
        """更新进度"""
        self.progress_bar.setValue(int(value))
        self.progress_bar.setFormat(f"{message} ({int(value)}%)")
        self.status_label.setText(message)

    def add_log_message(self, message: str, level: str):
        """添加日志消息"""
        formatted_message = f"[{level.upper()}] {message}"
        self.log_text.append(formatted_message)
        
    def show_results(self, result_data: dict):
        """显示结果"""
        # 清除现有结果
        for i in reversed(range(self.grid_layout.count())):
            widget = self.grid_layout.itemAt(i).widget()
            if widget:
                widget.setParent(None)
        self.duplicate_groups.clear()
        
        # 显示新结果
        duplicates = result_data.get('duplicates', {})
        if duplicates:
            # 计算列数（最小1列，最大5列）
            width = self.scroll_area.viewport().width()
            columns = max(1, min(5, width // 200))  # 每列至少200像素宽
            
            group_items = list(duplicates.items())
            for group_idx, (primary_file, duplicate_files) in enumerate(group_items):
                all_files = [primary_file] + duplicate_files
                # 这里应该计算实际的置信度，现在使用默认值
                confidence = 0.95
                
                # 计算网格位置
                row = group_idx # columns
                col = group_idx % columns
                
                # 创建卡片
                group_widget = DuplicateGroupWidget(group_idx + 1, all_files, confidence)
                self.grid_layout.addWidget(group_widget, row, col)
                self.duplicate_groups.append(group_widget)
        else:
            # 显示没有找到重复项的消息
            no_result_label = QLabel("未找到重复图片")
            no_result_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            no_result_label.setStyleSheet("color: white; font-size: 14px;")
            self.grid_layout.addWidget(no_result_label)
            
    def resizeEvent(self, event):
        """处理窗口大小调整事件"""
        super().resizeEvent(event)
        self.update_grid_layout()
        
    def update_grid_layout(self):
        """更新网格布局"""
        if not self.duplicate_groups:
            return
            
        # 重新排列所有卡片
        # 计算列数（最小1列，最大5列）
        width = self.scroll_area.viewport().width()
        columns = max(1, min(5, width // 200))  # 每列至少200像素宽
        
        # 重新添加所有卡片到网格布局
        for i, group_widget in enumerate(self.duplicate_groups):
            # 先从布局中移除
            self.grid_layout.removeWidget(group_widget)
            
            # 计算新位置
            row = i # columns
            col = i % columns
            
            # 添加到新位置
            self.grid_layout.addWidget(group_widget, row, col)
        
    def select_all(self):
        """全选"""
        for group in self.duplicate_groups:
            if not group.is_selected():
                group.checkbox.setChecked(True)
        
    def unselect_all(self):
        """取消全选"""
        for group in self.duplicate_groups:
            if group.is_selected():
                group.checkbox.setChecked(False)
                    
    def toggle_log(self):
        """切换日志显示"""
        self.log_area.setVisible(self.log_btn.isChecked())


class WorkspacePanel(QWidget):
    """
    工作区面板
    """
    # 新增：欢迎屏幕图片加载完成信号
    welcome_image_loaded = pyqtSignal()

    def __init__(self, function_manager: FunctionManager):
        super().__init__()
        self.function_manager = function_manager
        self.stacked_widget = None
        self.module_workspaces = {}
        self.init_ui()

    def init_ui(self):
        """初始化UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        # 工作区
        self.stacked_widget = QStackedWidget()
        layout.addWidget(self.stacked_widget)

        # 添加欢迎屏幕作为默认显示
        welcome_widget = WelcomeScreen()
        self.welcome_screen = welcome_widget  # 保存引用以便连接信号

        # 连接欢迎屏幕的图片加载完成信号
        self.welcome_screen.image_loading_completed.connect(self.on_welcome_image_loaded)

        self.stacked_widget.addWidget(welcome_widget)
        
    def on_welcome_image_loaded(self):
        """欢迎屏幕图片加载完成"""
        print("WorkspacePanel收到欢迎屏幕图片加载完成信号")
        # 转发信号
        self.welcome_image_loaded.emit()

    def update_ui(self, module: BaseFunctionModule):
        """更新UI以显示指定模块的工作区"""
        # 检查是否已经为该模块创建工作区UI
        if module.name in self.module_workspaces:
            index = self.stacked_widget.indexOf(self.module_workspaces[module.name])
            self.stacked_widget.setCurrentIndex(index)
            # 更新模块引用（如果需要）
            if module.name == "deduplication":
                # 对于去重模块，我们让模块自己管理其工作区UI
                pass
            return
            
        # 为模块创建工作区UI
        workspace_ui = module.create_workspace_ui()
        if workspace_ui:
            # 添加到堆叠部件
            index = self.stacked_widget.addWidget(workspace_ui)
            self.module_workspaces[module.name] = workspace_ui
            self.stacked_widget.setCurrentIndex(index)
        else:
            # 如果模块没有工作区UI，显示默认消息
            default_widget = QWidget()
            default_layout = QVBoxLayout(default_widget)
            label = QLabel(f"模块 '{module.display_name}' 没有可用的工作区")
            label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            label.setStyleSheet("color: white;")
            default_layout.addWidget(label)
            
            index = self.stacked_widget.addWidget(default_widget)
            self.module_workspaces[module.name] = default_widget
            self.stacked_widget.setCurrentIndex(index)