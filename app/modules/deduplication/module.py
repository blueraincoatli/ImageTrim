#!/usr/bin/env python3
"""
图片去重模块
"""

from core.base_module import BaseFunctionModule
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
                             QProgressBar, QFileDialog, QLineEdit, QCheckBox, QSpinBox, 
                             QGroupBox, QListWidget)
from PyQt6.QtCore import Qt
from utils.image_utils import ImageUtils
import os


class DeduplicationModule(BaseFunctionModule):
    """
    图片去重模块
    """

    def __init__(self):
        super().__init__(
            name="deduplication",
            display_name="🔍 图片去重",
            description="查找并处理重复或相似的图片",
            icon="🔍"
        )
        self.scan_paths = []
        self.similarity_threshold = 95
        self.settings_ui = None
        self.workspace_ui = None

    def create_settings_ui(self):
        """
        创建设置UI面板

        Returns:
            QWidget: 设置UI面板
        """
        if self.settings_ui:
            return self.settings_ui
            
        widget = QWidget()
        self.settings_ui = widget
        layout = QVBoxLayout(widget)
        
        # 扫描路径设置
        path_group = QGroupBox("📁 扫描路径")
        path_layout = QVBoxLayout(path_group)
        
        # 路径列表
        self.path_list = QListWidget()
        self.path_list.setMaximumHeight(100)
        path_layout.addWidget(self.path_list)
        
        # 路径操作按钮
        path_btn_layout = QHBoxLayout()
        add_path_btn = QPushButton("添加路径...")
        add_path_btn.clicked.connect(self.add_path)
        remove_path_btn = QPushButton("移除选中")
        remove_path_btn.clicked.connect(self.remove_path)
        clear_paths_btn = QPushButton("清空路径")
        clear_paths_btn.clicked.connect(self.clear_paths)
        path_btn_layout.addWidget(add_path_btn)
        path_btn_layout.addWidget(remove_path_btn)
        path_btn_layout.addWidget(clear_paths_btn)
        path_layout.addLayout(path_btn_layout)
        
        self.subdir_checkbox = QCheckBox("包含子目录")
        self.subdir_checkbox.setChecked(True)
        
        path_layout.addWidget(self.subdir_checkbox)
        
        # 相似度设置
        similarity_group = QGroupBox("⚙️ 相似度设置")
        similarity_layout = QVBoxLayout(similarity_group)
        
        similarity_layout.addWidget(QLabel("相似度阈值:"))
        self.similarity_spinbox = QSpinBox()
        self.similarity_spinbox.setRange(1, 100)
        self.similarity_spinbox.setValue(self.similarity_threshold)
        self.similarity_spinbox.setSuffix(" %")
        similarity_layout.addWidget(self.similarity_spinbox)
        
        # 操作按钮
        button_layout = QHBoxLayout()
        self.scan_btn = QPushButton("🔍 开始扫描")
        self.scan_btn.clicked.connect(self.start_scan)
        self.stop_btn = QPushButton("⏹️ 停止")
        self.stop_btn.clicked.connect(self.stop_execution)
        self.stop_btn.setEnabled(False)
        button_layout.addWidget(self.scan_btn)
        button_layout.addWidget(self.stop_btn)
        
        # 添加到主布局
        layout.addWidget(path_group)
        layout.addWidget(similarity_group)
        layout.addLayout(button_layout)
        layout.addStretch()
        
        return widget

    def create_workspace_ui(self):
        """
        创建工作区UI面板

        Returns:
            QWidget: 工作区UI面板
        """
        # 工作区UI由WorkspacePanel特殊处理，这里返回None
        return None

    def add_path(self):
        """添加扫描路径"""
        # 直接选择目录，不使用文件选择对话框
        path = QFileDialog.getExistingDirectory(None, "选择扫描目录")
        if path and path not in self.scan_paths:
            self.scan_paths.append(path)
            self.path_list.addItem(path)

    def remove_path(self):
        """移除选中的路径"""
        for item in self.path_list.selectedItems():
            row = self.path_list.row(item)
            self.path_list.takeItem(row)
            if row < len(self.scan_paths):
                del self.scan_paths[row]

    def clear_paths(self):
        """清空所有路径"""
        self.path_list.clear()
        self.scan_paths.clear()

    def start_scan(self):
        """开始扫描"""
        self.similarity_threshold = self.similarity_spinbox.value()
        
        if not self.scan_paths:
            self.log_message.emit("请添加至少一个扫描路径", "warning")
            return
            
        self.scan_btn.setEnabled(False)
        self.stop_btn.setEnabled(True)
        
        # 执行扫描（这里应该在后台线程中进行）
        self.execute({
            'paths': self.scan_paths,
            'threshold': self.similarity_threshold,
            'include_subdirs': self.subdir_checkbox.isChecked()
        })

    def execute(self, params: dict):
        """
        执行去重操作

        Args:
            params: 执行参数
        """
        try:
            # 收集所有图片文件
            self.progress_updated.emit(0, "收集图片文件...")
            self.log_message.emit(f"开始扫描 {len(params['paths'])} 个路径", "info")
            
            all_image_files = []
            for path in params['paths']:
                if os.path.exists(path):
                    image_files = ImageUtils.get_image_files(path, params['include_subdirs'])
                    all_image_files.extend(image_files)
                    self.log_message.emit(f"从 {path} 找到 {len(image_files)} 个图片文件", "info")
                else:
                    self.log_message.emit(f"路径不存在: {path}", "error")
            
            total_files = len(all_image_files)
            if total_files == 0:
                self.log_message.emit("未找到任何图片文件", "warning")
                self.progress_updated.emit(100, "扫描完成")
                self.scan_btn.setEnabled(True)
                self.stop_btn.setEnabled(False)
                return
            
            self.log_message.emit(f"总共找到 {total_files} 个图片文件", "info")
            
            # 计算哈希值并查找重复项
            self.progress_updated.emit(10, "计算图片哈希值...")
            duplicates = ImageUtils.find_duplicates(
                all_image_files, 
                params['threshold'] / 100.0
            )
            
            # 报告结果
            self.progress_updated.emit(100, "扫描完成")
            if duplicates:
                total_groups = len(duplicates)
                total_duplicates = sum(len(files) for files in duplicates.values())
                self.log_message.emit(f"找到 {total_groups} 组重复图片，共 {total_duplicates} 个重复文件", "info")
                
                # 发送结果到工作区
                result_data = {
                    'duplicates': duplicates,
                    'total_files': total_files,
                    'total_groups': total_groups,
                    'total_duplicates': total_duplicates
                }
                self.execution_finished.emit(result_data)
            else:
                self.log_message.emit("未找到重复图片", "info")
                self.execution_finished.emit({
                    'duplicates': {},
                    'total_files': total_files,
                    'total_groups': 0,
                    'total_duplicates': 0
                })
                
        except Exception as e:
            self.log_message.emit(f"扫描过程中出错: {str(e)}", "error")
            self.progress_updated.emit(100, "扫描出错")
            
        self.scan_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)

    def stop_execution(self):
        """
        停止执行
        """
        self.log_message.emit("用户停止了扫描", "info")
        self.scan_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)
        self.progress_updated.emit(0, "已停止")