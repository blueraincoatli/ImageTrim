#!/usr/bin/env python3
"""
文件夹拖拽区域组件
"""

import os
import sys
from pathlib import Path
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
                             QFrame, QFileDialog, QListWidget, QAbstractItemView,
                             QTableWidget, QTableWidgetItem, QHeaderView, QSizePolicy)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QDragEnterEvent, QDragMoveEvent, QDropEvent
from app.ui.theme import Spacing


class DragDropArea(QFrame):
    """
    拖拽区域组件 - 用于在开始搜索前添加扫描路径并显示统计信息
    """
    
    # 拖拽完成信号，传递路径列表
    paths_dropped = pyqtSignal(list)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.scanned_paths = []  # 存储已扫描路径的统计信息
        self._has_paths = False
        self._background_image = self._resolve_resource("images/greyBG.jpg")
        self._style_empty = self._build_style(empty=True, highlight=False)
        self._style_active = self._build_style(empty=False, highlight=False)
        self._style_drag_empty = self._build_style(empty=True, highlight=True)
        self._style_drag_active = self._build_style(empty=False, highlight=True)
        self.init_ui()
        
    def init_ui(self):
        """初始化UI"""
        # 设置框架样式
        self.setFrameStyle(QFrame.Shape.StyledPanel | QFrame.Shadow.Raised)
        self.setLineWidth(2)
        self._apply_default_style()
        
        # 启用拖拽功能
        self.setAcceptDrops(True)
        
        # 创建布局
        layout = QVBoxLayout(self)
        layout.setContentsMargins(Spacing.LG, Spacing.LG, Spacing.LG, Spacing.LG)
        layout.setSpacing(Spacing.MD)
        
        # 空态占位容器
        self.placeholder_container = QFrame()
        self.placeholder_container.setObjectName("placeholderOverlay")
        self.placeholder_container.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.placeholder_container.setStyleSheet("""
            QFrame#placeholderOverlay {
                background-color: rgba(15, 15, 18, 0.5);
                border: 1px solid rgba(255, 255, 255, 0.08);
                border-radius: 18px;
                padding: 36px;
            }
        """)
        placeholder_layout = QVBoxLayout(self.placeholder_container)
        placeholder_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        placeholder_layout.setSpacing(Spacing.MD)
        
        # 标题图标
        icon_label = QLabel("📁")
        icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        icon_label.setStyleSheet("font-size: 56px;")
        placeholder_layout.addWidget(icon_label)
        
        # 标题文本
        title_label = QLabel("拖拽文件夹到此处")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setStyleSheet("""
            QLabel {
                color: #FFFFFF;
                font-size: 22px;
                font-weight: bold;
                margin: 0px;
            }
        """)
        placeholder_layout.addWidget(title_label)
        
        # 说明文本
        desc_label = QLabel()
        desc_label.setTextFormat(Qt.TextFormat.RichText)
        desc_label.setText("""
            <p style='line-height: 1.8; margin: 0;'>
                支持多选文件夹，可将文件夹从文件管理器拖拽至此区域<br>
                拖拽的文件夹将自动添加到左侧扫描路径列表
            </p>
        """)
        desc_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        desc_label.setStyleSheet("""
            color: #AAAAAA;
            font-size: 14px;
            margin: 6px 12px 0 12px;
        """)
        desc_label.setWordWrap(True)
        placeholder_layout.addWidget(desc_label)
        layout.addWidget(self.placeholder_container, 1, Qt.AlignmentFlag.AlignCenter)
        
        # 统计信息区域（初始状态隐藏）
        self.stats_group = QFrame()
        self.stats_group.setStyleSheet("""
            QFrame {
                background-color: #1e1e1e;
                border: 1px solid #3f3f46;
                border-radius: 6px;
                padding: 10px;
            }
        """)
        self.stats_group.setVisible(False)
        stats_layout = QVBoxLayout(self.stats_group)
        stats_layout.setSpacing(Spacing.SM)
        
        # 总览统计信息（简化为一行）
        self.overall_info = QLabel("📊 目录: 0 | 图片: 0 | 大小: 0 B")
        self.overall_info.setStyleSheet("""
            color: #CCCCCC;
            font-size: 12px;
            padding: 5px 0px;
            border-bottom: 1px solid #3f3f46;
            margin-bottom: 5px;
        """)
        stats_layout.addWidget(self.overall_info)
        
        # 详细统计区域（使用滚动区域，增加高度）
        from PyQt6.QtWidgets import QScrollArea
        self.stats_scroll = QScrollArea()
        self.stats_scroll.setWidgetResizable(True)
        self.stats_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.stats_scroll.setMinimumHeight(180)  # 增加最小高度
        self.stats_scroll.setStyleSheet("""
            QScrollArea {
                border: none;
                background-color: transparent;
            }
            QScrollBar:vertical {
                background-color: #2d2d30;
                width: 10px;
                border: none;
                border-radius: 5px;
            }
            QScrollBar::handle:vertical {
                background-color: #555555;
                border-radius: 5px;
                min-height: 20px;
            }
        """)
        
        self.stats_container = QWidget()
        self.stats_container.setStyleSheet("background-color: transparent;")
        self.stats_layout = QVBoxLayout(self.stats_container)
        self.stats_layout.setSpacing(Spacing.XS)
        self.stats_layout.setContentsMargins(0, 0, 0, 0)
        
        self.stats_scroll.setWidget(self.stats_container)
        stats_layout.addWidget(self.stats_scroll)
        
        layout.addWidget(self.stats_group)
        
    def dragEnterEvent(self, event: QDragEnterEvent):
        """拖拽进入事件"""
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
            # 改变样式表示可以接受拖拽
            self.setStyleSheet(self._style_drag_active if self._has_paths else self._style_drag_empty)
        else:
            event.ignore()
            
    def dragMoveEvent(self, event: QDragMoveEvent):
        """拖拽移动事件"""
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
        else:
            event.ignore()
            
    def dragLeaveEvent(self, event):
        """拖拽离开事件"""
        # 恢复原始样式
        self._apply_default_style()
        super().dragLeaveEvent(event)
            
    def dropEvent(self, event: QDropEvent):
        """拖拽释放事件"""
        if event.mimeData().hasUrls():
            urls = event.mimeData().urls()
            new_paths = []
            
            for url in urls:
                path = url.toLocalFile()
                if path and os.path.isdir(path) and path not in new_paths:
                    new_paths.append(path)
            
            if new_paths:
                self.paths_dropped.emit(new_paths)
                self.analyze_paths(new_paths)
            event.acceptProposedAction()
        else:
            event.ignore()
        
        self._apply_default_style()
        
    def analyze_paths(self, paths):
        """分析路径并显示统计信息"""
        # 清空现有统计信息
        self.scanned_paths.clear()
        
        # 清空统计容器
        for i in reversed(range(self.stats_layout.count())):
            item = self.stats_layout.takeAt(i)
            if not item:
                continue
            widget = item.widget()
            if widget is not None:
                widget.setParent(None)
        
        # 支持的图片格式
        image_extensions = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.webp', '.avif'}
        
        total_files = 0
        total_size = 0
        
        for path in paths:
            try:
                image_count = 0
                path_size = 0
                format_counts = {}
                
                # 遍历目录统计图片文件
                for root, dirs, files in os.walk(path):
                    for file in files:
                        ext = os.path.splitext(file)[1].lower()
                        if ext in image_extensions:
                            image_count += 1
                            file_path = os.path.join(root, file)
                            try:
                                file_size = os.path.getsize(file_path)
                                path_size += file_size
                                total_size += file_size
                                
                                # 统计格式分布
                                format_counts[ext] = format_counts.get(ext, 0) + 1
                            except:
                                pass
                
                total_files += image_count
                
                # 添加到统计列表
                self.scanned_paths.append({
                    'path': path,
                    'image_count': image_count,
                    'size': path_size,
                    'formats': format_counts
                })
                
                # 创建目录统计卡片
                self.create_stats_card(path, image_count, path_size, format_counts)
                
            except Exception as e:
                print(f"分析路径 {path} 时出错: {e}")
        
        # 如果有统计信息，显示统计区域
        if self.scanned_paths:
            self._has_paths = True
            self.placeholder_container.setVisible(False)
            self.stats_group.setVisible(True)
            
            # 更新总览统计
            total_size_str = self.format_size(total_size)
            self.overall_info.setText(f"📊 目录: {len(paths)} | 图片: {total_files} | 大小: {total_size_str}")
            
            # 添加弹性空间
            self.stats_layout.addStretch()
        else:
            self._has_paths = False
            self.stats_group.setVisible(False)
            self.placeholder_container.setVisible(True)

        self._apply_default_style()
    
    def create_stats_card(self, path, image_count, size, formats):
        """创建单个目录的统计卡片"""
        card = QFrame()
        card.setStyleSheet("""
            QFrame {
                background-color: #252526;
                border: 1px solid #3f3f46;
                border-radius: 4px;
                padding: 8px;
                margin: 2px;
            }
            QFrame:hover {
                background-color: #2a2a2a;
                border: 1px solid #555555;
            }
        """)
        
        layout = QHBoxLayout(card)
        layout.setContentsMargins(Spacing.SM, Spacing.SM, Spacing.SM, Spacing.SM)
        
        # 目录名
        dir_name = os.path.basename(path)
        name_label = QLabel(f"📁 {dir_name}")
        name_label.setStyleSheet("color: #FFFFFF; font-weight: bold; font-size: 13px;")
        name_label.setToolTip(path)
        layout.addWidget(name_label)
        
        layout.addStretch()
        
        # 图片数量
        count_label = QLabel(f"图片: {image_count}")
        count_label.setStyleSheet("color: #87CEEB; font-size: 12px;")
        layout.addWidget(count_label)
        
        # 文件大小
        size_str = self.format_size(size)
        size_label = QLabel(f"大小: {size_str}")
        size_label.setStyleSheet("color: #98FB98; font-size: 12px;")
        layout.addWidget(size_label)
        
        # 主要格式
        if formats:
            main_format = max(formats.items(), key=lambda x: x[1])[0]
            format_label = QLabel(f"主格式: {main_format}")
            format_label.setStyleSheet("color: #FFD700; font-size: 12px;")
            layout.addWidget(format_label)
        
        self.stats_layout.addWidget(card)
        
    def format_size(self, size_bytes):
        """格式化文件大小"""
        if size_bytes == 0:
            return "0 B"

        size_names = ["B", "KB", "MB", "GB", "TB"]
        i = 0
        while size_bytes >= 1024 and i < len(size_names) - 1:
            size_bytes /= 1024.0
            i += 1

        return f"{size_bytes:.2f} {size_names[i]}"

    def set_paths(self, paths):
        """
        设置路径列表并分析统计信息

        Args:
            paths: 路径列表
        """
        # 始终调用analyze_paths，即使paths为空
        # 这样可以在清空路径时也清除统计信息
        self.analyze_paths(paths)

    def _apply_default_style(self):
        if self._has_paths:
            self.setStyleSheet(self._style_active)
        else:
            self.setStyleSheet(self._style_empty)

    def _build_style(self, *, empty: bool, highlight: bool) -> str:
        border_color = "#FF8C00" if highlight else "#555555"
        background_color = "rgba(51, 51, 55, 0.85)" if highlight else "#2d2d30"
        background_image = ""
        if empty and self._background_image:
            normalized = self._background_image.replace("\\", "/")
            background_image = f"""
                background-image: url("{normalized}");
                background-position: center;
                background-repeat: no-repeat;
                background-size: cover;
            """
        return f"""
            DragDropArea {{
                background-color: {background_color};
                border: 2px dashed {border_color};
                border-radius: 12px;
                min-height: 220px;
                {background_image}
            }}
            DragDropArea:hover {{
                border: 2px dashed #FF8C00;
                background-color: rgba(51, 51, 55, 0.85);
            }}
        """

    def _resolve_resource(self, relative_path: str) -> str | None:
        """解析资源文件路径，支持 PyInstaller 和 Nuitka"""
        from app.utils.resource_path import get_resource_path
        return get_resource_path(relative_path)
