#!/usr/bin/env python3
"""
图片查看器组件
"""

from PyQt6.QtWidgets import QDialog, QLabel, QVBoxLayout, QHBoxLayout, QPushButton, QScrollArea, QWidget
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QPixmap, QImage, QKeySequence, QShortcut
from utils.image_utils import ImageUtils
from PIL import Image
import os


class ImageViewer(QDialog):
    """
    图片查看器对话框
    支持：
    - 滚动查看大图
    - 缩放功能
    - 双击关闭
    - ESC键关闭
    """
    
    def __init__(self, image_path, parent=None):
        super().__init__(parent)
        self.image_path = image_path
        self.pixmap = None
        self.scale_factor = 1.0
        self.init_ui()
        self.load_image()
        self.setup_shortcuts()
        
    def init_ui(self):
        """初始化UI"""
        self.setWindowTitle(f"图片预览 - {os.path.basename(self.image_path)}")
        self.setWindowState(Qt.WindowState.WindowMaximized)
        self.setStyleSheet("""
            QDialog {
                background-color: #1e1e1e;
            }
            QLabel {
                background-color: transparent;
                color: white;
                border: none;
            }
            QPushButton {
                background-color: #333337;
                color: #ffffff;
                border: 1px solid #454545;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: 500;
            }
            QPushButton:hover {
                background-color: #3f3f46;
            }
        """)
        
        # 主布局
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(10)
        
        # 顶部工具栏
        toolbar = QHBoxLayout()
        toolbar.setContentsMargins(0, 0, 0, 0)
        
        # 文件名标签
        self.filename_label = QLabel(os.path.basename(self.image_path))
        self.filename_label.setStyleSheet("font-weight: bold; font-size: 14px;")
        toolbar.addWidget(self.filename_label)
        toolbar.addStretch()
        
        # 缩放按钮
        self.zoom_in_btn = QPushButton("放大 (+)")
        self.zoom_in_btn.clicked.connect(self.zoom_in)
        toolbar.addWidget(self.zoom_in_btn)
        
        self.zoom_out_btn = QPushButton("缩小 (-)")
        self.zoom_out_btn.clicked.connect(self.zoom_out)
        toolbar.addWidget(self.zoom_out_btn)
        
        self.reset_btn = QPushButton("重置 (100%)")
        self.reset_btn.clicked.connect(self.reset_zoom)
        toolbar.addWidget(self.reset_btn)
        
        main_layout.addLayout(toolbar)
        
        # 滚动区域
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.scroll_area.setStyleSheet("""
            QScrollArea {
                border: 1px solid #353535;
                border-radius: 4px;
                background-color: #2d2d30;
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
        """)
        
        # 图片标签
        self.image_label = QLabel()
        self.image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.image_label.setStyleSheet("background-color: #2d2d30; border: none;")
        self.image_label.mouseDoubleClickEvent = self.mouseDoubleClickEvent
        
        self.scroll_area.setWidget(self.image_label)
        main_layout.addWidget(self.scroll_area)
        
        # 状态栏
        self.status_label = QLabel("双击图片或按ESC键关闭")
        self.status_label.setStyleSheet("color: #cccccc; font-size: 12px; padding: 5px;")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(self.status_label)
        
    def load_image(self):
        """加载图片"""
        try:
            # 使用PIL加载图片以支持更多格式
            with Image.open(self.image_path) as img:
                # 转换为RGB格式（如果需要）
                if img.mode in ('RGBA', 'LA', 'P'):
                    img = img.convert('RGB')
                
                # 转换为QImage
                qimage = ImageUtils.pil_to_qimage(img)
                self.pixmap = QPixmap.fromImage(qimage)
                
            # 设置图片
            self.image_label.setPixmap(self.pixmap)
            self.image_label.resize(self.pixmap.size())
            
            # 记录原始尺寸
            self.original_size = self.pixmap.size()
            self.update_status()
            
        except Exception as e:
            self.image_label.setText(f"无法加载图片: {str(e)}")
            self.image_label.setStyleSheet("color: #dc3545; font-size: 16px; background-color: #2d2d30;")
            
    def setup_shortcuts(self):
        """设置快捷键"""
        # ESC键关闭
        esc_shortcut = QShortcut(QKeySequence(Qt.Key.Key_Escape), self)
        esc_shortcut.activated.connect(self.close)
        
        # '+' 键放大
        zoom_in_shortcut = QShortcut(QKeySequence.StandardKey.ZoomIn, self)
        zoom_in_shortcut.activated.connect(self.zoom_in)
        
        # '-' 键缩小
        zoom_out_shortcut = QShortcut(QKeySequence.StandardKey.ZoomOut, self)
        zoom_out_shortcut.activated.connect(self.zoom_out)
        
        # '0' 键重置
        reset_shortcut = QShortcut(QKeySequence("0"), self)
        reset_shortcut.activated.connect(self.reset_zoom)
        
    def zoom_in(self):
        """放大"""
        self.scale_image(1.2)
        
    def zoom_out(self):
        """缩小"""
        self.scale_image(0.8)
        
    def reset_zoom(self):
        """重置缩放"""
        self.scale_factor = 1.0
        if self.pixmap:
            self.image_label.setPixmap(self.pixmap)
            self.image_label.resize(self.pixmap.size())
            self.update_status()
            
    def scale_image(self, factor):
        """缩放图片"""
        if not self.pixmap:
            return
            
        self.scale_factor *= factor
        # 限制缩放范围
        self.scale_factor = max(0.1, min(self.scale_factor, 10.0))
        
        new_size = self.original_size * self.scale_factor
        scaled_pixmap = self.pixmap.scaled(
            new_size,
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation
        )
        self.image_label.setPixmap(scaled_pixmap)
        self.image_label.resize(scaled_pixmap.size())
        self.update_status()
        
    def update_status(self):
        """更新状态栏"""
        if self.pixmap:
            self.status_label.setText(
                f"尺寸: {self.original_size.width()}×{self.original_size.height()} "
                f"缩放: {self.scale_factor*100:.1f}% "
                f"双击图片或按ESC键关闭"
            )
            
    def mouseDoubleClickEvent(self, event):
        """双击事件 - 关闭查看器"""
        self.close()