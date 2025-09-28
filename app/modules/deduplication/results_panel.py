#!/usr/bin/env python3
"""
图片去重结果面板 - 完全重新实现，基于备份目录中的代码
"""

import os
import shutil
from typing import Dict, List, Tuple
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
                             QTextEdit, QScrollArea, QGridLayout, QProgressBar, 
                             QFrame, QCheckBox, QSplitter, QFileDialog, QMessageBox,
                             QApplication, QDialog, QGraphicsView, QGraphicsScene, QGraphicsPixmapItem,
                             QSlider)
from PyQt6.QtCore import Qt, pyqtSignal, QRectF
from PyQt6.QtGui import QPixmap, QImage, QKeySequence, QShortcut, QPainter, QColor, QPen
from utils.image_utils import ImageUtils
from utils.ui_helpers import UIHelpers


class ImageViewerDialog(QDialog):
    """图片查看器对话框"""
    
    def __init__(self, image_path: str, parent=None):
        super().__init__(parent)
        self.image_path = image_path
        self.zoom_factor = 1.0
        self.init_ui()
        self.load_image()
        
    def init_ui(self):
        """初始化UI"""
        self.setWindowTitle(f"图片预览 - {os.path.basename(self.image_path)}")
        self.setWindowState(Qt.WindowState.WindowMaximized)
        self.setStyleSheet("background-color: #1e1e1e;")
        
        # 创建主布局
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # 创建图形视图
        self.graphics_view = QGraphicsView()
        self.graphics_view.setStyleSheet("border: none; background-color: #1e1e1e;")
        self.graphics_view.setRenderHint(QPainter.RenderHint.Antialiasing)
        self.graphics_view.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)
        self.graphics_view.setDragMode(QGraphicsView.DragMode.ScrollHandDrag)
        
        # 创建场景
        self.scene = QGraphicsScene()
        self.graphics_view.setScene(self.scene)
        
        layout.addWidget(self.graphics_view)
        
        # 添加快捷键
        self.add_shortcuts()
        
        # 状态标签
        self.status_label = QLabel()
        self.status_label.setStyleSheet("color: white; background-color: rgba(0, 0, 0, 180); padding: 5px;")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.status_label)
        
    def add_shortcuts(self):
        """添加快捷键"""
        # ESC关闭
        esc_shortcut = QShortcut(QKeySequence("Escape"), self)
        esc_shortcut.activated.connect(self.close)
        
        # Ctrl+Q关闭
        quit_shortcut = QShortcut(QKeySequence("Ctrl+Q"), self)
        quit_shortcut.activated.connect(self.close)
        
        # 空格键居中
        space_shortcut = QShortcut(QKeySequence("Space"), self)
        space_shortcut.activated.connect(self.center_image)
        
        # +放大
        plus_shortcut = QShortcut(QKeySequence("+"), self)
        plus_shortcut.activated.connect(self.zoom_in)
        
        # -缩小
        minus_shortcut = QShortcut(QKeySequence("-"), self)
        minus_shortcut.activated.connect(self.zoom_out)
        
        # 100%大小
        one_shortcut = QShortcut(QKeySequence("1"), self)
        one_shortcut.activated.connect(self.zoom_100)
        
        # 适合窗口大小
        f_shortcut = QShortcut(QKeySequence("F"), self)
        f_shortcut.activated.connect(self.fit_to_window)
        
    def load_image(self):
        """加载图片"""
        try:
            # 使用PIL加载图片以支持更多格式
            from PIL import Image
            with Image.open(self.image_path) as img:
                # 转换为RGB（处理RGBA等格式）
                if img.mode != 'RGB':
                    img = img.convert('RGB')
                
                # 转换为QImage
                data = img.tobytes("raw", "RGB")
                qimage = QImage(data, img.width, img.height, QImage.Format.Format_RGB888)
                pixmap = QPixmap.fromImage(qimage)
                
            # 清除场景
            self.scene.clear()
            
            # 添加图片到场景
            self.pixmap_item = QGraphicsPixmapItem(pixmap)
            self.scene.addItem(self.pixmap_item)
            
            # 设置视图为100%大小
            self.zoom_100()
            
            # 更新状态
            self.update_status(img.width, img.height, os.path.getsize(self.image_path))
            
        except Exception as e:
            error_msg = f"无法加载图片: {str(e)}"
            self.status_label.setText(error_msg)
            print(error_msg)
            
    def update_status(self, width: int, height: int, size: int):
        """更新状态信息"""
        size_str = self.format_file_size(size)
        self.status_label.setText(f"{width}×{height} | {size_str} | 缩放: {self.zoom_factor*100:.0f}% (空格居中, +/-缩放, F适合窗口, ESC退出)")
        
    def format_file_size(self, size: int) -> str:
        """格式化文件大小"""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size < 1024.0:
                return f"{size:.1f} {unit}"
            size /= 1024.0
        return f"{size:.1f} TB"
        
    def zoom_in(self):
        """放大"""
        self.zoom_factor *= 1.2
        self.apply_zoom()
        
    def zoom_out(self):
        """缩小"""
        self.zoom_factor /= 1.2
        self.apply_zoom()
        
    def zoom_100(self):
        """100%大小"""
        self.zoom_factor = 1.0
        self.apply_zoom()
        
    def fit_to_window(self):
        """适合窗口大小"""
        if hasattr(self, 'pixmap_item') and self.pixmap_item.pixmap().width() > 0:
            view_rect = self.graphics_view.viewport().rect()
            pixmap_rect = self.pixmap_item.boundingRect()
            
            # 计算缩放因子
            scale_x = view_rect.width() / pixmap_rect.width()
            scale_y = view_rect.height() / pixmap_rect.height()
            self.zoom_factor = min(scale_x, scale_y)
            
            self.apply_zoom()
            
    def apply_zoom(self):
        """应用缩放"""
        if hasattr(self, 'pixmap_item'):
            # 保存当前中心点
            center = self.graphics_view.mapToScene(self.graphics_view.viewport().rect().center())
            
            # 应用缩放
            self.graphics_view.resetTransform()
            self.graphics_view.scale(self.zoom_factor, self.zoom_factor)
            
            # 恢复中心点
            self.graphics_view.centerOn(center)
            
            # 更新状态
            if os.path.exists(self.image_path):
                from PIL import Image
                with Image.open(self.image_path) as img:
                    self.update_status(img.width, img.height, os.path.getsize(self.image_path))
                    
    def center_image(self):
        """居中图片"""
        if hasattr(self, 'pixmap_item'):
            self.graphics_view.centerOn(self.pixmap_item)


