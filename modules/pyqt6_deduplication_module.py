"""
PyQt6版本图片去重功能模块
"""

import os
import threading
from typing import Dict, Any, List
from datetime import datetime
from collections import defaultdict
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
                             QLabel, QPushButton, QCheckBox, QSlider, QSpinBox,
                             QDoubleSpinBox, QComboBox, QLineEdit, QTextEdit,
                             QProgressBar, QScrollArea, QFrame, QListWidget,
                             QFileDialog, QMessageBox, QGroupBox, QApplication)
from PyQt6.QtCore import Qt, pyqtSignal, QObject, pyqtSlot
from PyQt6.QtGui import QPixmap, QFont, QColor, QPalette, QImage

try:
    from PIL import Image, ImageQt
    import imagehash
except ImportError as e:
    print(f"错误: 必要的库未安装。{e}")
    exit()

from modules.pyqt6_base_module import PyQt6BaseFunctionModule
from ui.pyqt6_adapter import Variable, StringVar, IntVar, DoubleVar, BooleanVar


class PyQt6DeduplicationModule(PyQt6BaseFunctionModule):
    """PyQt6版本图片去重功能模块"""

    def __init__(self):
        super().__init__(
            name="pyqt6_deduplication",
            display_name="Image Deduplication",
            description="Find and process duplicate or similar images with advanced selection.",
            icon="🔍"
        )
        self.scan_thread = None
        self.is_running = False
        # UI组件的引用

        # 图片缓存管理器
        self._image_cache = self._ImageCache(max_size=100)
        self.workspace_root = None
        self.settings_root = None
        # 存储重复组数据
        self.duplicate_groups = {}
        # 存储选中的文件
        self.selected_files = set()
        # 存储上次点击的图片，用于Shift选择
        self.last_clicked_widget = None
        # 框选相关变量
        self.is_selecting = False
        self.selection_rect = None
        self.start_x = 0
        self.start_y = 0
        # 存储卡片框架引用
        self.card_frames_map = {}
        
        # 使用主应用的全局字体设置
        self.default_font = None
        self.large_font = None
        self.small_font = None

    def create_settings_ui(self, parent: QWidget) -> QWidget:
        """创建设置UI面板（中栏）"""
        self.settings_root = parent
        settings_frame = QWidget(parent)
        settings_layout = QVBoxLayout(settings_frame)
        settings_layout.setContentsMargins(10, 10, 10, 10)

        # 1. 扫描路径（支持多个路径）
        paths_frame = QGroupBox("Scan Paths")
        paths_frame.setStyleSheet("QGroupBox { background-color: #1B1B1B; color: white; border: 1px solid #353535; font-weight: bold; }")
        paths_layout = QVBoxLayout(paths_frame)
        paths_layout.setContentsMargins(10, 20, 10, 10)

        # 路径列表显示区域
        self.paths_listbox = QListWidget()
        self.paths_listbox.setStyleSheet("""
            QListWidget {
                background-color: #1B1B1B;
                color: white;
                border: 1px solid #6c757d;
                border-radius: 4px;
                min-height: 80px;
            }
            QListWidget::item {
                padding: 5px;
            }
            QListWidget::item:selected {
                background-color: #FF8C00;
                color: black;
            }
        """)
        paths_layout.addWidget(self.paths_listbox)
        
        # 路径操作按钮
        path_btn_frame = QWidget()
        path_btn_layout = QHBoxLayout(path_btn_frame)
        path_btn_layout.setContentsMargins(0, 0, 0, 0)
        
        add_path_btn = QPushButton("Add Path")
        add_path_btn.setStyleSheet("""
            QPushButton {
                background-color: #28a745;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #218838;
            }
        """)
        add_path_btn.clicked.connect(self.add_folder)
        path_btn_layout.addWidget(add_path_btn)
        
        remove_path_btn = QPushButton("Remove Path")
        remove_path_btn.setStyleSheet("""
            QPushButton {
                background-color: #dc3545;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #c82333;
            }
        """)
        remove_path_btn.clicked.connect(self.remove_folder)
        path_btn_layout.addWidget(remove_path_btn)
        
        clear_paths_btn = QPushButton("Clear Paths")
        clear_paths_btn.setStyleSheet("""
            QPushButton {
                background-color: #ffc107;
                color: black;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #e0a800;
            }
        """)
        clear_paths_btn.clicked.connect(self.clear_folders)
        path_btn_layout.addWidget(clear_paths_btn)
        
        paths_layout.addWidget(path_btn_frame)

        # 2. 检测设置
        options_frame = QGroupBox("Detection Settings")
        options_frame.setStyleSheet("QGroupBox { background-color: #1B1B1B; color: white; border: 1px solid #353535; font-weight: bold; }")
        options_layout = QVBoxLayout(options_frame)
        options_layout.setContentsMargins(10, 20, 10, 10)

        sens_frame = QWidget()
        sens_layout = QHBoxLayout(sens_frame)
        sens_layout.setContentsMargins(0, 0, 0, 0)
        sens_label = QLabel("Similarity Threshold:")
        sens_layout.addWidget(sens_label)
        
        self.sensitivity_var = DoubleVar(value=95.0)
        self.sens_scale = QSlider(Qt.Orientation.Horizontal)
        self.sens_scale.setMinimum(70)
        self.sens_scale.setMaximum(100)
        self.sens_scale.setValue(95)
        self.sens_scale.setStyleSheet("""
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
        self.sens_scale.valueChanged.connect(self.on_sensitivity_changed)
        sens_layout.addWidget(self.sens_scale)
        
        self.sens_value_label = QLabel("95%")
        self.sens_value_label.setFixedWidth(40)
        sens_layout.addWidget(self.sens_value_label)
        
        options_layout.addWidget(sens_frame)

        self.subdirs_var = BooleanVar(value=True)
        subdirs_check = QCheckBox("Include Subdirectories")
        subdirs_check.setChecked(True)
        subdirs_check.setStyleSheet("QCheckBox { color: white; }")
        subdirs_check.stateChanged.connect(lambda state: setattr(self.subdirs_var, 'value', state == Qt.CheckState.Checked.value))
        options_layout.addWidget(subdirs_check)

        # 3. 操作控制
        action_frame = QGroupBox("Operation Control")
        action_frame.setStyleSheet("QGroupBox { background-color: #1B1B1B; color: white; border: 1px solid #353535; font-weight: bold; }")
        action_layout = QVBoxLayout(action_frame)
        action_layout.setContentsMargins(10, 20, 10, 10)

        button_frame = QWidget()
        button_layout = QHBoxLayout(button_frame)
        button_layout.setContentsMargins(0, 0, 0, 0)
        
        self.start_btn = QPushButton("▶️ Start Scan")
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
        self.start_btn.clicked.connect(self.start_scan)
        button_layout.addWidget(self.start_btn)

        self.stop_btn = QPushButton("⏹️ Stop")
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
        settings_layout.addWidget(paths_frame)
        settings_layout.addWidget(options_frame)
        settings_layout.addWidget(action_frame)
        settings_layout.addStretch()

        return settings_frame

    def on_sensitivity_changed(self, value):
        """处理敏感度滑块变化"""
        self.sens_value_label.setText(f"{value}%")
        self.sensitivity_var.value = float(value)

    def create_workspace_ui(self, parent: QWidget) -> QWidget:
        """创建工作区UI面板（右栏）"""
        self.workspace_root = parent
        workspace_frame = QWidget(parent)
        workspace_layout = QVBoxLayout(workspace_frame)
        workspace_layout.setContentsMargins(10, 10, 10, 10)
        
        # 进度区域
        progress_frame = QWidget()
        progress_layout = QHBoxLayout(progress_frame)
        progress_layout.setContentsMargins(0, 0, 0, 0)
        self.stats_label = QLabel("Scan not started yet.")
        self.stats_label.setStyleSheet("color: white;")
        progress_layout.addWidget(self.stats_label)
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                border: 1px solid #6c757d;
                border-radius: 4px;
                text-align: center;
                background-color: #2B2B2B;
            }
            QProgressBar::chunk {
                background-color: #FF8C00;
            }
        """)
        self.progress_bar.setValue(0)
        progress_layout.addWidget(self.progress_bar)
        
        workspace_layout.addWidget(progress_frame)
        
        # Top operation toolbar
        toolbar_frame = QWidget()
        toolbar_layout = QHBoxLayout(toolbar_frame)
        toolbar_layout.setContentsMargins(0, 0, 0, 0)
        
        # Select all/Unselect all buttons
        self.select_all_btn = QPushButton("Select All")
        self.select_all_btn.setStyleSheet("""
            QPushButton {
                background-color: #007bff;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #0069d9;
            }
        """)
        self.select_all_btn.clicked.connect(self.select_all_images)
        toolbar_layout.addWidget(self.select_all_btn)
        
        self.unselect_all_btn = QPushButton("Unselect All")
        self.unselect_all_btn.setStyleSheet("""
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
        self.unselect_all_btn.clicked.connect(self.unselect_all_images)
        toolbar_layout.addWidget(self.unselect_all_btn)
        
        # Selected count label
        self.selection_count_label = QLabel("Selected: 0")
        self.selection_count_label.setStyleSheet("color: white; margin-left: 20px; margin-right: 20px;")
        toolbar_layout.addWidget(self.selection_count_label)
        
        # Operation buttons
        delete_btn = QPushButton("Delete Selected")
        delete_btn.setStyleSheet("""
            QPushButton {
                background-color: #dc3545;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #c82333;
            }
        """)
        delete_btn.clicked.connect(self.delete_selected_files_advanced)
        toolbar_layout.addWidget(delete_btn)
        
        move_btn = QPushButton("Move Selected")
        move_btn.setStyleSheet("""
            QPushButton {
                background-color: #ffc107;
                color: black;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #e0a800;
            }
        """)
        move_btn.clicked.connect(self.move_selected_files_advanced)
        toolbar_layout.addWidget(move_btn)
        
        # Toggle log button
        self.toggle_log_btn = QPushButton(" Log")
        self.toggle_log_btn.setStyleSheet("""
            QPushButton {
                background-color: #6c757d;
                color: white;
                border: none;
                padding: 8px 12px;
                border-radius: 4px;
                font-weight: bold;
                font-size: 12px;
                min-width: 90px;
            }
            QPushButton:hover {
                background-color: #5a6268;
            }
        """)
        self.toggle_log_btn.clicked.connect(self.toggle_log_visibility)
        toolbar_layout.addWidget(self.toggle_log_btn)
        
        toolbar_layout.addStretch()
        
        workspace_layout.addWidget(toolbar_frame)
        
        # Log area (hidden by default)
        self.log_frame = QGroupBox("Log")
        self.log_frame.setStyleSheet("QGroupBox { background-color: #1B1B1B; color: white; border: 1px solid #353535; font-weight: bold; }")
        log_layout = QVBoxLayout(self.log_frame)
        log_layout.setContentsMargins(10, 20, 10, 10)
        
        self.log_text = QTextEdit()
        self.log_text.setStyleSheet("""
            QTextEdit {
                background-color: #1B1B1B;
                color: white;
                border: 1px solid #6c757d;
                border-radius: 4px;
                min-height: 50px;
                max-height: 100px;
            }
        """)
        self.log_text.setReadOnly(True)
        log_layout.addWidget(self.log_text)
        
        # Initially hide log area
        self.log_frame.setVisible(False)
        self.log_visible = False
        
        workspace_layout.addWidget(self.log_frame)
        
        # Results area
        result_label = QLabel("Scan Results")
        result_label.setStyleSheet("color: white; font-size: 16px; font-weight: bold;")
        workspace_layout.addWidget(result_label)
        
        # Results scroll area (expand to fill available space)
        self.scroll_area = QScrollArea()
        self.scroll_area.setStyleSheet("""
            QScrollArea {
                background-color: #1B1B1B;
                border: 1px solid #6c757d;
                border-radius: 4px;
            }
        """)
        self.scroll_area.setWidgetResizable(True)
        
        self.scrollable_frame = QWidget()
        self.scrollable_frame.setStyleSheet("background-color: #1B1B1B;")
        self.scroll_area.setWidget(self.scrollable_frame)
        
        # Set the scroll area to expand and take up available space
        workspace_layout.addWidget(self.scroll_area)
        
        # 设置回调函数
        self.set_callbacks(self.update_progress, self.add_log_message)
        
        return workspace_frame

    def browse_folder(self):
        """浏览文件夹"""
        path = QFileDialog.getExistingDirectory(None, "Select Directory")
        if path:
            self.path_var.value = path
            
    def add_folder(self):
        """添加文件夹"""
        path = QFileDialog.getExistingDirectory(None, "Select Directory")
        if path and path not in [self.paths_listbox.item(i).text() for i in range(self.paths_listbox.count())]:
            self.paths_listbox.addItem(path)
            
    def remove_folder(self):
        """移除文件夹"""
        current_row = self.paths_listbox.currentRow()
        if current_row >= 0:
            self.paths_listbox.takeItem(current_row)
            
    def clear_folders(self):
        """清空文件夹列表"""
        self.paths_listbox.clear()

    def start_scan(self):
        """开始扫描"""
        # 获取所有扫描路径
        paths = [self.paths_listbox.item(i).text() for i in range(self.paths_listbox.count())]
        
        if not paths:
            QMessageBox.critical(None, "Invalid Path", "请至少添加一个有效的文件夹路径。")
            return
            
        # 验证所有路径都有效
        for path in paths:
            if not os.path.isdir(path):
                QMessageBox.critical(None, "Invalid Path", f"路径不存在或无效: {path}")
                return

        params = {
            'paths': paths,
            'sensitivity': self.sensitivity_var.value,
            'subdirs': self.subdirs_var.value
        }

        self.is_running = True
        self.start_btn.setEnabled(False)
        self.stop_btn.setEnabled(True)

        # 清空结果区域
        for i in reversed(range(self.scrollable_frame.layout().count() if self.scrollable_frame.layout() else 0)): 
            self.scrollable_frame.layout().itemAt(i).widget().setParent(None)

        self.scan_thread = threading.Thread(target=self.execute, args=(params,))
        self.scan_thread.daemon = True
        self.scan_thread.start()

    def stop_execution(self):
        """停止执行"""
        self.is_running = False

    def execute(self, params: Dict[str, Any]):
        """执行扫描"""
        try:
            scan_paths = params['paths']
            threshold = 100 - params['sensitivity']
            scan_subdirs = params['subdirs']

            # 收集所有图片文件
            image_files = []
            valid_extensions = ('.png', '.jpg', '.jpeg', '.bmp', '.gif', '.webp')
            
            total_paths = len(scan_paths)
            for path_idx, scan_path in enumerate(scan_paths):
                if not self.is_running: break
                
                # 更新进度信息
                if self.log_callback:
                    self.log_callback(f"正在扫描路径 ({path_idx+1}/{total_paths}): {scan_path}", "info")
                
                if scan_subdirs:
                    for root, _, files in os.walk(scan_path):
                        if not self.is_running: break
                        for file in files:
                            if file.lower().endswith(valid_extensions):
                                image_files.append(os.path.join(root, file))
                else:
                    for file in os.listdir(scan_path):
                        if not self.is_running: break
                        if file.lower().endswith(valid_extensions):
                            image_files.append(os.path.join(scan_path, file))
            
            if not self.is_running: return

            # 计算哈希值
            hashes = {}
            total_files = len(image_files)
            
            if self.log_callback:
                self.log_callback(f"找到 {total_files} 个图片文件，开始计算哈希值...", "info")
            
            for i, f in enumerate(image_files):
                if not self.is_running: break
                
                # 更新进度
                if self.progress_callback:
                    progress = (i + 1) / total_files * 100
                    self.progress_callback(progress, f"计算哈希值: {i+1}/{total_files}")
                
                try:
                    with Image.open(f) as img:
                        hash_value = imagehash.phash(img)
                        hashes[f] = hash_value
                except Exception as e:
                    if self.log_callback:
                        self.log_callback(f"无法处理图片 {f}: {str(e)}", "warning")
            
            if not self.is_running: return

            # 查找重复项
            if self.log_callback:
                self.log_callback("正在查找重复图片...", "info")
                self.log_callback(f"哈希值数量: {len(hashes)}, 阈值: {threshold}", "info")

            # 使用逐组显示的方式查找重复图片
            duplicates = self._find_duplicates_progressive(hashes, threshold)

            if self.log_callback:
                self.log_callback(f"找到重复组数量: {len(duplicates)}", "info")

            if not self.is_running: return

            # 存储重复组数据
            self.duplicate_groups = dict(duplicates)

            # 最终显示所有结果
            if hasattr(self.workspace_root, 'after'):  # 兼容tkinter的after方法
                self.workspace_root.after(0, lambda: self.display_results_async(duplicates))
            else:
                # PyQt6直接调用
                self.display_results_async(duplicates)

        except Exception as e:
            if self.log_callback:
                self.log_callback(f"执行过程中出错: {str(e)}", "error")
            print(f"Error during execution: {e}")
        finally:
            self.is_running = False
            if self.settings_root:
                if hasattr(self.settings_root, 'after'):  # 兼容tkinter的after方法
                    self.settings_root.after(0, lambda: self.start_btn.setEnabled(True))
                    self.settings_root.after(0, lambda: self.stop_btn.setEnabled(False))
                else:
                    # PyQt6直接调用
                    self.start_btn.setEnabled(True)
                    self.stop_btn.setEnabled(False)
                
            # 完成消息
            if self.log_callback:
                self.log_callback("扫描完成", "info")

    def update_progress(self, value: float, message: str = ""):
        """更新进度条和状态信息"""
        if self.workspace_root:
            if hasattr(self.workspace_root, 'after'):  # 兼容tkinter的after方法
                self.workspace_root.after(0, lambda: self.progress_bar.setValue(int(value)))
                if message:
                    self.workspace_root.after(0, lambda: self.stats_label.setText(message))
            else:
                # PyQt6直接调用
                self.progress_bar.setValue(int(value))
                if message:
                    self.stats_label.setText(message)
                
    def add_log_message(self, message: str, level: str = "info"):
        """Add log message"""
        if self.workspace_root:
            timestamp = datetime.now().strftime("%H:%M:%S")
            formatted_message = f"[{timestamp}] [{level.upper()}] {message}"
            # PyQt6 direct call
            self.update_log_label(formatted_message)
            
    def update_log_label(self, message: str):
        """Update log label"""
        # Check if log_text widget still exists and is valid using the base class method
        if hasattr(self, 'log_text') and self._is_widget_valid(self.log_text):
            try:
                self.log_text.append(message)
            except RuntimeError:
                # Widget has been deleted, clear the reference
                self.log_text = None
        
    def display_results_async(self, duplicates: Dict):
        """
        异步显示结果
        """
        if not self.is_running:
            return

        # 快速清空现有UI
        self._clear_results_fast()

        if not duplicates:
            self._show_no_results_message()
            return

        # 初始化显示数据
        self._init_display_data(duplicates)

        # 创建主容器
        main_container = self._create_main_container()

        # 直接创建UI组件（同步方式，确保能正确显示）
        self._create_ui_components_sync(main_container, duplicates)

    def _clear_results_fast(self):
        """快速清空现有UI组件"""
        try:
            # 清空滚动区域的内容
            if self.scrollable_frame.layout():
                for i in reversed(range(self.scrollable_frame.layout().count())):
                    widget = self.scrollable_frame.layout().itemAt(i).widget()
                    if widget:
                        widget.setParent(None)
        except Exception:
            pass  # 忽略清理错误

    def _show_no_results_message(self):
        """显示无结果消息"""
        self.stats_label.setText("未找到重复图片。")
        message_label = QLabel("恭喜！未在指定目录中找到重复图片。")
        message_label.setStyleSheet("color: white; font-style: italic; padding: 50px;")
        layout = self.scrollable_frame.layout() or QVBoxLayout(self.scrollable_frame)
        layout.addWidget(message_label)

    def _init_display_data(self, duplicates: Dict):
        """初始化显示数据"""
        num_groups = len(duplicates)
        num_files = sum(len(v) for v in duplicates.values())
        self.stats_label.setText(f"找到 {num_groups} 组重复图片，共 {num_files} 个文件。")

        # 重置数据结构
        self.image_widgets_map = {}
        self.card_frames_map = {}
        self.selected_groups = set()

    def _create_main_container(self):
        """创建主容器"""
        main_container = QWidget(self.scrollable_frame)
        layout = self.scrollable_frame.layout() or QVBoxLayout(self.scrollable_frame)
        layout.addWidget(main_container)
        return main_container

    def _create_ui_components_sync(self, main_container, duplicates: Dict):
        """
        同步创建UI组件
        """
        try:
            # 设置主容器布局
            grid_layout = QGridLayout(main_container)
            grid_layout.setSpacing(10)
            
            # 计算列数
            columns = 3  # 默认3列
            
            # 创建所有UI组件
            group_items = list(duplicates.items())
            
            for group_idx, (master, dups) in enumerate(group_items):
                if not self.is_running:
                    break

                # 计算网格位置
                row = group_idx // columns
                col = group_idx % columns

                # 创建卡片
                card_frame = self._create_single_card(dups, group_idx + 1)
                grid_layout.addWidget(card_frame, row, col)

        except Exception as e:
            if self.log_callback:
                self.log_callback(f"创建界面时出错: {str(e)}", "error")

    def _create_single_card(self, dups, group_number):
        """创建单个卡片"""
        try:
            # 创建卡片框架
            card_frame = QFrame()
            card_frame.setStyleSheet("""
                QFrame {
                    background-color: #1B1B1B;
                    border: 1px solid #353535;
                    border-radius: 5px;
                    padding: 8px;
                }
                QFrame:selected {
                    background-color: #2D2D2D;
                    border: 1px solid #FF8C00;
                }
            """)
            card_frame.setCursor(Qt.CursorShape.PointingHandCursor)
            
            # 存储引用和选择状态
            card_frame.group_files = dups
            card_frame.is_selected = False
            
            # 连接鼠标点击事件
            card_frame.mousePressEvent = lambda event, cf=card_frame: self._on_card_clicked(cf, event)
            
            card_layout = QVBoxLayout(card_frame)
            card_layout.setContentsMargins(8, 8, 8, 8)
            card_layout.setSpacing(8)

            # 存储引用
            self.card_frames_map[card_frame] = dups

            # 创建卡片内容
            self._create_card_header(card_frame, dups, group_number, card_layout)
            self._create_card_images(card_frame, dups, card_layout)

            return card_frame

        except Exception as e:
            print(f"创建单个卡片时出错: {e}")
            # 返回一个简单的框架以防出错
            error_frame = QFrame()
            error_layout = QVBoxLayout(error_frame)
            error_label = QLabel("Error creating card")
            error_label.setStyleSheet("color: red;")
            error_layout.addWidget(error_label)
            return error_frame

    def _create_card_header(self, card_frame, dups, group_number, card_layout):
        """创建卡片头部"""
        header_frame = QFrame()
        header_layout = QHBoxLayout(header_frame)
        header_layout.setContentsMargins(0, 0, 0, 0)
        
        # 选择复选框
        group_var = BooleanVar(value=False)
        group_check = QCheckBox()
        group_check.stateChanged.connect(lambda state, g=dups, v=group_var: self.toggle_group_selection(g, v))
        header_layout.addWidget(group_check)

        # 组信息
        group_info = QLabel(f"重复组 {group_number} ({len(dups)}张)")
        group_info.setStyleSheet("color: white;")
        header_layout.addWidget(group_info)
        header_layout.addStretch()

        # 置信度标签
        confidence_label = QLabel("高置信度")
        confidence_label.setStyleSheet("color: #198754;")
        header_layout.addWidget(confidence_label)
        
        card_layout.addWidget(header_frame)

    def _create_card_images(self, card_frame, dups, card_layout):
        """创建卡片图片区域"""
        image_frame = QFrame()
        image_layout = QHBoxLayout(image_frame)
        image_layout.setContentsMargins(0, 0, 0, 0)
        
        # 显示前2张图片
        for i in range(min(2, len(dups))):
            self._create_single_image(image_frame, dups[i], i == 1 and len(dups) > 2, dups, image_layout)

        card_layout.addWidget(image_frame)

    def _create_single_image(self, parent_frame, file_path, show_stack, dups, image_layout):
        """创建单个图片显示"""
        try:
            # 创建图片标签容器
            img_container = QFrame()
            img_container.setStyleSheet("background-color: #1B1B1B;")
            img_container.setFixedSize(90, 90)
            container_layout = QVBoxLayout(img_container)
            container_layout.setContentsMargins(2, 2, 2, 2)
            
            # 使用保持比例的图片加载
            pixmap = self._get_cached_pixmap_with_aspect_ratio(file_path, max_size=80)
            if pixmap:
                img_label = QLabel()
                img_label.setPixmap(pixmap)
                img_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
                img_label.setStyleSheet("background-color: #1B1B1B;")
                container_layout.addWidget(img_label)

            image_layout.addWidget(img_container)

        except Exception as e:
            # 错误占位符
            error_label = QLabel("无法显示")
            error_label.setStyleSheet("color: red;")
            error_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            image_layout.addWidget(error_label)

    def _get_cached_pixmap_with_aspect_ratio(self, file_path, max_size=80):
        """
        获取保持原始比例的缓存图片
        """
        try:
            # 打开图片并调整大小
            with Image.open(file_path) as img:
                # 获取原始尺寸
                original_width, original_height = img.size

                # 计算保持比例的新尺寸
                if original_width > original_height:
                    # 横向图片
                    new_width = max_size
                    new_height = int(original_height * (max_size / original_width))
                else:
                    # 纵向图片
                    new_height = max_size
                    new_width = int(original_width * (max_size / original_height))

                # 确保最小尺寸
                new_width = max(new_width, 1)
                new_height = max(new_height, 1)

                # 调整图片大小
                img_resized = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
                
                # 转换为QPixmap
                qimage = ImageQt.ImageQt(img_resized)
                pixmap = QPixmap.fromImage(qimage)
                
                return pixmap

        except Exception as e:
            print(f"无法加载图片 {file_path}: {e}")
            return None

    def _on_card_clicked(self, card_frame, event):
        """处理卡片点击事件"""
        # 检查是否是左键点击
        if event.button() == Qt.MouseButton.LeftButton:
            # 切换选中状态
            card_frame.is_selected = not card_frame.is_selected
            self._update_card_selection_style(card_frame)
            
            # 更新选择计数
            self._update_selection_count()

    def _update_card_selection_style(self, card_frame):
        """更新卡片选中样式"""
        if card_frame.is_selected:
            card_frame.setStyleSheet("""
                QFrame {
                    background-color: #2D2D2D;
                    border: 1px solid #FF8C00;
                    border-radius: 5px;
                    padding: 8px;
                }
            """)
        else:
            card_frame.setStyleSheet("""
                QFrame {
                    background-color: #1B1B1B;
                    border: 1px solid #353535;
                    border-radius: 5px;
                    padding: 8px;
                }
                QFrame:hover {
                    border: 1px solid #555555;
                }
            """)

    def _update_selection_count(self):
        """更新选择计数"""
        selected_count = sum(1 for card in self.card_frames_map.keys() if getattr(card, 'is_selected', False))
        if hasattr(self, 'selection_count_label') and self.selection_count_label:
            self.selection_count_label.setText(f"Selected: {selected_count}")

    def toggle_group_selection(self, group_files, checkbox_var):
        """Toggle selection of entire group"""
        # Simplified implementation, actual implementation needs to handle checkbox state
        pass

    def select_all_images(self):
        """Select all images"""
        for card_frame in self.card_frames_map.keys():
            if hasattr(card_frame, 'is_selected'):
                card_frame.is_selected = True
                self._update_card_selection_style(card_frame)
        self._update_selection_count()

    def unselect_all_images(self):
        """Unselect all images"""
        for card_frame in self.card_frames_map.keys():
            if hasattr(card_frame, 'is_selected'):
                card_frame.is_selected = False
                self._update_card_selection_style(card_frame)
        self._update_selection_count()

    def delete_selected_files_advanced(self):
        """Advanced delete function"""
        pass

    def move_selected_files_advanced(self):
        """Advanced move function"""
        pass
    
    def toggle_log_visibility(self):
        """Toggle log area visibility"""
        self.log_visible = not self.log_visible
        self.log_frame.setVisible(self.log_visible)
        if self.log_visible:
            self.toggle_log_btn.setText(" Hide Log")
        else:
            self.toggle_log_btn.setText(" Show Log")

    def _find_duplicates_progressive(self, hashes, threshold):
        """
        Find duplicate images group by group
        """
        from collections import defaultdict

        if not hashes:
            return {}

        files_to_check = list(hashes.keys())
        duplicates = defaultdict(list)

        for i in range(len(files_to_check)):
            if not self.is_running:
                break
            f1 = files_to_check[i]

            for j in range(i + 1, len(files_to_check)):
                if not self.is_running:
                    break
                f2 = files_to_check[j]

                if hashes[f1] - hashes[f2] <= threshold:
                    if not duplicates[f1]:
                        duplicates[f1].append(f1)
                    duplicates[f1].append(f2)

        return duplicates

    class _ImageCache:
        """
        图片缓存管理器
        """
        def __init__(self, max_size=100):
            self.max_size = max_size
            self._cache = {}  # 缓存字典
            self._access_order = []  # 访问顺序，用于LRU淘汰

        def clear(self):
            """清空缓存"""
            self._cache.clear()
            self._access_order.clear()