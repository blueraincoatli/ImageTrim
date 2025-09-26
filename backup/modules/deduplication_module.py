"""
PyQt6图片去重功能模块
"""

import os
import threading
from typing import Dict, Any, List, Optional
from datetime import datetime
from collections import defaultdict
from pathlib import Path

from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
                             QLabel, QPushButton, QCheckBox, QSlider, QSpinBox,
                             QDoubleSpinBox, QComboBox, QLineEdit, QTextEdit,
                             QProgressBar, QScrollArea, QFrame, QListWidget,
                             QFileDialog, QMessageBox, QGroupBox)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QPixmap, QFont

try:
    from PIL import Image, ImageQt
    import imagehash
    import numpy as np
except ImportError as e:
    print(f"错误: 必要的库未安装。{e}")
    exit()

from modules.base_function_module import BaseFunctionModule


class DeduplicationModule(BaseFunctionModule):
    """PyQt6版本图片去重功能模块"""
    
    def __init__(self):
        super().__init__(
            name="deduplication",
            display_name="图片去重",
            description="查找并处理重复或相似的图片",
            icon="🔍"
        )
        self.scan_thread: Optional[threading.Thread] = None
        self.is_running = False
        self.workspace_widget: Optional[QWidget] = None
        self.settings_widget: Optional[QWidget] = None
        
        # UI组件引用
        self.paths_listbox: Optional[QListWidget] = None
        self.sens_scale: Optional[QSlider] = None
        self.sens_value_label: Optional[QLabel] = None
        self.subdirs_check: Optional[QCheckBox] = None
        self.start_btn: Optional[QPushButton] = None
        self.stop_btn: Optional[QPushButton] = None
        self.progress_bar: Optional[QProgressBar] = None
        self.stats_label: Optional[QLabel] = None
        self.log_text: Optional[QTextEdit] = None
        self.scrollable_frame: Optional[QWidget] = None
        
        # 参数变量
        self.sensitivity = 95.0
        self.include_subdirs = True

    def create_settings_ui(self) -> QWidget:
        """创建设置UI面板（中栏）"""
        if self.settings_widget:
            return self.settings_widget
            
        self.settings_widget = QWidget()
        settings_layout = QVBoxLayout(self.settings_widget)
        settings_layout.setContentsMargins(10, 10, 10, 10)

        # 1. 扫描路径（支持多个路径）
        paths_frame = QGroupBox("扫描路径")
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
        
        add_path_btn = QPushButton("添加路径")
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
        add_path_btn.clicked.connect(self._add_folder)
        path_btn_layout.addWidget(add_path_btn)
        
        remove_path_btn = QPushButton("移除路径")
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
        remove_path_btn.clicked.connect(self._remove_folder)
        path_btn_layout.addWidget(remove_path_btn)
        
        clear_paths_btn = QPushButton("清空路径")
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
        clear_paths_btn.clicked.connect(self._clear_folders)
        path_btn_layout.addWidget(clear_paths_btn)
        
        paths_layout.addWidget(path_btn_frame)

        # 2. 检测设置
        options_frame = QGroupBox("检测设置")
        options_frame.setStyleSheet("QGroupBox { background-color: #1B1B1B; color: white; border: 1px solid #353535; font-weight: bold; }")
        options_layout = QVBoxLayout(options_frame)
        options_layout.setContentsMargins(10, 20, 10, 10)

        sens_frame = QWidget()
        sens_layout = QHBoxLayout(sens_frame)
        sens_layout.setContentsMargins(0, 0, 0, 0)
        sens_label = QLabel("相似度阈值:")
        sens_layout.addWidget(sens_label)
        
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
        self.sens_scale.valueChanged.connect(self._on_sensitivity_changed)
        sens_layout.addWidget(self.sens_scale)
        
        self.sens_value_label = QLabel("95%")
        self.sens_value_label.setFixedWidth(40)
        sens_layout.addWidget(self.sens_value_label)
        
        options_layout.addWidget(sens_frame)

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
        
        self.start_btn = QPushButton("▶️ 开始扫描")
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
        self.start_btn.clicked.connect(self._start_scan)
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
        settings_layout.addWidget(paths_frame)
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
        
        # 进度区域
        progress_frame = QWidget()
        progress_layout = QHBoxLayout(progress_frame)
        progress_layout.setContentsMargins(0, 0, 0, 0)
        self.stats_label = QLabel("扫描尚未开始。")
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
        
        # 日志区域
        log_frame = QGroupBox("处理日志")
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
                min-height: 100px;
            }
        """)
        self.log_text.setReadOnly(True)
        log_layout.addWidget(self.log_text)
        
        workspace_layout.addWidget(log_frame)
        
        # 结果区域
        result_label = QLabel("扫描结果")
        result_label.setStyleSheet("color: white; font-size: 16px; font-weight: bold;")
        workspace_layout.addWidget(result_label)
        
        # 结果滚动区域
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
        
        workspace_layout.addWidget(self.scroll_area)
        
        return self.workspace_widget

    def _on_sensitivity_changed(self, value: int):
        """处理敏感度滑块变化"""
        self.sens_value_label.setText(f"{value}%")
        self.sensitivity = float(value)

    def _on_subdirs_changed(self, state: int):
        """处理包含子目录选项变化"""
        self.include_subdirs = state == Qt.CheckState.Checked.value

    def _add_folder(self):
        """添加文件夹"""
        path = QFileDialog.getExistingDirectory(None, "选择目录")
        if path and path not in [self.paths_listbox.item(i).text() for i in range(self.paths_listbox.count())]:
            self.paths_listbox.addItem(path)
            
    def _remove_folder(self):
        """移除文件夹"""
        current_row = self.paths_listbox.currentRow()
        if current_row >= 0:
            self.paths_listbox.takeItem(current_row)
            
    def _clear_folders(self):
        """清空文件夹列表"""
        self.paths_listbox.clear()

    def _start_scan(self):
        """开始扫描"""
        print("开始扫描按钮被点击")
        
        # 获取所有扫描路径
        paths = [self.paths_listbox.item(i).text() for i in range(self.paths_listbox.count())]
        print(f"获取到路径列表: {paths}")
        
        if not paths:
            print("路径列表为空")
            QMessageBox.critical(None, "无效路径", "请至少添加一个有效的文件夹路径。")
            return
            
        # 验证所有路径都有效
        for path in paths:
            if not os.path.isdir(path):
                print(f"路径无效: {path}")
                QMessageBox.critical(None, "无效路径", f"路径不存在或无效: {path}")
                return

        params = {
            'paths': paths,
            'sensitivity': self.sensitivity,
            'subdirs': self.include_subdirs
        }

        print(f"准备启动扫描线程，参数: {params}")
        self.is_running = True
        self.start_btn.setEnabled(False)
        self.stop_btn.setEnabled(True)

        # 清空结果区域
        self._clear_results()

        # 发送开始日志消息
        self.log_message.emit("开始扫描...", "info")

        self.scan_thread = threading.Thread(target=self.execute, args=(params,))
        self.scan_thread.daemon = True
        print("启动扫描线程")
        self.scan_thread.start()
        print("扫描线程已启动")

    def stop_execution(self):
        """停止执行"""
        self.is_running = False

    def execute(self, params: Dict[str, Any]):
        """执行扫描"""
        print("execute方法被调用")
        try:
            scan_paths = params['paths']
            threshold = 100 - params['sensitivity']
            scan_subdirs = params['subdirs']
            print(f"参数解析完成: paths={scan_paths}, threshold={threshold}, subdirs={scan_subdirs}")

            # 收集所有图片文件
            image_files = []
            valid_extensions = ('.png', '.jpg', '.jpeg', '.bmp', '.gif', '.webp')
            
            total_paths = len(scan_paths)
            print(f"开始扫描路径，总路径数: {total_paths}")
            for path_idx, scan_path in enumerate(scan_paths):
                if not self.is_running: 
                    self.log_message.emit("扫描被用户停止", "info")
                    break
                
                # 更新进度信息
                self.log_message.emit(f"正在扫描路径 ({path_idx+1}/{total_paths}): {scan_path}", "info")
                
                if scan_subdirs:
                    print(f"扫描子目录: {scan_path}")
                    for root, _, files in os.walk(scan_path):
                        if not self.is_running: 
                            self.log_message.emit("扫描被用户停止", "info")
                            break
                        for file in files:
                            if file.lower().endswith(valid_extensions):
                                image_files.append(os.path.join(root, file))
                else:
                    print(f"扫描当前目录: {scan_path}")
                    for file in os.listdir(scan_path):
                        if not self.is_running: 
                            self.log_message.emit("扫描被用户停止", "info")
                            break
                        if file.lower().endswith(valid_extensions):
                            image_files.append(os.path.join(scan_path, file))
            
            print(f"扫描完成，找到图片文件数: {len(image_files)}")
            if not self.is_running: 
                return

            # 计算哈希值
            hashes = {}
            total_files = len(image_files)
            
            self.log_message.emit(f"找到 {total_files} 个图片文件，开始计算哈希值...", "info")
            
            for i, f in enumerate(image_files):
                if not self.is_running: 
                    self.log_message.emit("扫描被用户停止", "info")
                    break
                
                # 更新进度
                progress = (i + 1) / total_files * 100
                self.progress_updated.emit(progress, f"计算哈希值: {i+1}/{total_files}")
                
                try:
                    # 使用改进的哈希算法
                    hash_value = self._calculate_improved_hash(f)
                    if hash_value is not None:
                        hashes[f] = hash_value
                except Exception as e:
                    self.log_message.emit(f"无法处理图片 {f}: {str(e)}", "warning")
            
            print(f"哈希计算完成，有效哈希数: {len(hashes)}")
            if not self.is_running: 
                return

            # 查找重复项
            self.log_message.emit("正在查找重复图片...", "info")
            self.log_message.emit(f"哈希值数量: {len(hashes)}, 阈值: {threshold}", "info")

            # 查找重复图片
            duplicates = self._find_duplicates(hashes, threshold)

            self.log_message.emit(f"找到重复组数量: {len(duplicates)}", "info")

            if not self.is_running: 
                return

            # 显示结果
            self._display_results(duplicates)

        except Exception as e:
            self.log_message.emit(f"执行过程中出错: {str(e)}", "error")
            print(f"Error during execution: {e}")
            import traceback
            traceback.print_exc()
        finally:
            self.is_running = False
            self.start_btn.setEnabled(True)
            self.stop_btn.setEnabled(False)
            
            # 完成消息
            self.log_message.emit("扫描完成", "info")

    def _calculate_improved_hash(self, file_path: str) -> Optional[int]:
        """
        计算改进的图片哈希值
        
        Args:
            file_path: 图片文件路径
            
        Returns:
            int: 哈希值，失败返回None
        """
        try:
            with Image.open(file_path) as img:
                # 转换为RGB模式（处理RGBA等格式）
                if img.mode in ('RGBA', 'LA', 'P'):
                    # 创建白色背景
                    background = Image.new('RGB', img.size, (255, 255, 255))
                    if img.mode == 'RGBA':
                        background.paste(img, mask=img.split()[-1])
                    else:
                        background.paste(img)
                    img = background
                elif img.mode != 'RGB':
                    img = img.convert('RGB')
                
                # 计算多个哈希值并组合
                # 1. 感知哈希
                phash = imagehash.phash(img, hash_size=16)  # 增加哈希大小提高精度
                
                # 2. 平均哈希
                ahash = imagehash.average_hash(img, hash_size=16)
                
                # 3. 差异哈希
                dhash = imagehash.dhash(img, hash_size=16)
                
                # 4. 色彩直方图
                hist = img.histogram()
                # 取每种颜色的前10个值
                hist_hash = sum(hist[:30]) % (2**63)
                
                # 组合所有哈希值
                combined_hash = (int(str(phash), 16) ^ 
                               int(str(ahash), 16) ^ 
                               int(str(dhash), 16) ^ 
                               hist_hash)
                
                return combined_hash
                
        except Exception as e:
            print(f"计算哈希值失败 {file_path}: {e}")
            return None

    def _find_duplicates(self, hashes: Dict[str, int], threshold: float) -> Dict[str, List[str]]:
        """
        查找重复图片
        
        Args:
            hashes: 图片路径到哈希值的映射
            threshold: 相似度阈值
            
        Returns:
            Dict[str, List[str]]: 重复组字典
        """
        duplicates = defaultdict(list)
        files_list = list(hashes.keys())
        
        # 使用更高效的算法查找重复项
        processed_files = set()
        
        for i, f1 in enumerate(files_list):
            if not self.is_running:
                break
                
            if f1 in processed_files:
                continue
                
            # 计算当前文件与所有后续文件的相似度
            group = [f1]
            processed_files.add(f1)
            
            for j in range(i + 1, len(files_list)):
                if not self.is_running:
                    break
                    
                f2 = files_list[j]
                if f2 in processed_files:
                    continue
                    
                # 计算哈希值差异
                hash_diff = abs(hashes[f1] - hashes[f2])
                
                # 转换为相似度百分比 (简化计算)
                similarity = max(0, 100 - (hash_diff / (2**60)) * 100)
                
                if similarity >= (100 - threshold):
                    group.append(f2)
                    processed_files.add(f2)
            
            # 如果找到重复项，添加到结果中
            if len(group) > 1:
                duplicates[group[0]] = group
                
        return duplicates

    def _clear_results(self):
        """清空结果区域"""
        try:
            # 清空滚动区域的内容
            if self.scrollable_frame.layout():
                for i in reversed(range(self.scrollable_frame.layout().count())):
                    widget = self.scrollable_frame.layout().itemAt(i).widget()
                    if widget:
                        widget.setParent(None)
        except Exception:
            pass

    def _display_results(self, duplicates: Dict[str, List[str]]):
        """显示结果"""
        # 在主线程中更新UI
        from PyQt6.QtCore import QTimer
        QTimer.singleShot(0, lambda: self._update_results_ui(duplicates))
        
    def _update_results_ui(self, duplicates: Dict[str, List[str]]):
        """更新结果UI"""
        # 清空现有结果
        self._clear_results()
        
        if not duplicates:
            self.stats_label.setText("未找到重复图片。")
            message_label = QLabel("恭喜！未在指定目录中找到重复图片。")
            message_label.setStyleSheet("color: white; font-style: italic; padding: 50px;")
            layout = self.scrollable_frame.layout() or QVBoxLayout(self.scrollable_frame)
            layout.addWidget(message_label)
            return

        # 更新统计信息
        num_groups = len(duplicates)
        num_files = sum(len(v) for v in duplicates.values())
        self.stats_label.setText(f"找到 {num_groups} 组重复图片，共 {num_files} 个文件。")

        # 创建主容器
        main_container = QWidget(self.scrollable_frame)
        grid_layout = QGridLayout(main_container)
        grid_layout.setSpacing(10)
        
        # 计算列数
        columns = 3
        
        # 创建所有UI组件
        group_items = list(duplicates.items())
        
        for group_idx, (master, dups) in enumerate(group_items):
            if not self.is_running:
                break

            # 计算网格位置
            row = group_idx // columns
            col = group_idx % columns

            # 创建卡片
            card_frame = self._create_card(dups, group_idx + 1)
            grid_layout.addWidget(card_frame, row, col)

        # 添加到滚动区域
        layout = self.scrollable_frame.layout() or QVBoxLayout(self.scrollable_frame)
        layout.addWidget(main_container)

    def _create_card(self, dups: List[str], group_number: int) -> QFrame:
        """创建重复组卡片"""
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
            """)
            card_layout = QVBoxLayout(card_frame)
            card_layout.setContentsMargins(8, 8, 8, 8)
            card_layout.setSpacing(8)

            # 创建卡片内容
            # 头部信息
            header_frame = QFrame()
            header_layout = QHBoxLayout(header_frame)
            header_layout.setContentsMargins(0, 0, 0, 0)
            
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

            # 图片区域
            image_frame = QFrame()
            image_layout = QHBoxLayout(image_frame)
            image_layout.setContentsMargins(0, 0, 0, 0)
            
            # 显示前2张图片
            for i in range(min(2, len(dups))):
                self._create_image_label(image_frame, dups[i], i == 1 and len(dups) > 2, dups, image_layout)

            card_layout.addWidget(image_frame)

            return card_frame

        except Exception as e:
            print(f"创建卡片时出错: {e}")
            # 返回一个简单的框架以防出错
            error_frame = QFrame()
            error_layout = QVBoxLayout(error_frame)
            error_label = QLabel("Error creating card")
            error_label.setStyleSheet("color: red;")
            error_layout.addWidget(error_label)
            return error_frame

    def _create_image_label(self, parent_frame: QFrame, file_path: str, show_stack: bool, dups: List[str], image_layout: QHBoxLayout):
        """创建图片标签"""
        try:
            # 创建图片标签容器
            img_container = QFrame()
            img_container.setStyleSheet("background-color: #1B1B1B;")
            img_container.setFixedSize(90, 90)
            container_layout = QVBoxLayout(img_container)
            container_layout.setContentsMargins(2, 2, 2, 2)
            
            if show_stack:
                # 显示堆叠图标
                stack_label = QLabel(f"🖼️+{len(dups)-1}")
                stack_label.setStyleSheet("color: white; font-size: 12px;")
                stack_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
                container_layout.addWidget(stack_label)
            else:
                # 显示实际图片
                pixmap = self._get_thumbnail(file_path, max_size=80)
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

    def _get_thumbnail(self, file_path: str, max_size: int = 80) -> Optional[QPixmap]:
        """
        获取缩略图
        
        Args:
            file_path: 图片文件路径
            max_size: 最大尺寸
            
        Returns:
            QPixmap: 缩略图，失败返回None
        """
        try:
            # 打开图片并调整大小
            with Image.open(file_path) as img:
                # 转换为RGB模式（处理RGBA等格式）
                if img.mode in ('RGBA', 'LA', 'P'):
                    # 创建白色背景
                    background = Image.new('RGB', img.size, (255, 255, 255))
                    if img.mode == 'RGBA':
                        background.paste(img, mask=img.split()[-1])
                    else:
                        background.paste(img)
                    img = background
                elif img.mode != 'RGB':
                    img = img.convert('RGB')
                
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