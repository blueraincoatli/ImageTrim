import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os
import threading
from typing import Dict, Any

try:
    import ttkbootstrap as ttkb
    from ttkbootstrap.constants import *
    from PIL import Image, ImageTk
except ImportError:
    print("错误: 必要的库未安装。请运行 'pip install ttkbootstrap Pillow'")
    exit()

from function_modules import BaseFunctionModule

class AVIFConverterModule(BaseFunctionModule):
    """AVIF格式转换功能模块"""

    def __init__(self):
        super().__init__(
            name="avif_converter",
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

    def create_settings_ui(self, parent: ttkb.Frame) -> ttkb.Frame:
        """创建设置UI面板（中栏）"""
        self.settings_root = parent
        settings_frame = ttkb.Frame(parent, padding=10)

        # 1. 源路径和目标路径
        source_frame = ttkb.Labelframe(settings_frame, text="Source Path", padding=10)
        source_frame.pack(fill=X, pady=5, expand=True)

        self.source_path_var = tk.StringVar(value="")
        source_entry = ttkb.Entry(source_frame, textvariable=self.source_path_var)
        source_entry.pack(side=LEFT, fill=X, expand=True, padx=(0, 5))

        source_browse_btn = ttkb.Button(source_frame, text="Browse", command=self.browse_source_folder, bootstyle='secondary')
        source_browse_btn.pack(side=LEFT)

        target_frame = ttkb.Labelframe(settings_frame, text="Target Path", padding=10)
        target_frame.pack(fill=X, pady=5, expand=True)

        self.target_path_var = tk.StringVar(value="")
        target_entry = ttkb.Entry(target_frame, textvariable=self.target_path_var)
        target_entry.pack(side=LEFT, fill=X, expand=True, padx=(0, 5))

        target_browse_btn = ttkb.Button(target_frame, text="Browse", command=self.browse_target_folder, bootstyle='secondary')
        target_browse_btn.pack(side=LEFT)

        # 2. 转换设置
        options_frame = ttkb.Labelframe(settings_frame, text="Conversion Settings", padding=10)
        options_frame.pack(fill=X, pady=5, expand=True)

        quality_frame = ttkb.Frame(options_frame)
        quality_frame.pack(fill=X, pady=5)
        ttkb.Label(quality_frame, text="Quality:").pack(side=LEFT, padx=(0, 10))
        self.quality_var = tk.IntVar(value=85)
        quality_scale = ttkb.Scale(quality_frame, from_=1, to=100, variable=self.quality_var, orient=HORIZONTAL)
        quality_scale.pack(side=LEFT, fill=X, expand=True)
        self.quality_label = ttkb.Label(quality_frame, text="85%", width=5)
        self.quality_label.pack(side=LEFT, padx=(10, 0))
        quality_scale.config(command=lambda val: self.quality_label.config(text=f"{int(float(val))}%"))

        self.subdirs_var = tk.BooleanVar(value=True)
        subdirs_check = ttkb.Checkbutton(options_frame, text="Include Subdirectories", variable=self.subdirs_var, bootstyle='round-toggle')
        subdirs_check.pack(fill=X, pady=5)

        # 3. 操作控制
        action_frame = ttkb.Labelframe(settings_frame, text="Operation Control", padding=10)
        action_frame.pack(fill=X, pady=5, expand=True)

        self.start_btn = ttkb.Button(action_frame, text="▶️ Start Conversion", command=self.start_conversion, bootstyle='success')
        self.start_btn.pack(side=LEFT, fill=X, expand=True, padx=(0, 5))

        self.stop_btn = ttkb.Button(action_frame, text="⏹️ Stop", command=self.stop_execution, bootstyle='danger', state=DISABLED)
        self.stop_btn.pack(side=LEFT, fill=X, expand=True, padx=5)
        
        return settings_frame

    def create_workspace_ui(self, parent: ttkb.Frame) -> ttkb.Frame:
        """创建工作区UI面板（右栏）"""
        self.workspace_root = parent
        workspace_frame = ttkb.Frame(parent, padding=10)
        
        # 进度和统计信息区域
        progress_frame = ttkb.Frame(workspace_frame)
        progress_frame.pack(fill=X, pady=5)
        self.progress_label = ttkb.Label(progress_frame, text="Conversion not started yet.", font=("", 10))
        self.progress_label.pack(anchor=W)
        
        self.progress_bar = ttkb.Progressbar(progress_frame, bootstyle='success-striped')
        self.progress_bar.pack(fill=X, pady=5)
        
        # 统计信息
        stats_frame = ttkb.Frame(workspace_frame)
        stats_frame.pack(fill=X, pady=5)
        self.stats_label = ttkb.Label(stats_frame, text="Files: 0 | Converted: 0 | Failed: 0", font=("", 10))
        self.stats_label.pack(anchor=W)
        
        # 当前转换图片预览区域
        preview_frame = ttkb.Labelframe(workspace_frame, text="Current Conversion", padding=5)
        preview_frame.pack(fill=X, pady=10)
        
        # 创建左右两个子框架
        preview_content_frame = ttkb.Frame(preview_frame)
        preview_content_frame.pack(fill=BOTH, expand=True)
        
        # 左侧：源图片预览
        source_preview_frame = ttkb.Labelframe(preview_content_frame, text="Source Image", padding=5)
        source_preview_frame.pack(side=LEFT, fill=BOTH, expand=True, padx=(0, 5))
        
        self.source_preview_label = ttkb.Label(source_preview_frame, text="No image", bootstyle='secondary')
        self.source_preview_label.pack(expand=True)
        
        # 右侧：目标图片信息
        target_preview_frame = ttkb.Labelframe(preview_content_frame, text="Target Info", padding=5)
        target_preview_frame.pack(side=RIGHT, fill=BOTH, expand=True, padx=(5, 0))
        
        self.target_info_label = ttkb.Label(target_preview_frame, text="AVIF output", bootstyle='secondary')
        self.target_info_label.pack(expand=True)
        
        # 压缩比例图示区域
        self.compression_frame = ttkb.Labelframe(workspace_frame, text="Compression Ratio", padding=5)
        self.compression_frame.pack(fill=X, pady=10)
        
        # 压缩比例信息
        self.compression_info_label = ttkb.Label(self.compression_frame, text="No conversion data available", bootstyle='secondary')
        self.compression_info_label.pack(pady=5)
        
        # 压缩比例可视化图表
        self.compression_canvas = tk.Canvas(self.compression_frame, height=100, bg='#2B2B2B')
        self.compression_canvas.pack(fill=X, padx=10, pady=5)
        
        # 日志区域
        log_frame = ttkb.Labelframe(workspace_frame, text="Conversion Log", padding=5)
        log_frame.pack(fill=BOTH, expand=True, pady=10)
        
        self.log_text = tk.Text(log_frame, height=10, state='disabled')
        log_scrollbar = ttkb.Scrollbar(log_frame, orient="vertical", command=self.log_text.yview)
        self.log_text.configure(yscrollcommand=log_scrollbar.set)
        
        self.log_text.pack(side="left", fill="both", expand=True)
        log_scrollbar.pack(side="right", fill="y")
        
        return workspace_frame

    def browse_source_folder(self):
        path = filedialog.askdirectory()
        if path:
            self.source_path_var.set(path)

    def browse_target_folder(self):
        path = filedialog.askdirectory()
        if path:
            self.target_path_var.set(path)

    def start_conversion(self):
        source_path = self.source_path_var.get()
        target_path = self.target_path_var.get()
        
        if not source_path or not os.path.isdir(source_path):
            messagebox.showerror("Invalid Path", "Please enter a valid source folder path.")
            return
            
        if not target_path:
            messagebox.showerror("Invalid Path", "Please enter a valid target folder path.")
            return

        params = {
            'source_path': source_path,
            'target_path': target_path,
            'quality': self.quality_var.get(),
            'subdirs': self.subdirs_var.get()
        }

        self.is_running = True
        self.start_btn.config(state=DISABLED)
        self.stop_btn.config(state=NORMAL)
        self.progress_bar.config(value=0)
        
        # 重置统计信息
        self.total_files = 0
        self.converted_files = 0
        self.failed_files = 0
        self.stats_label.config(text=f"Files: {self.total_files} | Converted: {self.converted_files} | Failed: {self.failed_files}")
        
        # 清除预览区域和压缩比例图示
        self._clear_preview()

        self.convert_thread = threading.Thread(target=self.execute, args=(params,))
        self.convert_thread.daemon = True
        self.convert_thread.start()
        
    def _clear_preview(self):
        """清除预览区域"""
        if self.source_preview_label:
            self.source_preview_label.config(image="", text="No image")
        if self.target_info_label:
            self.target_info_label.config(text="AVIF output")
        if self.compression_info_label:
            self.compression_info_label.config(text="No conversion data available")
        if self.compression_canvas:
            self.compression_canvas.delete("all")
            
    def _show_preview(self, file_path: str):
        """显示当前转换图片的预览"""
        try:
            # 清除之前的预览
            for widget in self.source_preview_label.winfo_children():
                widget.destroy()
                
            # 加载并显示图片
            img = Image.open(file_path)
            
            # 调整图片大小以适应预览区域
            max_size = (200, 200)
            img.thumbnail(max_size, Image.Resampling.LANCZOS)
            
            # 转换为PhotoImage
            photo = ImageTk.PhotoImage(img)
            
            # 更新源图片预览标签
            self.source_preview_label.config(image=photo, text="")
            self.source_preview_label.image = photo  # 保持引用防止被垃圾回收
            
            # 更新目标信息
            file_size = os.path.getsize(file_path)
            file_size_mb = file_size / (1024 * 1024)
            file_name = os.path.basename(file_path)
            file_ext = os.path.splitext(file_name)[1].upper()
            
            info_text = f"File: {file_name}\nSize: {file_size_mb:.2f} MB\nFormat: {file_ext}\n\nTarget: AVIF"
            self.target_info_label.config(text=info_text)
            
        except Exception as e:
            self.source_preview_label.config(image="", text="Cannot preview image")
            self.target_info_label.config(text=f"Error loading preview:\n{str(e)}")
            
    def _show_compression_ratio(self, source_path: str, target_path: str):
        """显示压缩比例图示"""
        try:
            # 获取源文件和目标文件大小
            source_size = os.path.getsize(source_path)
            target_size = os.path.getsize(target_path)
            
            # 计算压缩比例
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
                
                # 更新压缩比例信息标签
                info_text = f"Source: {source_size_str} → Target: {target_size_str}\n"
                info_text += f"Size reduction: {reduction_str} ({compression_ratio:.1f}% smaller)"
                self.compression_info_label.config(text=info_text)
                
                # 绘制压缩比例可视化图表
                self.compression_canvas.delete("all")
                
                # 获取画布尺寸
                canvas_width = self.compression_canvas.winfo_width()
                if canvas_width <= 1:
                    canvas_width = 400  # 默认宽度
                
                canvas_height = 80
                bar_height = 30
                bar_y = 20
                
                # 绘制源文件大小条（红色）
                self.compression_canvas.create_rectangle(
                    50, bar_y, 
                    50 + (canvas_width - 100), bar_y + bar_height,
                    fill="#FF6B6B", outline="", tags="source_bar"
                )
                
                # 绘制目标文件大小条（绿色）
                target_width = (target_size / source_size) * (canvas_width - 100)
                self.compression_canvas.create_rectangle(
                    50, bar_y, 
                    50 + target_width, bar_y + bar_height,
                    fill="#4ECDC4", outline="", tags="target_bar"
                )
                
                # 添加标签
                self.compression_canvas.create_text(
                    25, bar_y + bar_height/2, 
                    text="Source", fill="white", anchor="e"
                )
                self.compression_canvas.create_text(
                    25, bar_y + bar_height/2 + 20, 
                    text="Target", fill="white", anchor="e"
                )
                
                # 添加大小标签
                self.compression_canvas.create_text(
                    50 + (canvas_width - 100)/2, bar_y - 10,
                    text=source_size_str, fill="white", anchor="s"
                )
                self.compression_canvas.create_text(
                    50 + target_width/2, bar_y + bar_height + 10,
                    text=target_size_str, fill="white", anchor="n"
                )
                
            else:
                self.compression_info_label.config(text="Source file size is 0")
                self.compression_canvas.delete("all")
                
        except Exception as e:
            self.compression_info_label.config(text=f"Error calculating compression ratio: {str(e)}")
            self.compression_canvas.delete("all")

    def stop_execution(self):
        self.is_running = False

    def log_message(self, message: str, level: str = "info"):
        """在日志区域显示消息"""
        self.workspace_root.after(0, lambda: self._update_log(message, level))
        
    def _update_log(self, message: str, level: str):
        self.log_text.config(state='normal')
        self.log_text.insert(tk.END, f"[{level.upper()}] {message}\n")
        self.log_text.see(tk.END)
        self.log_text.config(state='disabled')

    def execute(self, params: Dict[str, Any]):
        try:
            source_path = params['source_path']
            target_path = params['target_path']
            quality = params['quality']
            scan_subdirs = params['subdirs']
            
            # 初始化统计信息
            self.total_files = 0
            self.converted_files = 0
            self.failed_files = 0
            
            # 收集要转换的文件
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
            
            # 更新进度标签和统计信息
            self.workspace_root.after(0, lambda: self.progress_label.config(text=f"Converting: 0/{self.total_files}"))
            self.workspace_root.after(0, lambda: self.stats_label.config(text=f"Files: {self.total_files} | Converted: {self.converted_files} | Failed: {self.failed_files}"))
            
            # 转换文件
            last_converted_source = None
            last_converted_target = None
            
            for i, (file_path, original_dir) in enumerate(image_files):
                if not self.is_running: 
                    self.log_message("Conversion stopped", "info")
                    break
                    
                try:
                    # 显示当前转换的图片预览
                    self.workspace_root.after(0, lambda fp=file_path: self._show_preview(fp))
                    
                    # 计算目标路径
                    relative_path = os.path.relpath(original_dir, source_path)
                    target_dir = os.path.join(target_path, relative_path) if relative_path != '.' else target_path
                    os.makedirs(target_dir, exist_ok=True)
                    
                    # 生成目标文件名
                    base_name = os.path.splitext(os.path.basename(file_path))[0]
                    target_file = os.path.join(target_dir, f"{base_name}.avif")
                    
                    # 保存原始目标文件路径用于重名处理
                    original_target_file = target_file
                    
                    # 检查是否已存在
                    if os.path.exists(target_file):
                        counter = 1
                        while os.path.exists(os.path.join(target_dir, f"{base_name}_{counter}.avif")):
                            counter += 1
                        target_file = os.path.join(target_dir, f"{base_name}_{counter}.avif")
                    
                    # 转换图片
                    with Image.open(file_path) as img:
                        # 处理RGBA模式的图片
                        if img.mode == 'RGBA':
                            # 创建白色背景
                            background = Image.new('RGB', img.size, (255, 255, 255))
                            background.paste(img, mask=img.split()[-1])
                            img = background
                        elif img.mode != 'RGB':
                            img = img.convert('RGB')
                            
                        img.save(target_file, 'AVIF', quality=quality)
                    
                    self.converted_files += 1
                    self.log_message(f"Converted: {os.path.basename(file_path)} -> {os.path.basename(target_file)}", "success")
                    
                    # 保存最后转换的文件路径用于压缩比例显示
                    last_converted_source = file_path
                    last_converted_target = target_file
                    
                    # 显示上一张图片的压缩比例（如果不是第一张）
                    if last_converted_source and last_converted_target and last_converted_source != file_path:
                        self.workspace_root.after(0, lambda s=last_converted_source, t=last_converted_target: self._show_compression_ratio(s, t))
                    
                    # 更新进度和统计信息
                    progress = (i + 1) / self.total_files * 100
                    self.workspace_root.after(0, lambda: self.progress_bar.config(value=progress))
                    self.workspace_root.after(0, lambda c=self.converted_files, t=self.total_files: self.progress_label.config(text=f"Converting: {c}/{t}"))
                    self.workspace_root.after(0, lambda c=self.converted_files, f=self.failed_files: self.stats_label.config(text=f"Files: {self.total_files} | Converted: {c} | Failed: {f}"))
                    
                except Exception as e:
                    self.failed_files += 1
                    self.log_message(f"Conversion failed {os.path.basename(file_path)}: {str(e)}", "error")
                    # 更新统计信息
                    self.workspace_root.after(0, lambda c=self.converted_files, f=self.failed_files: self.stats_label.config(text=f"Files: {self.total_files} | Converted: {c} | Failed: {f}"))
            
            # 显示最后一张图片的压缩比例
            if last_converted_source and last_converted_target:
                self.workspace_root.after(0, lambda s=last_converted_source, t=last_converted_target: self._show_compression_ratio(s, t))
            
            # 完成
            self.log_message(f"Conversion completed! Successfully converted {self.converted_files}/{self.total_files} files", "info")
            
        except Exception as e:
            self.log_message(f"Error during conversion: {str(e)}", "error")
        finally:
            self.is_running = False
            if self.settings_root:
                self.settings_root.after(0, lambda: self.start_btn.config(state=NORMAL))
                self.settings_root.after(0, lambda: self.stop_btn.config(state=DISABLED))