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
from PyQt6.QtWidgets import QSizePolicy
from PyQt6.QtCore import Qt, pyqtSignal, QRectF, QCoreApplication
from PyQt6.QtGui import QPixmap, QImage, QKeySequence, QShortcut, QPainter, QColor, QPen, QScreen
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
            from PIL import Image, ImageFile
            # 设置加载截断处理，避免因截断图像导致的错误
            ImageFile.LOAD_TRUNCATED_IMAGES = True
            
            with Image.open(self.image_path) as img:
                # 转换为RGB（处理RGBA等格式）
                if img.mode != 'RGB':
                    img = img.convert('RGB')
                
                # 检查图像尺寸是否合理
                if img.width <= 0 or img.height <= 0:
                    raise Exception("无效的图像尺寸")
                
                # 限制最大尺寸以避免内存问题
                max_dimension = 8192
                if img.width > max_dimension or img.height > max_dimension:
                    # 按比例缩放
                    ratio = min(max_dimension / img.width, max_dimension / img.height)
                    new_width = int(img.width * ratio)
                    new_height = int(img.height * ratio)
                    img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
                
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
            # 显示错误信息而不是退出程序
            self.scene.clear()
            error_item = self.scene.addText(error_msg, self.font())
            error_item.setDefaultTextColor(QColor(255, 0, 0))
            
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
    
    def __init__(self, file_path: str, width: int = 180, height: int = 120, parent=None):
        super().__init__(parent)
        self.file_path = file_path
        self.width = width
        self.height = height
        self.is_selected = False
        self.init_ui()
        
    def init_ui(self):
        """初始化UI"""
        # 设置样式（透明背景）
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
        """创建图片标签，使用新的内存图片缓存系统"""
        # 创建容器标签（完美居中显示）
        container = QLabel()
        container.setAlignment(Qt.AlignmentFlag.AlignCenter)
        container.setStyleSheet("""
            QLabel {
                background-color: transparent;
                border: none;
                padding: 0px;
                margin: 0px;
                qproperty-alignment: AlignCenter;
            }
        """)

        # 使用新的内存图片缓存系统
        try:
            from utils.image_cache_enhanced import get_image_cache
            image_cache = get_image_cache()

            # 获取统一缩略图
            pixmap = image_cache.get_thumbnail_pixmap(
                self.file_path,
                self.width,
                self.height
            )

            if pixmap and not pixmap.isNull():
                # 设置缩略图并确保完美居中
                container.setPixmap(pixmap)

                # 强制重新计算布局以确保居中
                container.update()
                container.updateGeometry()
            else:
                # 显示占位符
                container.setText("⏳")
                container.setStyleSheet("""
                    QLabel {
                        color: #6c757d;
                        font-size: 24px;
                        background-color: #1e1e1e;
                        border: none;
                        padding: 0px;
                        margin: 0px;
                    }
                """)

                # 连接缩略图准备好信号
                try:
                    # 确保只连接一次信号
                    if not hasattr(self, '_thumbnail_signal_connected'):
                        image_cache.thumbnail_ready.connect(self._on_thumbnail_ready)
                        self._thumbnail_signal_connected = True
                except Exception as e:
                    print(f"连接缩略图准备好信号失败: {e}")

        except Exception as e:
            print(f"图片缓存加载失败: {e}")
            # 如果缓存加载失败，使用原始方法
            return self._create_image_label_fallback(container)

        return container

    def _create_image_label_fallback(self, container):
        """备用方法：直接加载图片"""
        try:
            # 获取原始图片尺寸
            from PIL import Image
            with Image.open(self.file_path) as img:
                original_width, original_height = img.size

            # 计算缩放比例，确保图片适应指定尺寸的容器
            container_aspect_ratio = self.width / self.height
            image_aspect_ratio = original_width / original_height

            if image_aspect_ratio > container_aspect_ratio:
                # 图片更宽，以宽度为准
                new_width = self.width
                new_height = int(new_width / image_aspect_ratio)
            else:
                # 图片更高，以高度为准
                new_height = self.height
                new_width = int(new_height * image_aspect_ratio)

            # 限制图片最大尺寸
            if new_width > self.width:
                new_width = self.width
            if new_height > self.height:
                new_height = self.height

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
            container.setFixedSize(self.width, self.height)
            container.setStyleSheet("color: #dc3545; font-size: 24px; background-color: transparent; border: none;")

        return container

    def _on_thumbnail_ready(self, file_path, pixmap):
        """缩略图准备好时的回调"""
        if file_path == self.file_path and hasattr(self, 'image_label'):
            try:
                # 缓存系统已经提供了正确尺寸的缩略图，直接设置
                if pixmap and not pixmap.isNull():
                    # 按宽度缩放图片，保持原始宽高比
                    scaled_pixmap = pixmap.scaledToWidth(
                        self.width,
                        Qt.TransformationMode.SmoothTransformation
                    )
                    self.image_label.setPixmap(scaled_pixmap)
                else:
                    # 如果缩略图为空，显示占位符
                    self.image_label.setText("⏳")
                    self.image_label.setStyleSheet("""
                        QLabel {
                            color: #6c757d;
                            font-size: 24px;
                            background-color: transparent;
                            border: none;
                            padding: 0px;
                            margin: 0px;
                        }
                    """)
            except Exception as e:
                print(f"设置缩略图时出错: {e}")
                # 显示错误占位符
                self.image_label.setText("🚫")
                self.image_label.setStyleSheet("""
                    QLabel {
                        color: #dc3545;
                        font-size: 24px;
                        background-color: transparent;
                        border: none;
                        padding: 0px;
                        margin: 0px;
                    }
                """)

            # 强制重新计算布局以确保完美居中
            self.image_label.update()
            self.image_label.updateGeometry()
        
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
        self.images_layout = None
        self.card_height = 0  # 卡片高度
        self.init_ui()
        
    def init_ui(self):
        """初始化UI"""
        self.setStyleSheet("""
            QFrame {
                background-color: #1B1B1B;
                border: 1px solid #353535;
                border-radius: 8px;
            }
            QFrame:hover {
                background-color: #252525;
            }
        """)
        
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        images_container = QFrame()
        images_container.setStyleSheet("background-color: transparent; border: none;")
        self.images_layout = QHBoxLayout(images_container)
        self.images_layout.setContentsMargins(0, 0, 0, 0)
        self.images_layout.setSpacing(0)
        main_layout.addWidget(images_container)

    def update_thumbnails(self, card_width: int):
        """更新缩略图大小"""
        # 设置卡片固定宽高比 (宽度:高度 = 2:1)
        self.card_height = int(card_width / 2)
        self.setFixedHeight(self.card_height)
        
        # 计算内边距和间距
        padding = int(self.card_height / 6)  # 内边距为卡片高度的1/6
        spacing = int(self.card_height / 12)  # 图片间距为卡片高度的1/12
        
        # 设置图片布局的边距
        self.images_layout.setContentsMargins(padding, padding, padding, padding)
        self.images_layout.setSpacing(spacing)
        
        # 清除现有内容
        for widget in self.image_widgets:
            widget.setParent(None)
        self.image_widgets.clear()
        
        while self.images_layout.count():
            child = self.images_layout.takeAt(0)
            if child.widget():
                child.widget().setParent(None)

        # 计算每张图片的可用空间
        if len(self.files) > 0:
            # 可用宽度 = 卡片宽度 - 2*内边距 - (图片数量-1)*间距
            available_width = card_width - 2 * padding - (len(self.files) - 1) * spacing
            # 每张图片的平均宽度
            image_width = int(available_width / len(self.files))
            # 图片高度应该根据卡片高度和内边距计算，留出一些额外空间
            image_height = self.card_height - 2 * padding - 10  # 减去一些额外空间确保图片不会超出边界
            # 确保图片高度不为负数
            image_height = max(50, image_height)  # 最小高度为50像素
        else:
            image_width = 100  # 默认宽度
            image_height = 50  # 默认高度
            
        # 重新添加控件
        for file_path in self.files:
            image_widget = DuplicateImageWidget(file_path, image_width, image_height)
            image_widget.selection_changed.connect(self.on_image_selection_changed)
            image_widget.image_double_clicked.connect(self.image_double_clicked.emit)
            self.images_layout.addWidget(image_widget)
            self.image_widgets.append(image_widget)
        
    def on_image_selection_changed(self, files, is_selected):
        """处理图片选择变化"""
        self.selection_changed.emit(self.files, is_selected)
        
    def set_selected(self, selected):
        """设置选中状态"""
        self.is_selected = selected
        if selected:
            self.setStyleSheet("""
                QFrame {
                    background-color: #2a2a2e;
                    border: 2px solid #FF8C00;
                    border-radius: 8px;
                }
            """)
        else:
            self.setStyleSheet("""
                QFrame {
                    background-color: #1B1B1B;
                    border: 1px solid #353535;
                    border-radius: 8px;
                }
                QFrame:hover {
                    background-color: #252525;
                }
            """)
        self.style().unpolish(self)
        self.style().polish(self)
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
        self.grid_size = 3  # 网格列数 (1-8)
        self.thumbnail_size = 120  # 缩略图大小

        # 获取DPI缩放因子
        self.dpi_scale_factor = self.get_dpi_scale_factor()
        print(f"DPI调试: 初始化DPI缩放因子 = {self.dpi_scale_factor}")

        self.init_ui()
        self.connect_signals()

    def get_dpi_scale_factor(self):
        """获取DPI缩放因子"""
        try:
            # 获取主屏幕
            screen = QCoreApplication.instance().primaryScreen()
            if screen:
                # 获取逻辑DPI和物理DPI
                logical_dpi = screen.logicalDotsPerInch()
                physical_dpi = screen.physicalDotsPerInch()
                # 计算缩放因子
                scale_factor = logical_dpi / 96.0  # 96是标准DPI
                print(f"DPI调试: 逻辑DPI={logical_dpi}, 物理DPI={physical_dpi}, 缩放因子={scale_factor}")
                return scale_factor
        except Exception as e:
            print(f"获取DPI缩放因子时出错: {str(e)}")

        # 如果无法获取，使用默认值
        print("DPI调试: 无法获取DPI信息，使用默认缩放因子1.0")
        return 1.0
        
    def init_ui(self):
        """初始化UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)
        
        # 创建分割器用于结果区域和日志区域
        self.splitter = QSplitter(Qt.Orientation.Vertical)
        # 连接分割器移动信号，以便在分割线移动时更新布局
        self.splitter.splitterMoved.connect(self.on_splitter_moved)
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
        
        # 网格列数控制
        self.grid_size_label = QLabel("网格列数:")
        self.grid_size_label.setStyleSheet("color: white; margin-left: 10px;")
        top_layout.addWidget(self.grid_size_label)

        self.grid_size_slider = QSlider(Qt.Orientation.Horizontal)
        self.grid_size_slider.setRange(1, 8)  # 1-8列
        self.grid_size_slider.setValue(3)  # 默认3列，更适合大多数屏幕
        self.grid_size_slider.setFixedWidth(120)
        self.grid_size_slider.setStyleSheet("""
            QSlider::groove:horizontal {
                border: none;
                height: 6px;
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                                         stop:0 #404040, stop:1 #2a2a2a);
                margin: 2px 0;
                border-radius: 3px;
            }
            QSlider::handle:horizontal {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                         stop:0 #FF8C00, stop:0.5 #FF6B35, stop:1 #FF8C00);
                border: 2px solid #ffffff;
                width: 20px;
                margin: -8px 0;
                border-radius: 10px;
                box-shadow: 0 2px 4px rgba(0,0,0,0.3);
            }
            QSlider::handle:horizontal:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                         stop:0 #FFA500, stop:0.5 #FF8C00, stop:1 #FFA500);
                border: 2px solid #ffffff;
                box-shadow: 0 4px 8px rgba(255,140,0,0.4);
                transform: scale(1.1);
            }
            QSlider::handle:horizontal:pressed {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                         stop:0 #FF6B35, stop:0.5 #FF4500, stop:1 #FF6B35);
                border: 2px solid #ffffff;
                box-shadow: 0 2px 6px rgba(255,140,0,0.6);
                transform: scale(0.95);
            }
            QSlider::sub-page:horizontal {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                                         stop:0 #FF8C00, stop:0.5 #FF6B35, stop:1 #FF8C00);
                border-radius: 3px;
                margin: 2px 0;
            }
            QSlider::add-page:horizontal {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                                         stop:0 #404040, stop:1 #2a2a2a);
                border-radius: 3px;
                margin: 2px 0;
            }
        """)
        self.grid_size_slider.valueChanged.connect(self.on_grid_size_changed)
        top_layout.addWidget(self.grid_size_slider)

        # 显示当前列数的标签
        self.grid_size_value_label = QLabel("3")
        self.grid_size_value_label.setStyleSheet("""
            color: #FF8C00;
            font-weight: bold;
            font-size: 14px;
            min-width: 20px;
            padding: 2px 6px;
            background: rgba(255, 140, 0, 0.1);
            border: 1px solid rgba(255, 140, 0, 0.3);
            border-radius: 4px;
        """)
        top_layout.addWidget(self.grid_size_value_label)

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

        # 延迟执行一次布局更新，确保窗口已经完全显示
        from PyQt6.QtCore import QTimer
        QTimer.singleShot(100, self.delayed_layout_update)

    def force_thumbnail_refresh(self):
        """强制刷新缩略图显示"""
        try:
            if hasattr(self, 'duplicate_groups') and self.duplicate_groups:
                print(f"强制刷新 {len(self.duplicate_groups)} 个重复组的缩略图")
                # 重新计算当前列宽并刷新所有缩略图
                columns = self.grid_size
                container_width = self.scroll_area.viewport().width()
                if container_width > 0:
                    column_width = container_width // columns

                    for group_widget in self.duplicate_groups:
                        if hasattr(group_widget, 'files') and group_widget.files:
                            self.update_group_widget_size(group_widget, column_width)

                    # 强制UI更新
                    self.scroll_area.viewport().update()
                    
                    # 触发所有缩略图重新加载
                    self.reload_all_thumbnails()
        except Exception as e:
            print(f"强制刷新缩略图时出错: {e}")

    def delayed_layout_update(self):
        """延迟布局更新，确保窗口已经完全显示"""
        if hasattr(self, 'grid_layout') and self.grid_layout:
            print("DPI调试: 执行延迟布局更新")
            self.update_grid_layout()
            
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
            # 使用滑块定义的列数
            columns = self.grid_size  # 直接使用用户设置的列数

            # 计算每列的精确宽度（容器总宽度 / 列数）
            container_width = self.scroll_area.viewport().width()
            column_width = container_width // columns
            
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

                # 立即设置正确的图片尺寸（关键修复！）
                if hasattr(self, 'scroll_area') and self.scroll_area:
                    self.update_group_widget_size(group_widget, column_width)
                
            # 设置列的拉伸因子，使列宽度相等
            for i in range(columns):
                self.grid_layout.setColumnStretch(i, 1)
                
            # 设置行的拉伸因子，使行高度相等
            rows = (len(group_items) + columns - 1) // columns
            for i in range(rows):
                self.grid_layout.setRowStretch(i, 1)
                
            self.status_label.setText(f"找到 {len(group_items)} 组重复图片 | 布局: {columns}列 | 列宽: {column_width}px | 缩略图: {self.thumbnail_size}px")

            # 强制刷新布局和缩略图显示（修复自动刷新问题）
            from PyQt6.QtCore import QTimer
            QTimer.singleShot(100, self.force_thumbnail_refresh)
            
            # 再次刷新以确保所有缩略图都加载完成
            QTimer.singleShot(500, self.force_thumbnail_refresh)
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
        
    def on_splitter_moved(self, pos, index):
        """处理分割器移动事件"""
        try:
            # 延迟更新布局，避免在分割器拖动过程中频繁更新
            self.update_grid_layout()
        except Exception as e:
            print(f"分割器移动时出错: {str(e)}")

    def on_grid_size_changed(self, value):
        """处理网格列数变化"""
        self.grid_size = value

        # 更新显示当前列数的标签
        if hasattr(self, 'grid_size_value_label'):
            self.grid_size_value_label.setText(str(value))

        # 重新布局网格，这会更新每个重复组卡片的宽度
        self.update_grid_layout()
        
        # 延迟刷新缩略图以确保布局已经更新
        from PyQt6.QtCore import QTimer
        QTimer.singleShot(50, self.force_thumbnail_refresh)

    def update_group_widget_size(self, group_widget, column_width):
        """更新重复组卡片的尺寸和内部缩略图大小"""
        # 直接传递卡片宽度给update_thumbnails方法
        # DuplicateGroupWidget会根据固定宽高比自动计算高度
        group_widget.update_thumbnails(column_width)

    # update_all_thumbnails方法已移除，因为现在通过update_grid_layout和update_group_widget_size来处理
        
    def resizeEvent(self, event):
        """处理窗口大小调整事件"""
        try:
            super().resizeEvent(event)
            self.update_grid_layout()
        except Exception as e:
            # 捕获并记录调整大小时的错误，避免程序崩溃
            print(f"窗口调整大小时出错: {str(e)}")
            # 如果出错，至少确保基本布局还能工作
            if hasattr(self, 'status_label'):
                self.status_label.setText("布局更新出错，请尝试重新调整窗口大小")
        
    def reload_all_thumbnails(self):
        """重新加载所有缩略图"""
        try:
            # 通过更新整个网格布局来重新加载所有缩略图
            # 这会重新创建所有图片控件，从而触发缩略图的重新加载
            self.update_grid_layout()
            
            # 额外触发一次缓存刷新
            from utils.image_cache_enhanced import get_image_cache
            image_cache = get_image_cache()
            
            # 清理缓存并重新生成
            image_cache.clear_cache()
        except Exception as e:
            print(f"重新加载缩略图时出错: {e}")

    def update_grid_layout(self):
        """更新网格布局"""
        if not self.duplicate_groups:
            return

        try:
            # 使用滑块定义的列数
            columns = self.grid_size  # 直接使用用户设置的列数

            # 获取容器宽度和网格布局参数
            container_width = self.scroll_area.viewport().width()
            if container_width <= 0:
                return  # 避免除零错误

            # 获取网格布局的间距和边距
            grid_spacing = self.grid_layout.spacing()  # 网格间距（默认10px）
            margins = self.grid_layout.contentsMargins()
            left_margin = margins.left()
            right_margin = margins.right()
            top_margin = margins.top()
            bottom_margin = margins.bottom()
            total_horizontal_margin = left_margin + right_margin
            total_spacing_width = grid_spacing * (columns - 1)  # 列间距总数

            # 考虑DPI缩放因子调整容器宽度
            scaled_container_width = int(container_width / self.dpi_scale_factor)

            # 计算实际可用的宽度（容器宽度 - 边距 - 间距）
            available_width = scaled_container_width - total_horizontal_margin - total_spacing_width

            # 计算每列的实际可用宽度
            if available_width <= 0:
                print(f"DPI调试: 警告 - 可用宽度为负数或零: available_width={available_width}, 跳过布局更新")
                return  # 避免负数或零宽度

            # 确保最小列宽
            min_column_width = 100  # 最小列宽100px
            if available_width < columns * min_column_width:
                print(f"DPI调试: 警告 - 可用宽度不足以显示{columns}列, 最小需要{columns * min_column_width}px, 实际{available_width}px")
                # 自动减少列数以适应可用宽度
                columns = max(1, available_width // min_column_width)
                total_spacing_width = grid_spacing * (columns - 1)
                available_width = scaled_container_width - total_horizontal_margin - total_spacing_width
                print(f"DPI调试: 自动调整列数为{columns}, 新的可用宽度={available_width}px")

            actual_column_width = available_width // columns

            # 为了显示实际值，我们也保存原始逻辑宽度
            logical_container_width = container_width
            logical_available_width = logical_container_width - total_horizontal_margin - total_spacing_width
            logical_column_width = logical_available_width // columns

            print(f"DPI调试: 更新布局 - 列数={columns}, 容器宽度={container_width}, 缩放容器宽度={scaled_container_width}")
            print(f"DPI调试: 网格参数 - 左边距={left_margin}px, 右边距={right_margin}px, 总边距={total_horizontal_margin}px, 网格间距={grid_spacing}px, 总间距={total_spacing_width}px")
            print(f"DPI调试: 可用宽度 - 缩放可用={available_width}px, 逻辑可用={logical_available_width}px")
            print(f"DPI调试: 最终列宽 - 缩放列宽={actual_column_width}px, 逻辑列宽={logical_column_width}px, DPI缩放因子={self.dpi_scale_factor}")

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

            # 重新添加所有卡片到网格布局，并更新每个卡片的尺寸
            for i, group_widget in enumerate(self.duplicate_groups):
                # 计算新位置
                row = i // columns
                col = i % columns

                # 添加到新位置，居中对齐
                self.grid_layout.addWidget(group_widget, row, col, Qt.AlignmentFlag.AlignCenter)

                # 更新这个重复组卡片的宽度并重新计算内部图片大小
                self.update_group_widget_size(group_widget, actual_column_width)

            # 设置每列的固定宽度，使用实际计算的列宽
            for i in range(columns):
                self.grid_layout.setColumnStretch(i, 1)
                self.grid_layout.setColumnMinimumWidth(i, actual_column_width)

            # 清除多余的列拉伸因子，避免影响布局
            for i in range(columns, self.grid_layout.columnCount()):
                self.grid_layout.setColumnStretch(i, 0)

            # 添加一个可伸展的空白行，确保内容从顶部开始排列并可以正常滚动
            rows = (len(self.duplicate_groups) + columns - 1) // columns
            if rows > 0:
                # 在最后一行添加一个伸展因子，确保可以滚动
                self.grid_layout.setRowStretch(rows, 1)

            # 更新状态信息，显示当前布局信息
            if hasattr(self, 'status_label'):
                current_status = self.status_label.text()
                if "找到" in current_status:
                    # 保留"找到 X 组重复图片"的信息，更新布局信息
                    base_status = current_status.split('|')[0].strip()
                    if self.dpi_scale_factor != 1.0:
                        self.status_label.setText(f"{base_status} | 布局: {columns}列(重复组) | 可用宽度: {logical_available_width}px | 列宽: {logical_column_width}px | DPI缩放: {self.dpi_scale_factor:.2f}x")
                    else:
                        self.status_label.setText(f"{base_status} | 布局: {columns}列(重复组) | 可用宽度: {logical_available_width}px | 列宽: {logical_column_width}px")
                else:
                    # 如果没有找到重复图片的信息，只显示布局信息
                    if self.dpi_scale_factor != 1.0:
                        self.status_label.setText(f"布局: {columns}列(重复组) | 可用宽度: {logical_available_width}px | 列宽: {logical_column_width}px | DPI缩放: {self.dpi_scale_factor:.2f}x")
                    else:
                        self.status_label.setText(f"布局: {columns}列(重复组) | 可用宽度: {logical_available_width}px | 列宽: {logical_column_width}px")

        except Exception as e:
            # 捕获并记录布局更新时的错误
            print(f"更新网格布局时出错: {str(e)}")
            if hasattr(self, 'status_label'):
                self.status_label.setText("布局更新出错，请尝试调整窗口大小或更改列数")




