class DuplicateImageWidget(QFrame):
    """
    重复图片控件 - 支持双击预览
    """
    
    # 定义信号
    selection_changed = pyqtSignal(list, bool)  # files, is_selected
    image_double_clicked = pyqtSignal(str)  # file_path
    
    def __init__(self, file_path: str, thumbnail_size: int = 120, parent=None):
        super().__init__(parent)
        self.file_path = file_path
        self.thumbnail_size = thumbnail_size
        self.is_selected = False
        self.init_ui()
        
    def init_ui(self):
        """初始化UI"""
        # 设置样式（透明背景）
        # 使用3:2比例 (width: int(self.thumbnail_size * 1.5), height: self.thumbnail_size)
        self.setFixedSize(int(self.thumbnail_size * 1.5), self.thumbnail_size)
        self.setStyleSheet("""
            QFrame {
                background-color: transparent;
                border: none;
                border-radius: 0px;
            }
        """)
        
        # 主布局（居中对齐）
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # 创建图片标签
        self.image_label = self.create_image_label()
        layout.addWidget(self.image_label)
        
    def create_image_label(self):
        """创建图片标签，保持原图比例，长边为缩略图大小"""
        # 创建容器标签（居中对齐）
        container = QLabel()
        container.setAlignment(Qt.AlignmentFlag.AlignCenter)
        container.setStyleSheet("background-color: transparent; border: none;")
        # 使用3:2比例 (width: int(self.thumbnail_size * 1.5), height: self.thumbnail_size)
        container.setFixedSize(int(self.thumbnail_size * 1.5), self.thumbnail_size)
        
        # 加载缩略图并保持原图比例
        try:
            # 获取原始图片尺寸
            from PIL import Image
            with Image.open(self.file_path) as img:
                original_width, original_height = img.size
                
            # 计算缩放比例，确保图片适应3:2容器
            container_aspect_ratio = 1.5  # 3:2
            image_aspect_ratio = original_width / original_height
            
            if image_aspect_ratio > container_aspect_ratio:
                # 图片更宽，以宽度为准
                new_width = int(self.thumbnail_size * 1.5)
                new_height = int(new_width / image_aspect_ratio)
            else:
                # 图片更高，以高度为准
                new_height = self.thumbnail_size
                new_width = int(new_height * image_aspect_ratio)
                
            # 限制图片最大尺寸
            if new_width > int(self.thumbnail_size * 1.5):
                new_width = int(self.thumbnail_size * 1.5)
            if new_height > self.thumbnail_size:
                new_height = self.thumbnail_size
                
            container.setFixedSize(new_width, new_height)
            
            # 获取缩略图
            thumbnail = ImageUtils.get_thumbnail(self.file_path, (new_width, new_height))
            # 将PIL图像转换为QImage
            thumbnail = thumbnail.convert("RGBA")
            data = thumbnail.tobytes("raw", "RGBA")
            qimage = QImage(data, thumbnail.width, thumbnail.height, QImage.Format.Format_RGBA8888)
            pixmap = QPixmap.fromImage(qimage)
            container.setPixmap(pixmap)
        except Exception as e:
            # 如果加载失败，显示错误图标
            container.setText("🚫")
            container.setFixedSize(int(self.thumbnail_size * 1.5), self.thumbnail_size)
            container.setStyleSheet("color: #dc3545; font-size: 24px; background-color: transparent; border: none;")
            
        return container
        
    def mousePressEvent(self, event):
        """处理鼠标点击事件"""
        super().mousePressEvent(event)
        self.set_selected(not self.is_selected)
        
    def mouseDoubleClickEvent(self, event):
        """处理鼠标双击事件"""
        super().mouseDoubleClickEvent(event)
        self.image_double_clicked.emit(self.file_path)
        
    def set_selected(self, selected):
        """设置选中状态"""
        self.is_selected = selected
        
        # 只更新状态，不改变视觉效果
        # 发出信号
        self.selection_changed.emit([self.file_path], selected)


