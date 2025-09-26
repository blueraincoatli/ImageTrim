"""
PyQt6 AVIF转换功能模块
"""

import os
import threading
from typing import Dict, Any, Optional
from datetime import datetime

from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
                             QLabel, QPushButton, QCheckBox, QSlider, QSpinBox,
                             QDoubleSpinBox, QComboBox, QLineEdit, QTextEdit,
                             QProgressBar, QScrollArea, QFrame, QListWidget,
                             QFileDialog, QMessageBox, QGroupBox)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap, QFont

try:
    from PIL import Image, ImageQt
except ImportError as e:
    print(f"错误: 必要的库未安装。{e}")
    exit()

from modules.base_function_module import BaseFunctionModule


class AVIFConverterModule(BaseFunctionModule):
    """PyQt6版本AVIF格式转换功能模块"""
    
    def __init__(self):
        super().__init__(
            name="avif_converter",
            display_name="AVIF转换",
            description="将图片转换为AVIF格式以节省存储空间",
            icon="🔄"
        )
        self.convert_thread: Optional[threading.Thread] = None
        self.is_running = False
        self.workspace_widget: Optional[QWidget] = None
        self.settings_widget: Optional[QWidget] = None
        
        # UI组件引用
        self.source_entry: Optional[QLineEdit] = None
        self.target_entry: Optional[QLineEdit] = None
        self.quality_scale: Optional[QSlider] = None
        self.quality_value_label: Optional[QLabel] = None
        self.subdirs_check: Optional[QCheckBox] = None
        self.start_btn: Optional[QPushButton] = None
        self.stop_btn: Optional[QPushButton] = None
        self.progress_bar: Optional[QProgressBar] = None
        self.progress_label: Optional[QLabel] = None
        self.stats_label: Optional[QLabel] = None
        self.log_text: Optional[QTextEdit] = None
        
        # 参数变量
        self.quality = 85
        self.include_subdirs = True

    def create_settings_ui(self) -> QWidget:
        """创建设置UI面板（中栏）"""
        if self.settings_widget:
            return self.settings_widget
            
        self.settings_widget = QWidget()
        settings_layout = QVBoxLayout(self.settings_widget)
        settings_layout.setContentsMargins(10, 10, 10, 10)

        # 1. 源路径和目标路径
        source_frame = QGroupBox("源路径")
        source_frame.setStyleSheet("QGroupBox { background-color: #1B1B1B; color: white; border: 1px solid #353535; font-weight: bold; }")
        source_layout = QHBoxLayout(source_frame)
        source_layout.setContentsMargins(10, 20, 10, 10)

        self.source_entry = QLineEdit()
        self.source_entry.setStyleSheet("""
            QLineEdit {
                background-color: #4B4B4B;
                color: white;
                border: 1px solid #6c757d;
                padding: 5px;
                border-radius: 4px;
            }
        """)
        source_layout.addWidget(self.source_entry)

        source_browse_btn = QPushButton("浏览")
        source_browse_btn.setStyleSheet("""
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
        source_browse_btn.clicked.connect(self._browse_source_folder)
        source_layout.addWidget(source_browse_btn)

        target_frame = QGroupBox("目标路径")
        target_frame.setStyleSheet("QGroupBox { background-color: #1B1B1B; color: white; border: 1px solid #353535; font-weight: bold; }")
        target_layout = QHBoxLayout(target_frame)
        target_layout.setContentsMargins(10, 20, 10, 10)

        self.target_entry = QLineEdit()
        self.target_entry.setStyleSheet("""
            QLineEdit {
                background-color: #4B4B4B;
                color: white;
                border: 1px solid #6c757d;
                padding: 5px;
                border-radius: 4px;
            }
        """)
        target_layout.addWidget(self.target_entry)

        target_browse_btn = QPushButton("浏览")
        target_browse_btn.setStyleSheet("""
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
        target_browse_btn.clicked.connect(self._browse_target_folder)
        target_layout.addWidget(target_browse_btn)

        # 2. 转换设置
        options_frame = QGroupBox("转换设置")
        options_frame.setStyleSheet("QGroupBox { background-color: #1B1B1B; color: white; border: 1px solid #353535; font-weight: bold; }")
        options_layout = QVBoxLayout(options_frame)
        options_layout.setContentsMargins(10, 20, 10, 10)

        quality_frame = QWidget()
        quality_layout = QHBoxLayout(quality_frame)
        quality_layout.setContentsMargins(0, 0, 0, 0)
        quality_label = QLabel("质量:")
        quality_label.setStyleSheet("color: white;")
        quality_layout.addWidget(quality_label)
        
        self.quality_scale = QSlider(Qt.Orientation.Horizontal)
        self.quality_scale.setMinimum(1)
        self.quality_scale.setMaximum(100)
        self.quality_scale.setValue(85)
        self.quality_scale.setStyleSheet("""
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
        self.quality_scale.valueChanged.connect(self._on_quality_changed)
        quality_layout.addWidget(self.quality_scale)
        
        self.quality_value_label = QLabel("85%")
        self.quality_value_label.setStyleSheet("color: white;")
        self.quality_value_label.setFixedWidth(40)
        quality_layout.addWidget(self.quality_value_label)
        
        options_layout.addWidget(quality_frame)

        self.subdirs_check = QCheckBox("包含子目录")
        self.subdirs_check.setChecked(True)
        self.subdirs_check.setStyleSheet("QCheckBox { color: white; }")
        self.subdirs_check.stateChanged.connect(self._on_subdirs_changed)
        options_layout.addWidget(self.subdirs_check)

        # 3. 操作控制
        action_frame = QGroupBox("操作控制")
        action_frame.setStyleSheet("QGroupBox { background-color: #1B1B1B; color: white; border: 1px solid #353535; font-weight: bold; }")
        action_layout = QVBoxLayout(action_frame)
        action_layout.setContentsMargins(10, 20, 10, 10)

        button_frame = QWidget()
        button_layout = QHBoxLayout(button_frame)
        button_layout.setContentsMargins(0, 0, 0, 0)
        
        self.start_btn = QPushButton("▶️ 开始转换")
        self.start_btn.setStyleSheet("""
            QPushButton {
                background-color: #28a745;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #218838;
            }
            QPushButton:disabled {
                background-color: #6c757d;
            }
        """)
        self.start_btn.clicked.connect(self._start_conversion)
        button_layout.addWidget(self.start_btn)

        self.stop_btn = QPushButton("⏹️ 停止")
        self.stop_btn.setStyleSheet("""
            QPushButton {
                background-color: #dc3545;
                color: white;
                border: none;
                padding: 10px 20px;
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
        self.stop_btn.clicked.connect(self.stop_execution)
        self.stop_btn.setEnabled(False)
        button_layout.addWidget(self.stop_btn)
        
        action_layout.addWidget(button_frame)
        
        # 添加所有组件到设置布局
        settings_layout.addWidget(source_frame)
        settings_layout.addWidget(target_frame)
        settings_layout.addWidget(options_frame)
        settings_layout.addWidget(action_frame)
        settings_layout.addStretch()

        return self.settings_widget

    def create_workspace_ui(self) -> QWidget:
        """创建工作区UI面板（右栏）"""
        if self.workspace_widget:
            return self.workspace_widget
            
        self.workspace_widget = QWidget()
        workspace_layout = QVBoxLayout(self.workspace_widget)
        workspace_layout.setContentsMargins(10, 10, 10, 10)
        
        # 进度和统计区域
        progress_frame = QWidget()
        progress_layout = QHBoxLayout(progress_frame)
        progress_layout.setContentsMargins(0, 0, 0, 0)
        self.progress_label = QLabel("转换尚未开始。")
        self.progress_label.setStyleSheet("color: white;")
        progress_layout.addWidget(self.progress_label)
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                border: 1px solid #6c757d;
                border-radius: 4px;
                text-align: center;
                background-color: #2B2B2B;
            }
            QProgressBar::chunk {
                background-color: #28a745;
            }
        """)
        self.progress_bar.setValue(0)
        progress_layout.addWidget(self.progress_bar)
        
        workspace_layout.addWidget(progress_frame)
        
        # 统计信息
        stats_frame = QWidget()
        stats_layout = QHBoxLayout(stats_frame)
        stats_layout.setContentsMargins(0, 0, 0, 0)
        self.stats_label = QLabel("文件: 0 | 已转换: 0 | 失败: 0")
        self.stats_label.setStyleSheet("color: white;")
        stats_layout.addWidget(self.stats_label)
        
        workspace_layout.addWidget(stats_frame)
        
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
        
        workspace_layout.addWidget(log_frame)
        
        return self.workspace_widget

    def _on_quality_changed(self, value: int):
        """处理质量滑块变化"""
        self.quality_value_label.setText(f"{value}%")
        self.quality = value

    def _on_subdirs_changed(self, state: int):
        """处理包含子目录选项变化"""
        self.include_subdirs = state == Qt.CheckState.Checked.value

    def _browse_source_folder(self):
        """浏览源文件夹"""
        path = QFileDialog.getExistingDirectory(None, "选择源目录")
        if path:
            self.source_entry.setText(path)

    def _browse_target_folder(self):
        """浏览目标文件夹"""
        path = QFileDialog.getExistingDirectory(None, "选择目标目录")
        if path:
            self.target_entry.setText(path)

    def _start_conversion(self):
        """开始转换"""
        source_path = self.source_entry.text()
        target_path = self.target_entry.text()
        
        if not source_path or not os.path.isdir(source_path):
            QMessageBox.critical(None, "无效路径", "请输入有效的源文件夹路径。")
            return
            
        if not target_path:
            QMessageBox.critical(None, "无效路径", "请输入有效的目标文件夹路径。")
            return

        params = {
            'source_path': source_path,
            'target_path': target_path,
            'quality': self.quality,
            'subdirs': self.include_subdirs
        }

        self.is_running = True
        self.start_btn.setEnabled(False)
        self.stop_btn.setEnabled(True)
        self.progress_bar.setValue(0)
        
        self.convert_thread = threading.Thread(target=self.execute, args=(params,))
        self.convert_thread.daemon = True
        self.convert_thread.start()

    def stop_execution(self):
        """停止执行"""
        self.is_running = False

    def execute(self, params: Dict[str, Any]):
        """执行转换"""
        try:
            source_path = params['source_path']
            target_path = params['target_path']
            quality = params['quality']
            scan_subdirs = params['subdirs']
            
            # 初始化统计
            total_files = 0
            converted_files = 0
            failed_files = 0
            
            # 收集要转换的文件
            image_files = []
            valid_extensions = ('.png', '.jpg', '.jpeg', '.bmp', '.gif', '.webp')
            
            if scan_subdirs:
                for root, _, files in os.walk(source_path):
                    if not self.is_running: 
                        self.log_message.emit("转换被用户停止", "info")
                        return
                    for file in files:
                        if file.lower().endswith(valid_extensions):
                            image_files.append((os.path.join(root, file), root))
            else:
                for file in os.listdir(source_path):
                    if not self.is_running: 
                        self.log_message.emit("转换被用户停止", "info")
                        return
                    if file.lower().endswith(valid_extensions):
                        image_files.append((os.path.join(source_path, file), source_path))
            
            if not image_files:
                self.log_message.emit("未找到要转换的图片文件", "warning")
                return
                
            total_files = len(image_files)
            self.log_message.emit(f"找到 {total_files} 个文件进行转换", "info")
            
            # 更新进度标签和统计
            self.progress_label.setText(f"转换中: 0/{total_files}")
            self.stats_label.setText(f"文件: {total_files} | 已转换: {converted_files} | 失败: {failed_files}")
            
            # 转换文件
            for i, (file_path, original_dir) in enumerate(image_files):
                if not self.is_running: 
                    self.log_message.emit("转换被用户停止", "info")
                    break
                    
                try:
                    # 计算目标路径
                    relative_path = os.path.relpath(original_dir, source_path)
                    target_dir = os.path.join(target_path, relative_path) if relative_path != '.' else target_path
                    os.makedirs(target_dir, exist_ok=True)
                    
                    # 生成目标文件名
                    base_name = os.path.splitext(os.path.basename(file_path))[0]
                    target_file = os.path.join(target_dir, f"{base_name}.avif")
                    
                    # 检查是否已存在
                    if os.path.exists(target_file):
                        counter = 1
                        while os.path.exists(os.path.join(target_dir, f"{base_name}_{counter}.avif")):
                            counter += 1
                        target_file = os.path.join(target_dir, f"{base_name}_{counter}.avif")
                    
                    # 转换图片
                    with Image.open(file_path) as img:
                        # 处理RGBA模式图片
                        if img.mode == 'RGBA':
                            # 创建白色背景
                            background = Image.new('RGB', img.size, (255, 255, 255))
                            background.paste(img, mask=img.split()[-1])
                            img = background
                        elif img.mode != 'RGB':
                            img = img.convert('RGB')
                            
                        img.save(target_file, 'AVIF', quality=quality)
                    
                    converted_files += 1
                    self.log_message.emit(f"已转换: {os.path.basename(file_path)} -> {os.path.basename(target_file)}", "success")
                    
                    # 更新进度和统计
                    progress = (i + 1) / total_files * 100
                    self.progress_updated.emit(progress, f"转换中: {converted_files}/{total_files}")
                    self.stats_label.setText(f"文件: {total_files} | 已转换: {converted_files} | 失败: {failed_files}")
                    
                except Exception as e:
                    failed_files += 1
                    self.log_message.emit(f"转换失败 {os.path.basename(file_path)}: {str(e)}", "error")
                    # 更新统计
                    self.stats_label.setText(f"文件: {total_files} | 已转换: {converted_files} | 失败: {failed_files}")
            
            # 完成
            self.log_message.emit(f"转换完成！成功转换 {converted_files}/{total_files} 个文件", "info")
            
        except Exception as e:
            self.log_message.emit(f"转换过程中出错: {str(e)}", "error")
        finally:
            self.is_running = False
            self.start_btn.setEnabled(True)
            self.stop_btn.setEnabled(False)