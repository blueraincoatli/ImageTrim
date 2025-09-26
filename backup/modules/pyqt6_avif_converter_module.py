
"""
PyQt6 AVIF Converter Function Module
"""

import os
import threading
from typing import Dict, Any
from datetime import datetime
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
                             QLabel, QPushButton, QCheckBox, QSlider, QSpinBox,
                             QDoubleSpinBox, QComboBox, QLineEdit, QTextEdit,
                             QProgressBar, QScrollArea, QFrame, QListWidget,
                             QFileDialog, QMessageBox, QGroupBox, QApplication,
                             QGraphicsView, QGraphicsScene, QGraphicsPixmapItem)
from PyQt6.QtCore import Qt, pyqtSignal, QObject, pyqtSlot
from PyQt6.QtGui import QPixmap, QFont, QColor, QPalette, QImage

try:
    from PIL import Image, ImageQt
except ImportError as e:
    print(f"错误: 必要的库未安装。{e}")
    exit()

from modules.pyqt6_base_module import PyQt6BaseFunctionModule
from ui.pyqt6_adapter import Variable, StringVar, IntVar, DoubleVar, BooleanVar


class PyQt6AVIFConverterModule(PyQt6BaseFunctionModule):
    """PyQt6版本AVIF格式转换功能模块"""

    def __init__(self):
        super().__init__(
            name="pyqt6_avif_converter",
            display_name="AVIF Converter",
            description="Convert images to AVIF format to save storage space.",
            icon="🔄"
        )
        self.convert_thread = None
        self.is_running = False
        self.workspace_root = None
        self.settings_root = None
        # 统计信息
        self.total_files = 0
        self.converted_files = 0
        self.failed_files = 0

    def create_settings_ui(self, parent: QWidget) -> QWidget:
        """创建设置UI面板（中栏）"""
        self.settings_root = parent
        settings_frame = QWidget(parent)
        settings_layout = QVBoxLayout(settings_frame)
        settings_layout.setContentsMargins(10, 10, 10, 10)

        # 1. 源路径和目标路径
        source_frame = QGroupBox("Source Path")
        source_frame.setStyleSheet("QGroupBox { background-color: #1B1B1B; color: white; border: 1px solid #353535; font-weight: bold; }")
        source_layout = QHBoxLayout(source_frame)
        source_layout.setContentsMargins(10, 20, 10, 10)

        self.source_path_var = StringVar(value="")
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

        source_browse_btn = QPushButton("Browse")
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
        source_browse_btn.clicked.connect(self.browse_source_folder)
        source_layout.addWidget(source_browse_btn)

        target_frame = QGroupBox("Target Path")
        target_frame.setStyleSheet("QGroupBox { background-color: #1B1B1B; color: white; border: 1px solid #353535; font-weight: bold; }")
        target_layout = QHBoxLayout(target_frame)
        target_layout.setContentsMargins(10, 20, 10, 10)

        self.target_path_var = StringVar(value="")
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

        target_browse_btn = QPushButton("Browse")
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
        target_browse_btn.clicked.connect(self.browse_target_folder)
        target_layout.addWidget(target_browse_btn)

        # 2. 转换设置
        options_frame = QGroupBox("Conversion Settings")
        options_frame.setStyleSheet("QGroupBox { background-color: #1B1B1B; color: white; border: 1px solid #353535; font-weight: bold; }")
        options_layout = QVBoxLayout(options_frame)
        options_layout.setContentsMargins(10, 20, 10, 10)

        quality_frame = QWidget()
        quality_layout = QHBoxLayout(quality_frame)
        quality_layout.setContentsMargins(0, 0, 0, 0)
        quality_label = QLabel("Quality:")
        quality_label.setStyleSheet("color: white;")
        quality_layout.addWidget(quality_label)
        
        self.quality_var = IntVar(value=85)
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
        self.quality_scale.valueChanged.connect(self.on_quality_changed)
        quality_layout.addWidget(self.quality_scale)
        
        self.quality_value_label = QLabel("85%")
        self.quality_value_label.setStyleSheet("color: white;")
        self.quality_value_label.setFixedWidth(40)
        quality_layout.addWidget(self.quality_value_label)
        
        options_layout.addWidget(quality_frame)

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
        
        self.start_btn = QPushButton("▶️ Start Conversion")
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
        self.start_btn.clicked.connect(self.start_conversion)
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
        
        # Add all components to the settings layout
        settings_layout.addWidget(source_frame)
        settings_layout.addWidget(target_frame)
        settings_layout.addWidget(options_frame)
        settings_layout.addWidget(action_frame)
        settings_layout.addStretch()

        return settings_frame

    def on_quality_changed(self, value):
        """Handle quality slider changes"""
        self.quality_value_label.setText(f"{value}%")
        self.quality_var.value = value

    def create_workspace_ui(self, parent: QWidget) -> QWidget:
        """Create workspace UI panel (right column)"""
        self.workspace_root = parent
        workspace_frame = QWidget(parent)
        workspace_layout = QVBoxLayout(workspace_frame)
        workspace_layout.setContentsMargins(10, 10, 10, 10)
        
        # Progress and statistics area
        progress_frame = QWidget()
        progress_layout = QHBoxLayout(progress_frame)
        progress_layout.setContentsMargins(0, 0, 0, 0)
        self.progress_label = QLabel("Conversion not started yet.")
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
        
        # Statistics information
        stats_frame = QWidget()
        stats_layout = QHBoxLayout(stats_frame)
        stats_layout.setContentsMargins(0, 0, 0, 0)
        self.stats_label = QLabel("Files: 0 | Converted: 0 | Failed: 0")
        self.stats_label.setStyleSheet("color: white;")
        stats_layout.addWidget(self.stats_label)
        
        workspace_layout.addWidget(stats_frame)
        
        # Current conversion image preview area
        preview_frame = QGroupBox("Current Conversion")
        preview_frame.setStyleSheet("QGroupBox { background-color: #1B1B1B; color: white; border: 1px solid #353535; font-weight: bold; }")
        preview_layout = QVBoxLayout(preview_frame)
        preview_layout.setContentsMargins(10, 20, 10, 10)
        
        # Create left and right sub-frames
        preview_content_frame = QWidget()
        preview_content_layout = QHBoxLayout(preview_content_frame)
        preview_content_layout.setContentsMargins(0, 0, 0, 0)
        
        # Left: Source image preview
        source_preview_frame = QGroupBox("Source Image")
        source_preview_frame.setStyleSheet("QGroupBox { background-color: #1B1B1B; color: white; border: 1px solid #353535; font-weight: bold; }")
        source_preview_layout = QVBoxLayout(source_preview_frame)
        source_preview_layout.setContentsMargins(10, 20, 10, 10)
        
        self.source_preview_label = QLabel("No image")
        self.source_preview_label.setStyleSheet("color: #6c757d;")
        self.source_preview_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        source_preview_layout.addWidget(self.source_preview_label)
        
        # Right: Target image information
        target_preview_frame = QGroupBox("Target Info")
        target_preview_frame.setStyleSheet("QGroupBox { background-color: #1B1B1B; color: white; border: 1px solid #353535; font-weight: bold; }")
        target_preview_layout = QVBoxLayout(target_preview_frame)
        target_preview_layout.setContentsMargins(10, 20, 10, 10)
        
        self.target_info_label = QLabel("AVIF output")
        self.target_info_label.setStyleSheet("color: #6c757d;")
        self.target_info_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        target_preview_layout.addWidget(self.target_info_label)
        
        preview_content_layout.addWidget(source_preview_frame)
        preview_content_layout.addWidget(target_preview_frame)
        
        preview_layout.addWidget(preview_content_frame)
        
        workspace_layout.addWidget(preview_frame)
        
        # Compression ratio display area
        self.compression_frame = QGroupBox("Compression Ratio")
        self.compression_frame.setStyleSheet("QGroupBox { background-color: #1B1B1B; color: white; border: 1px solid #353535; font-weight: bold; }")
        compression_layout = QVBoxLayout(self.compression_frame)
        compression_layout.setContentsMargins(10, 20, 10, 10)
        
        # Compression ratio information
        self.compression_info_label = QLabel("No conversion data available")
        self.compression_info_label.setStyleSheet("color: #6c757d;")
        self.compression_info_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        compression_layout.addWidget(self.compression_info_label)
        
        workspace_layout.addWidget(self.compression_frame)
        
        # Log area
        log_frame = QGroupBox("Conversion Log")
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
        
        return workspace_frame

    def browse_source_folder(self):
        """Browse source folder"""
        path = QFileDialog.getExistingDirectory(None, "Select Source Directory")
        if path:
            self.source_path_var.value = path
            self.source_entry.setText(path)

    def browse_target_folder(self):
        """Browse target folder"""
        path = QFileDialog.getExistingDirectory(None, "Select Target Directory")
        if path:
            self.target_path_var.value = path
            self.target_entry.setText(path)

    def start_conversion(self):
        """Start conversion"""
        source_path = self.source_entry.text()
        target_path = self.target_entry.text()
        
        if not source_path or not os.path.isdir(source_path):
            QMessageBox.critical(None, "Invalid Path", "Please enter a valid source folder path.")
            return
            
        if not target_path:
            QMessageBox.critical(None, "Invalid Path", "Please enter a valid target folder path.")
            return

        params = {
            'source_path': source_path,
            'target_path': target_path,
            'quality': self.quality_var.value,
            'subdirs': self.subdirs_var.value
        }

        self.is_running = True
        self.start_btn.setEnabled(False)
        self.stop_btn.setEnabled(True)
        self.progress_bar.setValue(0)
        
        # Reset statistics
        self.total_files = 0
        self.converted_files = 0
        self.failed_files = 0
        self.stats_label.setText(f"Files: {self.total_files} | Converted: {self.converted_files} | Failed: {self.failed_files}")
        
        # Clear preview area and compression ratio display
        self._clear_preview()

        self.convert_thread = threading.Thread(target=self.execute, args=(params,))
        self.convert_thread.daemon = True
        self.convert_thread.start()
        
    def _clear_preview(self):
        """清除预览区域"""
        if self.source_preview_label:
            self.source_preview_label.setText("No image")
        if self.target_info_label:
            self.target_info_label.setText("AVIF output")
        if self.compression_info_label:
            self.compression_info_label.setText("No conversion data available")
            
    def stop_execution(self):
        """停止执行"""
        self.is_running = False

    def log_message(self, message: str, level: str = "info"):
        """Display message in log area"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        formatted_message = f"[{timestamp}] [{level.upper()}] {message}"
        # Check if log_text widget still exists and is valid using the base class method
        if hasattr(self, 'log_text') and self._is_widget_valid(self.log_text):
            try:
                self.log_text.append(formatted_message)
            except RuntimeError:
                # Widget has been deleted, clear the reference
                self.log_text = None

    def execute(self, params: Dict[str, Any]):
        """Execute conversion"""
        try:
            source_path = params['source_path']
            target_path = params['target_path']
            quality = params['quality']
            scan_subdirs = params['subdirs']
            
            # Initialize statistics
            self.total_files = 0
            self.converted_files = 0
            self.failed_files = 0
            
            # Collect files to convert
            image_files = []
            valid_extensions = ('.png', '.jpg', '.jpeg', '.bmp', '.gif', '.webp')
            
            if scan_subdirs:
                for root, _, files in os.walk(source_path):
                    if not self.is_running: 
                        self.log_message("Conversion stopped", "info")
                        return
                    for file in files:
                        if file.lower().endswith(valid_extensions):
                            image_files.append((os.path.join(root, file), root))
            else:
                for file in os.listdir(source_path):
                    if not self.is_running: 
                        self.log_message("Conversion stopped", "info")
                        return
                    if file.lower().endswith(valid_extensions):
                        image_files.append((os.path.join(source_path, file), source_path))
            
            if not image_files:
                self.log_message("No image files found for conversion", "warning")
                return
                
            self.total_files = len(image_files)
            self.log_message(f"Found {self.total_files} files for conversion", "info")
            
            # Update progress label and statistics
            self.progress_label.setText(f"Converting: 0/{self.total_files}")
            self.stats_label.setText(f"Files: {self.total_files} | Converted: {self.converted_files} | Failed: {self.failed_files}")
            
            # Convert files
            last_converted_source = None
            last_converted_target = None
            
            for i, (file_path, original_dir) in enumerate(image_files):
                if not self.is_running: 
                    self.log_message("Conversion stopped", "info")
                    break
                    
                try:
                    # Show preview of current conversion image
                    self._show_preview(file_path)
                    
                    # Calculate target path
                    relative_path = os.path.relpath(original_dir, source_path)
                    target_dir = os.path.join(target_path, relative_path) if relative_path != '.' else target_path
                    os.makedirs(target_dir, exist_ok=True)
                    
                    # Generate target filename
                    base_name = os.path.splitext(os.path.basename(file_path))[0]
                    target_file = os.path.join(target_dir, f"{base_name}.avif")
                    
                    # Save original target file path for duplicate handling
                    original_target_file = target_file
                    
                    # Check if already exists
                    if os.path.exists(target_file):
                        counter = 1
                        while os.path.exists(os.path.join(target_dir, f"{base_name}_{counter}.avif")):
                            counter += 1
                        target_file = os.path.join(target_dir, f"{base_name}_{counter}.avif")
                    
                    # Convert image
                    with Image.open(file_path) as img:
                        # Handle RGBA mode images
                        if img.mode == 'RGBA':
                            # Create white background
                            background = Image.new('RGB', img.size, (255, 255, 255))
                            background.paste(img, mask=img.split()[-1])
                            img = background
                        elif img.mode != 'RGB':
                            img = img.convert('RGB')
                            
                        img.save(target_file, 'AVIF', quality=quality)
                    
                    self.converted_files += 1
                    self.log_message(f"Converted: {os.path.basename(file_path)} -> {os.path.basename(target_file)}", "success")
                    
                    # Save last converted file paths for compression ratio display
                    last_converted_source = file_path
                    last_converted_target = target_file
                    
                    # Update progress and statistics
                    progress = (i + 1) / self.total_files * 100
                    self.progress_bar.setValue(int(progress))
                    self.progress_label.setText(f"Converting: {self.converted_files}/{self.total_files}")
                    self.stats_label.setText(f"Files: {self.total_files} | Converted: {self.converted_files} | Failed: {self.failed_files}")
                    
                except Exception as e:
                    self.failed_files += 1
                    self.log_message(f"Conversion failed {os.path.basename(file_path)}: {str(e)}", "error")
                    # Update statistics
                    self.stats_label.setText(f"Files: {self.total_files} | Converted: {self.converted_files} | Failed: {self.failed_files}")
            
            # Display compression ratio of the last image
            if last_converted_source and last_converted_target:
                self._show_compression_ratio(last_converted_source, last_converted_target)
            
            # Complete
            self.log_message(f"Conversion completed! Successfully converted {self.converted_files}/{self.total_files} files", "info")
            
        except Exception as e:
            self.log_message(f"Error during conversion: {str(e)}", "error")
        finally:
            self.is_running = False
            if self.settings_root:
                self.start_btn.setEnabled(True)
                self.stop_btn.setEnabled(False)

    def _show_preview(self, file_path: str):
        """Show preview of current conversion image"""
        try:
            # Load and display image
            pixmap = QPixmap(file_path)
            
            # Adjust image size to fit preview area
            max_size = 200
            if pixmap.width() > pixmap.height():
                if pixmap.width() > max_size:
                    pixmap = pixmap.scaledToWidth(max_size, Qt.TransformationMode.SmoothTransformation)
            else:
                if pixmap.height() > max_size:
                    pixmap = pixmap.scaledToHeight(max_size, Qt.TransformationMode.SmoothTransformation)
            
            # Update source image preview label
            self.source_preview_label.setPixmap(pixmap)
            self.source_preview_label.setText("")
            
            # Update target information
            file_size = os.path.getsize(file_path)
            file_size_mb = file_size / (1024 * 1024)
            file_name = os.path.basename(file_path)
            file_ext = os.path.splitext(file_name)[1].upper()
            
            info_text = f"File: {file_name}\nSize: {file_size_mb:.2f} MB\nFormat: {file_ext}\n\nTarget: AVIF"
            self.target_info_label.setText(info_text)
            
        except Exception as e:
            self.source_preview_label.setText("Cannot preview image")
            self.target_info_label.setText(f"Error loading preview:\n{str(e)}")

    def _show_compression_ratio(self, source_path: str, target_path: str):
        """Show compression ratio display"""
        try:
            # Get source and target file sizes
            source_size = os.path.getsize(source_path)
            target_size = os.path.getsize(target_path)
            
            # Calculate compression ratio
            if source_size > 0:
                compression_ratio = (1 - target_size / source_size) * 100
                size_reduction = source_size - target_size
                
                # Format size display
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
                
                # Update compression ratio information label
                info_text = f"Source: {source_size_str} → Target: {target_size_str}\n"
                info_text += f"Size reduction: {reduction_str} ({compression_ratio:.1f}% smaller)"
                self.compression_info_label.setText(info_text)
                
            else:
                self.compression_info_label.setText("Source file size is 0")
                
        except Exception as e:
            self.compression_info_label.setText(f"Error calculating compression ratio: {str(e)}")