class DuplicateGroupWidget(QFrame):
    """
    重复图片组控件
    """
    
    # 定义信号
    selection_changed = pyqtSignal(list, bool)  # files, is_selected
    image_double_clicked = pyqtSignal(str)  # file_path
    
    def __init__(self, group_id: int, files: List[str], confidence: float, parent=None):
        super().__init__(parent)
        self.group_id = group_id
        self.files = files
        self.confidence = confidence
        self.is_selected = False
        self.image_widgets = []  # 存储图片控件
        self.init_ui()
        
    def update_thumbnails(self, thumbnail_size: int):
        """更新缩略图大小"""
        # 更新缩略图大小属性
        self.thumbnail_size = thumbnail_size
        
        # 清除现有的图片控件
        for widget in self.image_widgets:
            widget.setParent(None)
        self.image_widgets.clear()
        
        # 找到图片容器布局并清除其中的所有控件
        layout = self.layout()
        if layout is not None and layout.count() > 0:
            # 获取图片容器（最后一个添加的widget）
            images_container_item = layout.itemAt(layout.count() - 1)
            if images_container_item and images_container_item.widget():
                images_container = images_container_item.widget()
                images_layout = images_container.layout()
                if images_layout:
                    # 清除现有布局中的所有控件
                    for i in reversed(range(images_layout.count())):
                        item = images_layout.itemAt(i)
                        if item and item.widget():
                            item.widget().setParent(None)
                    
                    # 重新创建图片控件
                    for file_path in self.files:
                        image_widget = DuplicateImageWidget(file_path, self.thumbnail_size)
                        image_widget.selection_changed.connect(self.on_image_selection_changed)
                        image_widget.image_double_clicked.connect(self.image_double_clicked.emit)
                        images_layout.addWidget(image_widget)
                        self.image_widgets.append(image_widget)
        
    def init_ui(self):
        """初始化UI"""
        # 设置卡片样式（减小内边距）
        self.setStyleSheet("""
            QFrame {
                background-color: #1B1B1B;
                border: 1px solid #353535;
                border-radius: 8px;
                padding: 5px;
            }
            QFrame:hover {
                background-color: #252525;
            }
        """)
        
        # 主布局
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(5)
        
        # 直接创建卡片图片区域（移除了头部信息）
        self.create_card_images(layout)
        
    def create_card_header(self, parent_layout):
        """创建卡片头部（已移除）"""
        # 已根据要求移除卡片头部信息
        pass
        
    def create_card_images(self, parent_layout):
        """创建卡片图片区域"""
        # 清除现有的图片容器（如果存在）
        for i in reversed(range(parent_layout.count())):
            item = parent_layout.itemAt(i)
            if item and item.widget():
                widget = item.widget()
                if isinstance(widget, QFrame):
                    layout = widget.layout()
                    if layout and isinstance(layout, QHBoxLayout):
                        # 清除布局中的所有控件
                        for j in reversed(range(layout.count())):
                            layout_item = layout.itemAt(j)
                            if layout_item and layout_item.widget():
                                layout_item.widget().setParent(None)
                        # 删除布局
                        widget.setLayout(None)
                        # 删除容器
                        widget.setParent(None)
        
        # 创建新的图片容器
        images_container = QFrame()
        images_container.setStyleSheet("background-color: transparent; border: none;")
        images_layout = QHBoxLayout(images_container)
        images_layout.setContentsMargins(2, 2, 2, 2)
        images_layout.setSpacing(5)
        images_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # 创建图片控件
        self.image_widgets = []
        for file_path in self.files:
            image_widget = DuplicateImageWidget(file_path, self.thumbnail_size if hasattr(self, "thumbnail_size") else 120)
            image_widget.selection_changed.connect(self.on_image_selection_changed)
            image_widget.image_double_clicked.connect(self.image_double_clicked.emit)
            images_layout.addWidget(image_widget)
            self.image_widgets.append(image_widget)
            
        images_layout.addStretch()
        parent_layout.addWidget(images_container)
        
    def on_checkbox_changed(self, state):
        """处理复选框变化"""
        is_checked = state == Qt.CheckState.Checked.value
        self.set_selected(is_checked)
        
    def on_image_selection_changed(self, files, is_selected):
        """处理图片选择变化"""
        # 发出信号
        self.selection_changed.emit(self.files, is_selected)
        
    def set_selected(self, selected):
        """设置选中状态"""
        self.is_selected = selected
            
        # 更新样式 - 实现上浮效果和发光效果
        if selected:
            self.setProperty("selected", True)
            # 上浮效果：改变背景色，向上移动3px
            # 使用较宽的浅色边框模拟发光效果
            self.setStyleSheet("""
                QFrame {
                    background-color: #2D2D30;
                    border: 3px solid rgba(173, 216, 230, 0.7);  /* 浅蓝色边框模拟发光 */
                    border-radius: 8px;
                    padding: 5px;
                }
            """)
            # 向上移动3px实现上浮效果
            self.move(self.x(), self.y() - 3)
        else:
            self.setProperty("selected", False)
            # 恢复原来的样式
            self.setStyleSheet("""
                QFrame {
                    background-color: #1B1B1B;
                    border: 1px solid #353535;
                    border-radius: 8px;
                    padding: 5px;
                }
            """)
            # 恢复原来的位置
            self.move(self.x(), self.y() + 3)
        self.style().unpolish(self)
        self.style().polish(self)
        
        # 更新所有图片控件的选中状态（但不改变它们的视觉效果）
        for widget in self.image_widgets:
            widget.is_selected = selected
        
        # 发出信号
        self.selection_changed.emit(self.files, selected)


