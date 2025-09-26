#!/usr/bin/env python3
"""
AVIF转换模块
"""

from core.base_module import BaseFunctionModule
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QProgressBar, QTextEdit, QFileDialog, QLineEdit, QCheckBox, QSpinBox, QGroupBox, QComboBox
from PyQt6.QtCore import Qt


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
        self.stop_btn = QPushButton("⏹️ 停止")
        self.stop_btn.clicked.connect(self.stop_execution)
        self.stop_btn.setEnabled(False)
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
        # 工作区由专门的面板处理
        return None

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
        
        # 执行转换（这里应该在后台线程中进行）
        self.execute({
            'source_path': self.source_path,
            'target_path': self.target_path,
            'quality': self.quality,
            'format': self.format_combo.currentText(),
            'include_subdirs': self.subdir_checkbox.isChecked()
        })

    def execute(self, params: dict):
        """
        执行转换操作

        Args:
            params: 执行参数
        """
        # 这里应该实现实际的转换逻辑
        # 为演示目的，我们只是模拟进度更新
        self.progress_updated.emit(0, "开始转换...")
        self.log_message.emit(f"开始转换: {params['source_path']} -> {params['target_path']}", "info")
        
        # 模拟转换过程
        import time
        for i in range(1, 101):
            time.sleep(0.05)  # 模拟工作
            self.progress_updated.emit(i, f"转换进度: {i}%")
            
        self.progress_updated.emit(100, "转换完成")
        self.log_message.emit("转换完成", "info")
        
        self.execution_finished.emit({})
        self.convert_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)

    def stop_execution(self):
        """
        停止执行
        """
        self.log_message.emit("用户停止了转换", "info")
        self.convert_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)
        self.progress_updated.emit(0, "已停止")

    def update_progress(self, value: float, message: str):
        """更新进度"""
        self.progress_bar.setValue(int(value))
        self.progress_bar.setFormat(f"{message} ({int(value)}%)")
        self.status_label.setText(message)

    def add_log_message(self, message: str, level: str):
        """添加日志消息"""
        formatted_message = f"[{level.upper()}] {message}"
        self.log_text.append(formatted_message)