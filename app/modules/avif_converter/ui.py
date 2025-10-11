#!/usr/bin/env python3
"""
AVIF转换模块UI实现
"""

import os
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QProgressBar, QTextEdit, QGroupBox, QApplication)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap, QImage
from utils.image_utils import ImageUtils


class AVIFConverterWorkspace(QWidget):
    """
    AVIF转换模块工作区UI
    """

    def __init__(self, module):
        super().__init__()
        self.module = module
        self.init_ui()
        self.connect_signals()
        
    def init_ui(self):
        """初始化UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)
        
        # 进度和统计信息区域
        progress_frame = QWidget()
        progress_layout = QHBoxLayout(progress_frame)
        progress_layout.setContentsMargins(0, 0, 0, 0)
        self.progress_label = QLabel("转换尚未开始")
        self.progress_label.setStyleSheet("color: white;")
        progress_layout.addWidget(self.progress_label)
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                border: 1px solid #454545;
                border-radius: 4px;
                text-align: center;
                background-color: #2B2B2B;
                color: white;
            }
            QProgressBar::chunk {
                background-color: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                                         stop:0 #FF8C00, stop:0.5 #FF6B35, stop:1 #FF8C00);
                border-radius: 3px;
            }
        """)
        self.progress_bar.setValue(0)
        progress_layout.addWidget(self.progress_bar)
        
        layout.addWidget(progress_frame)
        
        # 统计信息
        stats_frame = QWidget()
        stats_layout = QHBoxLayout(stats_frame)
        stats_layout.setContentsMargins(0, 0, 0, 0)
        self.stats_label = QLabel("文件: 0 | 已转换: 0 | 失败: 0")
        self.stats_label.setStyleSheet("color: white;")
        stats_layout.addWidget(self.stats_label)
        
        layout.addWidget(stats_frame)
        
        # 当前转换图片预览区域
        preview_frame = QGroupBox("当前转换")
        preview_frame.setStyleSheet("QGroupBox { background-color: #1B1B1B; color: white; border: 1px solid #353535; font-weight: bold; }")
        preview_layout = QVBoxLayout(preview_frame)
        preview_layout.setContentsMargins(10, 20, 10, 10)
        
        # 创建左右子框架
        preview_content_frame = QWidget()
        preview_content_layout = QHBoxLayout(preview_content_frame)
        preview_content_layout.setContentsMargins(0, 0, 0, 0)
        
        # 左侧: 源图片预览
        source_preview_frame = QGroupBox("源图片")
        source_preview_frame.setStyleSheet("QGroupBox { background-color: #1B1B1B; color: white; border: 1px solid #353535; font-weight: bold; }")
        source_preview_layout = QVBoxLayout(source_preview_frame)
        source_preview_layout.setContentsMargins(10, 20, 10, 10)
        
        self.source_preview_label = QLabel("无图片")
        self.source_preview_label.setStyleSheet("color: #6c757d;")
        self.source_preview_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        source_preview_layout.addWidget(self.source_preview_label)
        
        # 右侧: 目标信息
        target_preview_frame = QGroupBox("目标信息")
        target_preview_frame.setStyleSheet("QGroupBox { background-color: #1B1B1B; color: white; border: 1px solid #353535; font-weight: bold; }")
        target_preview_layout = QVBoxLayout(target_preview_frame)
        target_preview_layout.setContentsMargins(10, 20, 10, 10)
        
        self.target_info_label = QLabel("AVIF输出")
        self.target_info_label.setStyleSheet("color: #6c757d;")
        self.target_info_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        target_preview_layout.addWidget(self.target_info_label)
        
        preview_content_layout.addWidget(source_preview_frame)
        preview_content_layout.addWidget(target_preview_frame)
        
        preview_layout.addWidget(preview_content_frame)
        
        layout.addWidget(preview_frame)
        
        # 压缩比率显示区域
        self.compression_frame = QGroupBox("压缩比率")
        self.compression_frame.setStyleSheet("QGroupBox { background-color: #1B1B1B; color: white; border: 1px solid #353535; font-weight: bold; }")
        compression_layout = QVBoxLayout(self.compression_frame)
        compression_layout.setContentsMargins(10, 20, 10, 10)
        
        # 压缩比率信息
        self.compression_info_label = QLabel("无转换数据")
        self.compression_info_label.setStyleSheet("color: #6c757d;")
        self.compression_info_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        compression_layout.addWidget(self.compression_info_label)
        
        layout.addWidget(self.compression_frame)
        
        # 日志区域
        log_frame = QGroupBox("转换日志")
        log_frame.setStyleSheet("QGroupBox { background-color: #1B1B1B; color: white; border: 1px solid #353535; font-weight: bold; }")
        log_layout = QVBoxLayout(log_frame)
        log_layout.setContentsMargins(10, 20, 10, 10)
        
        self.log_text = QTextEdit()
        self.log_text.setStyleSheet("""
            QTextEdit {
                background-color: #1B1B1B;
                color: white;
                border: 1px solid #6c757d;
                border-radius: 4px;
                min-height: 150px;
            }
        """)
        self.log_text.setReadOnly(True)
        log_layout.addWidget(self.log_text)
        
        layout.addWidget(log_frame)
        
    def connect_signals(self):
        """连接信号"""
        if self.module:
            self.module.progress_updated.connect(self.update_progress)
            self.module.log_message.connect(self.add_log_message)
            self.module.execution_finished.connect(self.on_execution_finished)
            
    def update_progress(self, value: float, message: str):
        """更新进度"""
        self.progress_bar.setValue(int(value))
        self.progress_label.setText(message)
        
    def add_log_message(self, message: str, level: str):
        """添加日志消息"""
        formatted_message = f"[{level.upper()}] {message}"
        self.log_text.append(formatted_message)
        
    def on_execution_finished(self, result_data: dict):
        """处理执行完成事件"""
        # 启用开始按钮，禁用停止按钮
        if hasattr(self.module, 'settings_ui') and self.module.settings_ui:
            # 查找设置UI中的按钮并更新状态
            pass  # 按钮状态会在模块中处理
            
        # 更新统计信息
        total_files = result_data.get('total_files', 0)
        converted_files = result_data.get('converted_files', 0)
        failed_files = result_data.get('failed_files', 0)
        self.stats_label.setText(f"文件: {total_files} | 已转换: {converted_files} | 失败: {failed_files}")
        
    def clear_preview(self):
        """清除预览区域"""
        self.source_preview_label.setText("无图片")
        self.target_info_label.setText("AVIF输出")
        self.compression_info_label.setText("无转换数据")
        
    def show_preview(self, file_path: str):
        """显示预览图片"""
        try:
            # 加载并显示图片
            pixmap = QPixmap(file_path)
            
            # 调整图片大小以适应预览区域
            max_size = 200
            if pixmap.width() > pixmap.height():
                if pixmap.width() > max_size:
                    pixmap = pixmap.scaledToWidth(max_size, Qt.TransformationMode.SmoothTransformation)
            else:
                if pixmap.height() > max_size:
                    pixmap = pixmap.scaledToHeight(max_size, Qt.TransformationMode.SmoothTransformation)
            
            # 更新源图片预览标签
            self.source_preview_label.setPixmap(pixmap)
            self.source_preview_label.setText("")
            
            # 更新目标信息
            file_size = os.path.getsize(file_path)
            file_size_mb = file_size / (1024 * 1024)
            file_name = os.path.basename(file_path)
            file_ext = os.path.splitext(file_name)[1].upper()
            
            info_text = f"文件: {file_name}\n大小: {file_size_mb:.2f} MB\n格式: {file_ext}\n\n目标: AVIF"
            self.target_info_label.setText(info_text)
            
        except Exception as e:
            self.source_preview_label.setText("无法预览图片")
            self.target_info_label.setText(f"加载预览出错:\n{str(e)}")
            
    def show_compression_ratio(self, source_path: str, target_path: str):
        """显示压缩比率"""
        try:
            # 获取源文件和目标文件大小
            source_size = os.path.getsize(source_path)
            target_size = os.path.getsize(target_path)
            
            # 计算压缩比率
            if source_size > 0:
                compression_ratio = (1 - target_size / source_size) * 100
                size_reduction = source_size - target_size
                
                # 格式化大小显示
                def format_size(size):
                    if size < 1024:
                        return f"{size} B"
                    elif size < 1024 * 1024:
                        return f"{size / 1024:.1f} KB"
                    else:
                        return f"{size / (1024 * 1024):.1f} MB"
                
                source_size_str = format_size(source_size)
                target_size_str = format_size(target_size)
                reduction_str = format_size(size_reduction)
                
                # 更新压缩比率信息标签
                info_text = f"源文件: {source_size_str} → 目标: {target_size_str}\n"
                info_text += f"大小减少: {reduction_str} ({compression_ratio:.1f}% 更小)"
                self.compression_info_label.setText(info_text)
                
            else:
                self.compression_info_label.setText("源文件大小为0")
                
        except Exception as e:
            self.compression_info_label.setText(f"计算压缩比率出错: {str(e)}")