class DeduplicationResultsPanel(QWidget):
    """
    图片去重结果面板
    """
    
    def __init__(self, module):
        super().__init__()
        self.module = module
        self.duplicate_groups = []  # 存储所有重复组控件
        self.selected_files = set()  # 存储选中的文件
        self.grid_size = 5  # 网格大小等级 (1-10)
        self.thumbnail_size = 120  # 缩略图大小
        self.init_ui()
        self.connect_signals()
        
    def init_ui(self):
        """初始化UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)
        
        # 创建分割器用于结果区域和日志区域
        self.splitter = QSplitter(Qt.Orientation.Vertical)
        layout.addWidget(self.splitter)
        
        # 顶部操作栏
        top_bar = QWidget()
        top_layout = QHBoxLayout(top_bar)
        top_layout.setContentsMargins(0, 0, 0, 0)
        
        title = QLabel("🔍 重复图片结果")
        title.setStyleSheet("font-size: 16px; font-weight: bold; color: white;")
        top_layout.addWidget(title)
        top_layout.addStretch()
        
        # 全选/取消全选按钮
        self.select_all_btn = QPushButton("全选")
        self.select_all_btn.setStyleSheet("""
            QPushButton {
                background-color: #007bff;
                color: white;
                border: none;
                padding: 6px 12px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #0069d9;
            }
        """)
        self.select_all_btn.clicked.connect(self.select_all)
        top_layout.addWidget(self.select_all_btn)
        
        self.unselect_all_btn = QPushButton("取消全选")
        self.unselect_all_btn.setStyleSheet("""
            QPushButton {
                background-color: #6c757d;
                color: white;
                border: none;
                padding: 6px 12px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #5a6268;
            }
        """)
        self.unselect_all_btn.clicked.connect(self.unselect_all)
        top_layout.addWidget(self.unselect_all_btn)
        
        # 选中计数标签
        self.selection_count_label = QLabel("选中: 0")
        self.selection_count_label.setStyleSheet("color: white; margin: 0 10px;")
        top_layout.addWidget(self.selection_count_label)
        
        # 操作按钮
        self.delete_btn = QPushButton("🗑️ 删除选中")
        self.delete_btn.setStyleSheet("""
            QPushButton {
                background-color: #dc3545;
                color: white;
                border: none;
                padding: 6px 12px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #c82333;
            }
            QPushButton:disabled {
                background-color: #6c757d;
            }
        """)
        self.delete_btn.clicked.connect(self.delete_selected)
        self.delete_btn.setEnabled(False)
        top_layout.addWidget(self.delete_btn)
        
        self.move_btn = QPushButton("📂 移动到...")
        self.move_btn.setStyleSheet("""
            QPushButton {
                background-color: #ffc107;
                color: black;
                border: none;
                padding: 6px 12px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #e0a800;
            }
            QPushButton:disabled {
                background-color: #6c757d;
            }
        """)
        self.move_btn.clicked.connect(self.move_selected)
        self.move_btn.setEnabled(False)
        top_layout.addWidget(self.move_btn)
        
        # 日志按钮
        self.log_btn = QPushButton("📋 日志")
        self.log_btn.setCheckable(True)
        self.log_btn.setStyleSheet("""
            QPushButton {
                background-color: #333337;
                color: white;
                border: 1px solid #454545;
                padding: 6px 12px;
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
        top_layout.addWidget(self.log_btn)
        
        # 网格大小控制
        self.grid_size_label = QLabel("网格大小:")
        self.grid_size_label.setStyleSheet("color: white; margin-left: 10px;")
        top_layout.addWidget(self.grid_size_label)
        
        self.grid_size_slider = QSlider(Qt.Orientation.Horizontal)
        self.grid_size_slider.setRange(1, 8)  # 1-8列
        self.grid_size_slider.setValue(5)  # 默认中间值
        self.grid_size_slider.setFixedWidth(100)
        self.grid_size_slider.setStyleSheet("""
            QSlider::groove:horizontal {
                border: 1px solid #999999;
                height: 8px;
                background: #2B2B2B;
                margin: 2px 0;
            }
            QSlider::handle:horizontal {
                background: #FF8C00;
                border: 1px solid #5c5c5c;
                width: 18px;
                margin: -2px 0;
                border-radius: 3px;
            }
            QSlider::sub-page:horizontal {
                background: #FF8C00;
            }
        """)
        self.grid_size_slider.valueChanged.connect(self.on_grid_size_changed)
        top_layout.addWidget(self.grid_size_slider)
        
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
        
        # 状态标签
        self.status_label = QLabel("准备就绪")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.status_label.setStyleSheet("color: white;")
        
        # 重复项显示区域
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.scroll_area.setStyleSheet("""
            QScrollArea {
                border: 1px solid #353535;
                border-radius: 4px;
                background-color: #1e1e1e;
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
        self.grid_layout.setSpacing(10)  # 设置网格间距
        self.grid_layout.setContentsMargins(10, 10, 10, 10)  # 设置网格边距
        
        self.scroll_area.setWidget(self.scroll_widget)
        
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
        log_layout.setContentsMargins(10, 10, 10, 10)
        
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
        
        # 创建顶部区域容器
        top_container = QWidget()
        top_container_layout = QVBoxLayout(top_container)
        top_container_layout.setContentsMargins(0, 0, 0, 0)
        top_container_layout.setSpacing(5)
        top_container_layout.addWidget(top_bar)
        top_container_layout.addWidget(self.progress_bar)
        top_container_layout.addWidget(self.status_label)
        top_container_layout.addWidget(self.scroll_area)
        
        self.splitter.addWidget(top_container)
        self.splitter.addWidget(self.log_area)
        
        # 设置分割器比例
        self.splitter.setSizes([700, 200])
        
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
                # 断开信号连接
                if hasattr(widget, 'selection_changed'):
                    try:
                        widget.selection_changed.disconnect()
                    except:
                        pass
                if hasattr(widget, 'image_double_clicked'):
                    try:
                        widget.image_double_clicked.disconnect()
                    except:
                        pass
        self.duplicate_groups.clear()
        self.selected_files.clear()
        self.update_selection_count()

        # 显示新结果
        duplicates = result_data.get('duplicates', {})
        if duplicates:
            # 计算列数（根据窗口宽度动态计算，确保不会溢出）
            width = self.scroll_area.viewport().width()
            # 计算实际需要的卡片宽度（更精确的计算）
            card_content_width = int(self.thumbnail_size * 1.5)  # 3:2比例的图片宽度
            card_margins = 20  # 卡片内边距和边框
            spacing = self.grid_layout.spacing()  # 网格间距
            card_total_width = card_content_width + card_margins + spacing
            columns = max(1, int(width // card_total_width))  # 向下取整
            
            group_items = list(duplicates.items())
            for group_idx, (primary_file, duplicate_files) in enumerate(group_items):
                all_files = [primary_file] + duplicate_files
                # 计算实际的置信度（这里简化处理，实际应该从算法中获取）
                confidence = 0.95
                
                # 计算网格位置
                row = group_idx // columns
                col = group_idx % columns
                
                # 创建卡片
                group_widget = DuplicateGroupWidget(group_idx + 1, all_files, confidence)
                group_widget.thumbnail_size = self.thumbnail_size
                group_widget.selection_changed.connect(self.on_group_selection_changed)
                group_widget.image_double_clicked.connect(self.on_image_double_clicked)
                self.grid_layout.addWidget(group_widget, row, col, Qt.AlignmentFlag.AlignCenter)
                self.duplicate_groups.append(group_widget)
                
            # 设置列的拉伸因子，使列宽度相等
            for i in range(columns):
                self.grid_layout.setColumnStretch(i, 1)
                
            # 设置行的拉伸因子，使行高度相等
            rows = (len(group_items) + columns - 1) // columns
            for i in range(rows):
                self.grid_layout.setRowStretch(i, 1)
                
            self.status_label.setText(f"找到 {len(group_items)} 组重复图片")
        else:
            # 显示没有找到重复项的消息
            no_result_label = QLabel("未找到重复图片")
            no_result_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            no_result_label.setStyleSheet("color: white; font-size: 16px; font-weight: bold; padding: 50px;")
            self.grid_layout.addWidget(no_result_label)
            self.status_label.setText("未找到重复图片")
            
    def on_group_selection_changed(self, files, is_selected):
        """处理组选择变化"""
        if is_selected:
            self.selected_files.update(files)
        else:
            self.selected_files.difference_update(files)
            
        # 更新UI
        self.update_selection_count()
        self.delete_btn.setEnabled(len(self.selected_files) > 0)
        self.move_btn.setEnabled(len(self.selected_files) > 0)
        
    def on_image_double_clicked(self, file_path):
        """处理图片双击事件"""
        # 创建并显示图片查看器对话框
        viewer = ImageViewerDialog(file_path, self)
        viewer.exec()
        
    def update_selection_count(self):
        """更新选中计数"""
        count = len(self.selected_files)
        self.selection_count_label.setText(f"选中: {count}")
        
    def select_all(self):
        """全选"""
        for group in self.duplicate_groups:
            group.set_selected(True)
            
        # 收集所有文件
        all_files = set()
        for group in self.duplicate_groups:
            all_files.update(group.files)
            
        self.selected_files = all_files
        self.update_selection_count()
        self.delete_btn.setEnabled(len(self.selected_files) > 0)
        self.move_btn.setEnabled(len(self.selected_files) > 0)
        
    def unselect_all(self):
        """取消全选"""
        for group in self.duplicate_groups:
            group.set_selected(False)
            
        self.selected_files.clear()
        self.update_selection_count()
        self.delete_btn.setEnabled(False)
        self.move_btn.setEnabled(False)
        
    def delete_selected(self):
        """删除选中文件"""
        if not self.selected_files:
            return
            
        # 确认对话框
        reply = QMessageBox.question(
            self, 
            "确认删除", 
            f"确定要删除选中的 {len(self.selected_files)} 个文件吗？此操作不可撤销！",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            success_count = 0
            failed_files = []
            
            # 删除文件
            for file_path in self.selected_files:
                try:
                    if os.path.exists(file_path):
                        os.remove(file_path)
                        success_count += 1
                        self.module.log_message.emit(f"已删除: {file_path}", "info")
                    else:
                        failed_files.append(file_path)
                        self.module.log_message.emit(f"文件不存在: {file_path}", "warning")
                except Exception as e:
                    failed_files.append(file_path)
                    self.module.log_message.emit(f"删除失败 {file_path}: {str(e)}", "error")
                    
            # 显示结果
            message = f"成功删除 {success_count} 个文件"
            if failed_files:
                message += f"，失败 {len(failed_files)} 个文件"
                
            QMessageBox.information(self, "删除完成", message)
            
            # 清空选中
            self.selected_files.clear()
            self.update_selection_count()
            self.delete_btn.setEnabled(False)
            self.move_btn.setEnabled(False)
            
    def move_selected(self):
        """移动选中文件"""
        if not self.selected_files:
            return
            
        # 选择目标目录
        target_dir = QFileDialog.getExistingDirectory(self, "选择目标目录")
        if not target_dir:
            return
            
        success_count = 0
        failed_files = []
        
        # 移动文件
        for file_path in self.selected_files:
            try:
                if os.path.exists(file_path):
                    file_name = os.path.basename(file_path)
                    target_path = os.path.join(target_dir, file_name)
                    
                    # 如果目标文件已存在，添加序号
                    counter = 1
                    base_name, ext = os.path.splitext(file_name)
                    while os.path.exists(target_path):
                        new_name = f"{base_name}_{counter}{ext}"
                        target_path = os.path.join(target_dir, new_name)
                        counter += 1
                        
                    shutil.move(file_path, target_path)
                    success_count += 1
                    self.module.log_message.emit(f"已移动: {file_path} -> {target_path}", "info")
                else:
                    failed_files.append(file_path)
                    self.module.log_message.emit(f"文件不存在: {file_path}", "warning")
            except Exception as e:
                failed_files.append(file_path)
                self.module.log_message.emit(f"移动失败 {file_path}: {str(e)}", "error")
                
        # 显示结果
        message = f"成功移动 {success_count} 个文件到 {target_dir}"
        if failed_files:
            message += f"，失败 {len(failed_files)} 个文件"
            
        QMessageBox.information(self, "移动完成", message)
        
        # 清空选中
        self.selected_files.clear()
        self.update_selection_count()
        self.delete_btn.setEnabled(False)
        self.move_btn.setEnabled(False)
        
    def toggle_log(self):
        """切换日志显示"""
        self.log_area.setVisible(self.log_btn.isChecked())
        
    def on_grid_size_changed(self, value):
        """处理网格大小变化"""
        self.grid_size = value
        # 根据网格大小等级调整缩略图大小
        # 等级1: 60px, 等级5: 120px, 等级8: 180px
        self.thumbnail_size = 60 + (value - 1) * 17  # 调整增量以适应1-8的范围
        
        # 重新加载所有图片以适应新的缩略图大小
        self.update_all_thumbnails()
        
        # 重新布局网格
        self.update_grid_layout()
        
    def update_all_thumbnails(self):
        """更新所有缩略图大小"""
        # 更新所有组的缩略图大小
        for group_widget in self.duplicate_groups:
            # 更新组控件的缩略图大小属性
            group_widget.thumbnail_size = self.thumbnail_size
            # 重新创建图片控件
            group_widget.update_thumbnails(self.thumbnail_size)
        
    def resizeEvent(self, event):
        """处理窗口大小调整事件"""
        super().resizeEvent(event)
        self.update_grid_layout()
        
    def update_grid_layout(self):
        """更新网格布局"""
        if not self.duplicate_groups:
            return

        # 重新排列所有卡片
        # 计算列数（根据窗口宽度动态计算，确保不会溢出）
        width = self.scroll_area.viewport().width()
        # 计算实际需要的卡片宽度（更精确的计算）
        card_content_width = int(self.thumbnail_size * 1.5)  # 3:2比例的图片宽度
        card_margins = 20  # 卡片内边距和边框
        spacing = self.grid_layout.spacing()  # 网格间距
        card_total_width = card_content_width + card_margins + spacing

        # 计算列数，确保在合理范围内且不会溢出
        columns = max(1, min(8, int(width // card_total_width)))  # 向下取整
        
        # 清除现有的行和列拉伸因子
        for i in range(self.grid_layout.rowCount()):
            self.grid_layout.setRowStretch(i, 0)
        for i in range(self.grid_layout.columnCount()):
            self.grid_layout.setColumnStretch(i, 0)
            
        # 清除现有布局中的所有控件
        for i in reversed(range(self.grid_layout.count())):
            widget = self.grid_layout.itemAt(i).widget()
            if widget:
                self.grid_layout.removeWidget(widget)
        
        # 重新添加所有卡片到网格布局
        for i, group_widget in enumerate(self.duplicate_groups):
            # 计算新位置
            row = i // columns
            col = i % columns
            
            # 添加到新位置，左对齐顶部对齐
            self.grid_layout.addWidget(group_widget, row, col, Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)
            
        # 设置列的拉伸因子，使列宽度相等且填满容器
        for i in range(columns):
            self.grid_layout.setColumnStretch(i, 1)

        # 添加一个可伸展的空白行，确保内容从顶部开始排列并可以正常滚动
        rows = (len(self.duplicate_groups) + columns - 1) // columns
        if rows > 0:
            # 在最后一行添加一个伸展因子，确保可以滚动
            self.grid_layout.setRowStretch(rows, 1)

        # 更新状态信息，显示当前列数和容器信息
        if hasattr(self, 'status_label'):
            current_status = self.status_label.text()
            if "找到" in current_status:
                # 保留"找到 X 组重复图片"的信息，添加布局信息
                base_status = current_status.split('|')[0].strip()
                self.status_label.setText(f"{base_status} | 布局: {columns}列 | 容器宽度: {width}px")
            else:
                # 如果没有找到重复图片的信息，只显示布局信息
                self.status_label.setText(f"布局: {columns}列 | 容器宽度: {width}px")




















