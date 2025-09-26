import sys
import os
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QSplitter, QFrame, QLabel, QPushButton,
                             QTextEdit, QProgressBar, QListWidget, QGroupBox,
                             QFileDialog, QMessageBox, QSlider, QCheckBox, QLineEdit)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont

class SimplePyQt6App(QMainWindow):
    """
    简化版PyQt6图片处理工具套件主程序
    用于测试PyQt6是否能正常显示窗口
    """
    def __init__(self):
        super().__init__()
        self.setWindowTitle("简化版图片处理工具套件 - PyQt6测试")
        self.setGeometry(100, 100, 1200, 800)
        self.setMinimumSize(1000, 600)

        # 设置应用程序字体
        font = QFont("Segoe UI", 10)
        QApplication.instance().setFont(font)

        # 应用现代化深色主题样式表
        self.setStyleSheet("""
            QMainWindow {
                background-color: #1e1e1e;
            }
            
            QWidget {
                background-color: #1e1e1e;
                color: #ffffff;
                font-family: "Segoe UI", sans-serif;
            }
            
            QFrame {
                background-color: #2d2d30;
                border: none;
            }
            
            QLabel {
                color: #ffffff;
                background-color: transparent;
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
                border: 1px solid #555555;
            }
            
            QPushButton:pressed {
                background-color: #0078d7;
                border: 1px solid #0078d7;
            }
            
            QGroupBox {
                background-color: #2d2d30;
                border: 1px solid #3f3f46;
                border-radius: 6px;
                margin-top: 1ex;
                padding-top: 10px;
                font-weight: 600;
                color: #ffffff;
            }
            
            QGroupBox::title {
                subcontrol-origin: margin;
                subcontrol-position: top left;
                left: 10px;
                padding: 0 5px;
                color: #cccccc;
            }
            
            QLineEdit {
                background-color: #333337;
                color: #ffffff;
                border: 1px solid #454545;
                border-radius: 4px;
                padding: 6px;
            }
            
            QLineEdit:focus {
                border: 1px solid #0078d7;
            }
            
            QSlider::groove:horizontal {
                border: 1px solid #454545;
                height: 4px;
                background: #333337;
                border-radius: 2px;
            }
            
            QSlider::handle:horizontal {
                background: #0078d7;
                border: 1px solid #005a9e;
                width: 18px;
                height: 18px;
                margin: -7px 0;
                border-radius: 9px;
            }
            
            QCheckBox {
                color: #ffffff;
                spacing: 5px;
            }
            
            QCheckBox::indicator {
                width: 18px;
                height: 18px;
            }
            
            QCheckBox::indicator:unchecked {
                border: 1px solid #454545;
                background-color: #333337;
            }
            
            QCheckBox::indicator:checked {
                border: 1px solid #0078d7;
                background-color: #0078d7;
            }
            
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
            
            QTextEdit {
                background-color: #333337;
                color: #ffffff;
                border: 1px solid #454545;
                border-radius: 4px;
            }
            
            QListWidget {
                background-color: #333337;
                color: #ffffff;
                border: 1px solid #454545;
                border-radius: 4px;
            }
        """)

        # 创建主布局
        self.create_main_layout()

    def create_main_layout(self):
        """创建主布局"""
        # 创建中央窗口部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # 创建主水平分割器，用于分隔左侧功能区和右侧操作区
        main_splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # 左侧框架
        left_frame = QFrame()
        
        # 左上部分 (功能选择面板)
        function_selector_frame = QGroupBox("🔧 功能选择")
        
        # 功能按钮
        dedup_button = QPushButton("🔍 图片去重")
        avif_button = QPushButton("🔄 AVIF转换")
        
        function_layout = QVBoxLayout(function_selector_frame)
        function_layout.addWidget(dedup_button)
        function_layout.addWidget(avif_button)
        
        # 左下部分 (设置控制面板)
        settings_frame = QGroupBox("⚙️ 设置")
        
        # 简单设置控件
        path_label = QLabel("路径:")
        path_entry = QLineEdit()
        browse_btn = QPushButton("浏览")
        
        sensitivity_label = QLabel("相似度阈值:")
        sensitivity_slider = QSlider(Qt.Orientation.Horizontal)
        sensitivity_slider.setMinimum(70)
        sensitivity_slider.setMaximum(100)
        sensitivity_slider.setValue(95)
        
        subdirs_check = QCheckBox("包含子目录")
        subdirs_check.setChecked(True)
        
        start_btn = QPushButton("▶️ 开始")
        stop_btn = QPushButton("⏹️ 停止")
        
        settings_layout = QVBoxLayout(settings_frame)
        settings_layout.addWidget(path_label)
        settings_layout.addWidget(path_entry)
        settings_layout.addWidget(browse_btn)
        settings_layout.addWidget(sensitivity_label)
        settings_layout.addWidget(sensitivity_slider)
        settings_layout.addWidget(subdirs_check)
        settings_layout.addWidget(start_btn)
        settings_layout.addWidget(stop_btn)
        
        # 布局左侧
        left_layout = QVBoxLayout(left_frame)
        left_layout.addWidget(function_selector_frame)
        left_layout.addWidget(settings_frame)
        
        # 右侧部分 (操作区)
        right_frame = QFrame()
        right_title = QLabel("🎯 操作与结果")
        
        # 进度区域
        progress_label = QLabel("操作尚未开始")
        progress_bar = QProgressBar()
        progress_bar.setValue(30)
        
        # 日志区域
        log_text = QTextEdit()
        log_text.setReadOnly(True)
        log_text.append("这是日志区域")
        log_text.append("程序已启动")
        
        # 布局右侧
        right_layout = QVBoxLayout(right_frame)
        right_layout.addWidget(right_title)
        right_layout.addWidget(progress_label)
        right_layout.addWidget(progress_bar)
        right_layout.addWidget(QLabel("日志:"))
        right_layout.addWidget(log_text)
        
        # 将左右部分添加到主分割器
        main_splitter.addWidget(left_frame)
        main_splitter.addWidget(right_frame)
        
        # 设置初始大小比例
        main_splitter.setSizes([300, 900])
        
        # 布局中央窗口部件
        main_layout = QHBoxLayout(central_widget)
        main_layout.addWidget(main_splitter)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = SimplePyQt6App()
    window.show()
    sys.exit(app.exec())