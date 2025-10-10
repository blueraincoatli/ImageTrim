#!/usr/bin/env python3
"""
AVIF转换模块
"""

import threading
from core.base_module import BaseFunctionModule
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QProgressBar, QTextEdit, QFileDialog, QLineEdit, QCheckBox, QSpinBox, QGroupBox, QComboBox
from PyQt6.QtCore import Qt
from .ui import AVIFConverterWorkspace
from .logic import AVIFConverterLogic


class AVIFConverterModule(BaseFunctionModule):
    """
    AVIF转换模块
    """

    def __init__(self):
        super().__init__(
            name="avif_converter",
            display_name="🔄 AVIF转换",
            description="将图片转换为AVIF格式以节省存储空间",
            icon="🔄"
        )
        self.source_path = ""
        self.target_path = ""
        self.quality = 85
        self.settings_ui = None
        self.workspace_ui = None
        self.convert_thread = None
        self.converter_logic = AVIFConverterLogic(self)
        
        # 连接执行完成信号
        self.execution_finished.connect(self.on_execution_finished)

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
        
        # 源路径设置
        source_group = QGroupBox("📁 源路径")
        source_layout = QVBoxLayout(source_group)
        
        source_input_layout = QHBoxLayout()
        self.source_edit = QLineEdit()
        self.source_edit.setPlaceholderText("请选择要转换的图片或目录")
        source_browse_btn = QPushButton("浏览...")
        source_browse_btn.clicked.connect(self.browse_source)
        source_input_layout.addWidget(self.source_edit)
        source_input_layout.addWidget(source_browse_btn)
        
        source_layout.addLayout(source_input_layout)
        
        # 目标路径设置
        target_group = QGroupBox("📂 目标路径")
        target_layout = QVBoxLayout(target_group)
        
        target_input_layout = QHBoxLayout()
        self.target_edit = QLineEdit()
        self.target_edit.setPlaceholderText("请选择转换后文件的保存目录")
        target_browse_btn = QPushButton("浏览...")
        target_browse_btn.clicked.connect(self.browse_target)
        target_input_layout.addWidget(self.target_edit)
        target_input_layout.addWidget(target_browse_btn)
        
        target_layout.addLayout(target_input_layout)
        
        # 转换设置
        settings_group = QGroupBox("⚙️ 转换设置")
        settings_layout = QVBoxLayout(settings_group)
        
        # 质量设置
        quality_layout = QHBoxLayout()
        quality_layout.addWidget(QLabel("质量:"))
        self.quality_spinbox = QSpinBox()
        self.quality_spinbox.setRange(1, 100)
        self.quality_spinbox.setValue(self.quality)
        self.quality_spinbox.setSuffix(" %")
        quality_layout.addWidget(self.quality_spinbox)
        quality_layout.addStretch()
        settings_layout.addLayout(quality_layout)
        
        # 格式选项
        format_layout = QHBoxLayout()
        format_layout.addWidget(QLabel("格式:"))
        self.format_combo = QComboBox()
        self.format_combo.addItems(["AVIF", "WEBP", "JPEG", "PNG"])
        self.format_combo.setCurrentText("AVIF")
        format_layout.addWidget(self.format_combo)
        format_layout.addStretch()
        settings_layout.addLayout(format_layout)
        
        # 选项
        self.subdir_checkbox = QCheckBox("包含子目录")
        self.subdir_checkbox.setChecked(True)
        settings_layout.addWidget(self.subdir_checkbox)
        
        # 操作按钮
        button_layout = QHBoxLayout()
        self.convert_btn = QPushButton("🔄 开始转换")
        self.convert_btn.clicked.connect(self.start_conversion)
        self.convert_btn.setStyleSheet("""
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
        self.stop_btn = QPushButton("⏹️ 停止")
        self.stop_btn.clicked.connect(self.stop_execution)
        self.stop_btn.setEnabled(False)
        self.stop_btn.setStyleSheet("""
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
        button_layout.addWidget(self.convert_btn)
        button_layout.addWidget(self.stop_btn)
        
        # 添加到主布局
        layout.addWidget(source_group)
        layout.addWidget(target_group)
        layout.addWidget(settings_group)
        layout.addLayout(button_layout)
        layout.addStretch()
        
        return widget

    def create_workspace_ui(self):
        """
        创建工作区UI面板

        Returns:
            QWidget: 工作区UI面板
        """
        if not self.workspace_ui:
            self.workspace_ui = AVIFConverterWorkspace(self)
        return self.workspace_ui

    def browse_source(self):
        """浏览选择源路径"""
        path = QFileDialog.getExistingDirectory(None, "选择源目录")
        if path:
            self.source_edit.setText(path)
            self.source_path = path

    def browse_target(self):
        """浏览选择目标路径"""
        path = QFileDialog.getExistingDirectory(None, "选择目标目录")
        if path:
            self.target_edit.setText(path)
            self.target_path = path

    def start_conversion(self):
        """开始转换"""
        self.source_path = self.source_edit.text()
        self.target_path = self.target_edit.text()
        self.quality = self.quality_spinbox.value()
        
        if not self.source_path:
            self.log_message.emit("请选择源路径", "warning")
            return
            
        if not self.target_path:
            self.log_message.emit("请选择目标路径", "warning")
            return
            
        self.convert_btn.setEnabled(False)
        self.stop_btn.setEnabled(True)
        
        # 在后台线程中执行转换
        params = {
            'source_path': self.source_path,
            'target_path': self.target_path,
            'quality': self.quality,
            'format': self.format_combo.currentText(),
            'include_subdirs': self.subdir_checkbox.isChecked()
        }
        
        self.converter_logic.is_running = True
        self.convert_thread = threading.Thread(target=self.converter_logic.convert_images, args=(params,))
        self.convert_thread.daemon = True
        self.convert_thread.start()

    def execute(self, params: dict):
        """
        执行转换操作

        Args:
            params: 执行参数
        """
        # 这个方法现在由start_conversion调用的后台线程处理
        pass

    def stop_execution(self):
        """
        停止执行
        """
        self.converter_logic.is_running = False
        self.log_message.emit("用户停止了转换", "info")
        self.convert_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)
        self.progress_updated.emit(0, "已停止")
        
    def on_execution_finished(self, result_data):
        """
        处理执行完成事件
        """
        self.convert_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)
        
    def on_execution_finished(self, result_data):
        """
        处理执行完成事件
        """
        self.convert_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)
        
        # 如果工作区UI存在，更新其统计信息
        if self.workspace_ui:
            self.workspace_ui.on_execution_finished(result_data)