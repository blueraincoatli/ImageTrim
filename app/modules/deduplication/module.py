#!/usr/bin/env python3
"""
图片去重模块
"""

import threading
from core.base_module import BaseFunctionModule
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
                             QProgressBar, QFileDialog, QLineEdit, QCheckBox, QSpinBox, 
                             QGroupBox, QListWidget, QStackedWidget)
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QObject
from utils.image_utils import ImageUtils
import os


class DeduplicationWorker(QObject):
    """
    图片去重扫描工作线程
    """
    
    # 定义信号
    progress_updated = pyqtSignal(float, str)
    log_message = pyqtSignal(str, str)
    finished = pyqtSignal(dict)
    
    def __init__(self):
        super().__init__()
        self.is_running = False
        
    def stop(self):
        """停止扫描"""
        self.is_running = False
        
    def scan_duplicates(self, params):
        """执行扫描操作"""
        self.is_running = True
        
        try:
            # 收集所有图片文件
            self.progress_updated.emit(0, "收集图片文件...")
            self.log_message.emit(f"开始扫描 {len(params['paths'])} 个路径", "info")

            all_image_files = []
            total_files_found = 0
            total_paths = len(params['paths'])

            # 收集文件，同时更新进度
            for path_idx, path in enumerate(params['paths']):
                if not self.is_running:
                    break

                if os.path.exists(path):
                    # 创建进度回调函数，实时更新文件发现进度
                    def file_found_callback(count):
                        """每发现一个文件时调用"""
                        # 计算当前路径的基础进度
                        base_progress = path_idx / total_paths * 30
                        # 添加当前路径内的进度（估算，每10个文件更新一次）
                        if count % 10 == 0 or count < 10:
                            current_progress = base_progress
                            self.progress_updated.emit(
                                current_progress,
                                f"收集图片文件... 路径 {path_idx+1}/{total_paths}, 已找到 {len(all_image_files) + count} 个文件"
                            )

                    image_files = ImageUtils.get_image_files(
                        path,
                        params['include_subdirs'],
                        progress_callback=file_found_callback
                    )
                    all_image_files.extend(image_files)
                    total_files_found += len(image_files)

                    # 更新路径完成进度
                    progress = (path_idx + 1) / total_paths * 30  # 收集文件占30%进度
                    self.progress_updated.emit(
                        progress,
                        f"收集图片文件... {path_idx+1}/{total_paths} 路径, 已找到 {total_files_found} 个文件"
                    )
                    self.log_message.emit(f"从 {path} 找到 {len(image_files)} 个图片文件", "info")
                else:
                    self.log_message.emit(f"路径不存在: {path}", "error")
            
            if not self.is_running:
                return
                
            total_files = len(all_image_files)
            if total_files == 0:
                self.log_message.emit("未找到任何图片文件", "warning")
                self.progress_updated.emit(100, "扫描完成")
                self.finished.emit({})
                return
            
            self.log_message.emit(f"总共找到 {total_files} 个图片文件", "info")

            # 计算哈希值并查找重复项 - 传递进度回调和停止检查
            def progress_callback(progress, message):
                """进度回调函数"""
                self.progress_updated.emit(progress, message)

            def should_stop():
                """检查是否需要停止"""
                return not self.is_running

            duplicates = ImageUtils.find_duplicates(
                all_image_files,
                params['threshold'] / 100.0,
                progress_callback=progress_callback,
                should_stop=should_stop
            )
            
            if not self.is_running:
                return
            
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
                self.finished.emit(result_data)
            else:
                self.log_message.emit("未找到重复图片", "info")
                self.finished.emit({
                    'duplicates': {},
                    'total_files': total_files,
                    'total_groups': 0,
                    'total_duplicates': 0
                })
                
        except Exception as e:
            self.log_message.emit(f"扫描过程中出错: {str(e)}", "error")
            self.progress_updated.emit(100, "扫描出错")
            self.finished.emit({})


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
        self.scan_thread = None
        self.scan_worker = None

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
        self.subdir_checkbox.setStyleSheet("""
            QCheckBox {
                color: white;
                spacing: 8px;
            }
            QCheckBox::indicator {
                width: 18px;
                height: 18px;
                border-radius: 3px;
                border: 2px solid #4C4C4C;
                background-color: #2d2d30;
            }
            QCheckBox::indicator:hover {
                border-color: #FF8C00;
                background-color: #3A3A3A;
            }
            QCheckBox::indicator:checked {
                background-color: #FF8C00;
                border-color: #FF8C00;
                image: url(data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMTIiIGhlaWdodD0iOSIgdmlld0JveD0iMCAwIDEyIDkiIGZpbGw9Im5vbmUiIHhtbG5zPSJodHRwOi8vd3d3LnczLm9yZy8yMDAwL3N2ZyI+PHBhdGggZD0iTTEgNEw0LjUgNy41TDExIDEiIHN0cm9rZT0id2hpdGUiIHN0cm9rZS13aWR0aD0iMiIgc3Ryb2tlLWxpbmVjYXA9InJvdW5kIiBzdHJva2UtbGluZWpvaW49InJvdW5kIi8+PC9zdmc+);
            }
            QCheckBox::indicator:checked:hover {
                background-color: #FFA500;
                border-color: #FFA500;
            }
        """)

        path_layout.addWidget(self.subdir_checkbox)
        
        # 相似度设置
        similarity_group = QGroupBox("⚙️ 相似度设置")
        similarity_layout = QVBoxLayout(similarity_group)
        
        similarity_layout.addWidget(QLabel("相似度阈值:"))
        self.similarity_spinbox = QSpinBox()
        self.similarity_spinbox.setRange(1, 100)
        self.similarity_spinbox.setValue(self.similarity_threshold)
        self.similarity_spinbox.setSuffix(" %")
        self.similarity_spinbox.setStyleSheet("""
            QSpinBox {
                background-color: #2d2d30;
                border: 1px solid #4C4C4C;
                border-radius: 4px;
                padding: 4px 8px;
                color: white;
                min-width: 80px;
            }
            QSpinBox:hover {
                border-color: #FF8C00;
            }
            QSpinBox:focus {
                border-color: #FF8C00;
                outline: none;
            }
            QSpinBox::up-button {
                subcontrol-origin: border;
                subcontrol-position: top right;
                width: 20px;
                border-left: 1px solid #4C4C4C;
                border-top-right-radius: 4px;
                background-color: #3A3A3A;
            }
            QSpinBox::up-button:hover {
                background-color: #4A4A4A;
            }
            QSpinBox::up-button:pressed {
                background-color: #FF8C00;
            }
            QSpinBox::up-arrow {
                image: none;
                border-left: 4px solid transparent;
                border-right: 4px solid transparent;
                border-bottom: 5px solid white;
                width: 0;
                height: 0;
                margin: 0px 2px;
            }
            QSpinBox::down-button {
                subcontrol-origin: border;
                subcontrol-position: bottom right;
                width: 20px;
                border-left: 1px solid #4C4C4C;
                border-bottom-right-radius: 4px;
                background-color: #3A3A3A;
            }
            QSpinBox::down-button:hover {
                background-color: #4A4A4A;
            }
            QSpinBox::down-button:pressed {
                background-color: #FF8C00;
            }
            QSpinBox::down-arrow {
                image: none;
                border-left: 4px solid transparent;
                border-right: 4px solid transparent;
                border-top: 5px solid white;
                width: 0;
                height: 0;
                margin: 0px 2px;
            }
        """)
        similarity_layout.addWidget(self.similarity_spinbox)
        
        # 操作按钮 - 开始/停止切换按钮
        button_layout = QHBoxLayout()
        self.scan_stop_btn = QPushButton("🔍 开始扫描")
        self.scan_stop_btn.clicked.connect(self.toggle_scan)
        self.scan_stop_btn.setEnabled(False)  # 初始状态禁用，直到有路径
        self.is_scanning = False  # 扫描状态
        button_layout.addWidget(self.scan_stop_btn)
        
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
        # 延迟导入结果面板和拖拽区域，避免循环导入
        from modules.deduplication.results_panel import DeduplicationResultsPanel
        from modules.deduplication.drag_drop_area import DragDropArea
        
        if self.workspace_ui is None:
            # 创建一个堆叠部件，用于在拖拽区域和结果面板之间切换
            from PyQt6.QtWidgets import QStackedWidget, QVBoxLayout, QWidget
            
            # 创建主容器
            container = QWidget()
            layout = QVBoxLayout(container)
            layout.setContentsMargins(0, 0, 0, 0)
            
            # 创建堆叠部件
            self.workspace_stacked_widget = QStackedWidget()
            
            # 创建拖拽区域
            self.drag_drop_area = DragDropArea()
            self.drag_drop_area.paths_dropped.connect(self.on_paths_dropped)
            self.workspace_stacked_widget.addWidget(self.drag_drop_area)
            
            # 创建结果面板
            self.results_panel = DeduplicationResultsPanel(self)
            self.workspace_stacked_widget.addWidget(self.results_panel)
            
            # 默认显示拖拽区域（索引0）
            self.workspace_stacked_widget.setCurrentIndex(0)
            
            layout.addWidget(self.workspace_stacked_widget)
            self.workspace_ui = container
            
        return self.workspace_ui

    def add_path(self):
        """添加扫描路径"""
        # 直接选择目录，不使用文件选择对话框
        path = QFileDialog.getExistingDirectory(None, "选择扫描目录")
        if path and path not in self.scan_paths:
            self.scan_paths.append(path)
            self.path_list.addItem(path)
            
            # 同步到拖拽区域
            if hasattr(self, "drag_drop_area"):
                self.drag_drop_area.set_paths(self.scan_paths)

    def remove_path(self):
        """移除选中的路径"""
        for item in self.path_list.selectedItems():
            row = self.path_list.row(item)
            self.path_list.takeItem(row)
            if row < len(self.scan_paths):
                del self.scan_paths[row]
                
        # 同步到拖拽区域
        if hasattr(self, "drag_drop_area"):
            self.drag_drop_area.set_paths(self.scan_paths)

    def clear_paths(self):
        """清空所有路径"""
        self.path_list.clear()
        self.scan_paths.clear()
        
        # 同步到拖拽区域
        if hasattr(self, "drag_drop_area"):
            self.drag_drop_area.set_paths(self.scan_paths)

    def toggle_scan(self):
        """切换扫描状态"""
        if not self.is_scanning:
            self.start_scan()
        else:
            self.stop_execution()
    
    def start_scan(self):
        """开始扫描"""
        self.similarity_threshold = self.similarity_spinbox.value()
        
        if not self.scan_paths:
            self.log_message.emit("请添加至少一个扫描路径", "warning")
            return
            
        self.is_scanning = True
        self.scan_stop_btn.setText("⏹️ 停止扫描")
        self.scan_stop_btn.setStyleSheet("""
            QPushButton {
                background-color: #3A3A3A;
                color: white;
                border: 1px solid #4C4C4C;
                padding: 6px 12px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #4A4A4A;
                color: #FF8C00;
            }
            QPushButton:pressed {
                background-color: #333333;
                color: #FF8C00;
            }
        """)
        
        # 切换到结果面板
        if hasattr(self, "workspace_stacked_widget"):
            self.workspace_stacked_widget.setCurrentIndex(1)
        
        # 创建工作线程
        self.scan_thread = QThread()
        self.scan_worker = DeduplicationWorker()
        self.scan_worker.moveToThread(self.scan_thread)
        
        # 连接信号
        self.scan_worker.progress_updated.connect(self.progress_updated.emit)
        self.scan_worker.log_message.connect(self.log_message.emit)
        self.scan_worker.finished.connect(self.on_scan_finished)
        self.scan_thread.started.connect(lambda: self.scan_worker.scan_duplicates({
            'paths': self.scan_paths,
            'threshold': self.similarity_threshold,
            'include_subdirs': self.subdir_checkbox.isChecked()
        }))
        
        # 启动线程
        self.scan_thread.start()

    def execute(self, params: dict):
        """
        执行去重操作（现在由工作线程处理）

        Args:
            params: 执行参数
        """
        # 这个方法现在由工作线程处理
        pass

    def stop_execution(self):
        """
        停止执行
        """
        self.log_message.emit("用户停止了扫描", "info")
        
        # 停止工作线程
        if self.scan_worker:
            self.scan_worker.stop()
        
        if self.scan_thread and self.scan_thread.isRunning():
            self.scan_thread.quit()
            self.scan_thread.wait(3000)  # 等待3秒
        
        self.is_scanning = False
        self.scan_stop_btn.setText("🔍 开始扫描")
        self.scan_stop_btn.setStyleSheet("""
            QPushButton {
                background-color: #3A3A3A;
                color: white;
                border: 1px solid #4C4C4C;
                padding: 6px 12px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #4A4A4A;
                color: #FF8C00;
            }
            QPushButton:pressed {
                background-color: #333333;
                color: #FF8C00;
            }
            QPushButton:disabled {
                background-color: #555555;
                color: #A0A0A0;
            }
        """)
        self.progress_updated.emit(0, "已停止")
        
        # 切换回拖拽区域
        if hasattr(self, "workspace_stacked_widget"):
            self.workspace_stacked_widget.setCurrentIndex(0)
    
    def on_scan_finished(self, result_data):
        """
        扫描完成处理
        """
        self.is_scanning = False
        self.scan_stop_btn.setText("🔍 开始扫描")
        self.scan_stop_btn.setStyleSheet("""
            QPushButton {
                background-color: #3A3A3A;
                color: white;
                border: 1px solid #4C4C4C;
                padding: 6px 12px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #4A4A4A;
                color: #FF8C00;
            }
            QPushButton:pressed {
                background-color: #333333;
                color: #FF8C00;
            }
            QPushButton:disabled {
                background-color: #555555;
                color: #A0A0A0;
            }
        """)
        
        # 清理线程资源
        if self.scan_thread:
            self.scan_thread.quit()
            self.scan_thread.wait()
            self.scan_thread = None
            self.scan_worker = None
        
        # 发送结果到工作区
        self.execution_finished.emit(result_data)
        
        # 如果没有找到重复图片，切换回拖拽区域
        if not result_data.get('duplicates'):
            if hasattr(self, "workspace_stacked_widget"):
                self.workspace_stacked_widget.setCurrentIndex(0)
            
    def on_paths_dropped(self, paths):
        """
        处理拖拽进来的路径
        
        Args:
            paths: 拖拽进来的路径列表
        """
        # 更新扫描路径
        new_path_count = 0
        for path in paths:
            if path not in self.scan_paths:
                self.scan_paths.append(path)
                self.path_list.addItem(path)
                new_path_count += 1
        
        if new_path_count > 0:
            self.log_message.emit(f"已自动添加 {new_path_count} 个路径到扫描列表", "info")
            # 启用扫描按钮
            self.scan_stop_btn.setEnabled(True)