import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os
import threading
from typing import Dict, Any

try:
    import ttkbootstrap as ttkb
    from ttkbootstrap.constants import *
    from PIL import Image
except ImportError:
    print("错误: 必要的库未安装。请运行 'pip install ttkbootstrap Pillow'")
    exit()

from function_modules import BaseFunctionModule

class AVIFConverterModule(BaseFunctionModule):
    """AVIF格式转换功能模块"""

    def __init__(self):
        super().__init__(
            name="avif_converter",
            display_name="AVIF转换",
            description="将图片转换为AVIF格式以节省存储空间。",
            icon="🔄"
        )
        self.convert_thread = None
        self.is_running = False
        self.workspace_root = None
        self.settings_root = None

    def create_settings_ui(self, parent: ttkb.Frame) -> ttkb.Frame:
        """创建设置UI面板（中栏）"""
        self.settings_root = parent
        settings_frame = ttkb.Frame(parent, padding=10)

        # 1. 源路径和目标路径
        source_frame = ttkb.Labelframe(settings_frame, text="源路径", padding=10)
        source_frame.pack(fill=X, pady=5, expand=True)

        self.source_path_var = tk.StringVar(value="")
        source_entry = ttkb.Entry(source_frame, textvariable=self.source_path_var)
        source_entry.pack(side=LEFT, fill=X, expand=True, padx=(0, 5))

        source_browse_btn = ttkb.Button(source_frame, text="浏览", command=self.browse_source_folder, bootstyle='secondary')
        source_browse_btn.pack(side=LEFT)

        target_frame = ttkb.Labelframe(settings_frame, text="目标路径", padding=10)
        target_frame.pack(fill=X, pady=5, expand=True)

        self.target_path_var = tk.StringVar(value="")
        target_entry = ttkb.Entry(target_frame, textvariable=self.target_path_var)
        target_entry.pack(side=LEFT, fill=X, expand=True, padx=(0, 5))

        target_browse_btn = ttkb.Button(target_frame, text="浏览", command=self.browse_target_folder, bootstyle='secondary')
        target_browse_btn.pack(side=LEFT)

        # 2. 转换设置
        options_frame = ttkb.Labelframe(settings_frame, text="转换设置", padding=10)
        options_frame.pack(fill=X, pady=5, expand=True)

        quality_frame = ttkb.Frame(options_frame)
        quality_frame.pack(fill=X, pady=5)
        ttkb.Label(quality_frame, text="质量:").pack(side=LEFT, padx=(0, 10))
        self.quality_var = tk.IntVar(value=85)
        quality_scale = ttkb.Scale(quality_frame, from_=1, to=100, variable=self.quality_var, orient=HORIZONTAL)
        quality_scale.pack(side=LEFT, fill=X, expand=True)
        self.quality_label = ttkb.Label(quality_frame, text="85%", width=5)
        self.quality_label.pack(side=LEFT, padx=(10, 0))
        quality_scale.config(command=lambda val: self.quality_label.config(text=f"{int(float(val))}%"))

        self.subdirs_var = tk.BooleanVar(value=True)
        subdirs_check = ttkb.Checkbutton(options_frame, text="包含子目录", variable=self.subdirs_var, bootstyle='round-toggle')
        subdirs_check.pack(fill=X, pady=5)

        # 3. 操作控制
        action_frame = ttkb.Labelframe(settings_frame, text="操作控制", padding=10)
        action_frame.pack(fill=X, pady=5, expand=True)

        self.start_btn = ttkb.Button(action_frame, text="▶️ 开始转换", command=self.start_conversion, bootstyle='success')
        self.start_btn.pack(side=LEFT, fill=X, expand=True, padx=(0, 5))

        self.stop_btn = ttkb.Button(action_frame, text="⏹️ 停止", command=self.stop_execution, bootstyle='danger', state=DISABLED)
        self.stop_btn.pack(side=LEFT, fill=X, expand=True, padx=5)
        
        return settings_frame

    def create_workspace_ui(self, parent: ttkb.Frame) -> ttkb.Frame:
        """创建工作区UI面板（右栏）"""
        self.workspace_root = parent
        workspace_frame = ttkb.Frame(parent, padding=10)
        
        # 进度和日志区域
        progress_frame = ttkb.Frame(workspace_frame)
        progress_frame.pack(fill=X, pady=5)
        self.progress_label = ttkb.Label(progress_frame, text="尚未开始转换。", font=("", 10))
        self.progress_label.pack(anchor=W)
        
        self.progress_bar = ttkb.Progressbar(progress_frame, bootstyle='success-striped')
        self.progress_bar.pack(fill=X, pady=5)
        
        # 日志区域
        log_frame = ttkb.Labelframe(workspace_frame, text="转换日志", padding=5)
        log_frame.pack(fill=BOTH, expand=True, pady=10)
        
        self.log_text = tk.Text(log_frame, height=15, state='disabled')
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
            messagebox.showerror("路径无效", "请输入一个有效的源文件夹路径。")
            return
            
        if not target_path:
            messagebox.showerror("路径无效", "请输入一个有效的目标文件夹路径。")
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

        self.convert_thread = threading.Thread(target=self.execute, args=(params,))
        self.convert_thread.daemon = True
        self.convert_thread.start()

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
            
            # 收集要转换的文件
            image_files = []
            valid_extensions = ('.png', '.jpg', '.jpeg', '.bmp', '.gif', '.webp')
            
            if scan_subdirs:
                for root, _, files in os.walk(source_path):
                    if not self.is_running: 
                        self.log_message("转换已停止", "info")
                        return
                    for file in files:
                        if file.lower().endswith(valid_extensions):
                            image_files.append((os.path.join(root, file), root))
            else:
                for file in os.listdir(source_path):
                    if not self.is_running: 
                        self.log_message("转换已停止", "info")
                        return
                    if file.lower().endswith(valid_extensions):
                        image_files.append((os.path.join(source_path, file), source_path))
            
            if not image_files:
                self.log_message("未找到可转换的图片文件", "warning")
                return
                
            total_files = len(image_files)
            self.log_message(f"找到 {total_files} 个文件待转换", "info")
            
            # 更新进度标签
            self.workspace_root.after(0, lambda: self.progress_label.config(text=f"正在转换: 0/{total_files}"))
            
            # 转换文件
            converted_count = 0
            for i, (file_path, original_dir) in enumerate(image_files):
                if not self.is_running: 
                    self.log_message("转换已停止", "info")
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
                        # 处理RGBA模式的图片
                        if img.mode == 'RGBA':
                            # 创建白色背景
                            background = Image.new('RGB', img.size, (255, 255, 255))
                            background.paste(img, mask=img.split()[-1])
                            img = background
                        elif img.mode != 'RGB':
                            img = img.convert('RGB')
                            
                        img.save(target_file, 'AVIF', quality=quality)
                    
                    converted_count += 1
                    self.log_message(f"已转换: {os.path.basename(file_path)} -> {os.path.basename(target_file)}", "success")
                    
                    # 更新进度
                    progress = (i + 1) / total_files * 100
                    self.workspace_root.after(0, lambda: self.progress_bar.config(value=progress))
                    self.workspace_root.after(0, lambda c=converted_count, t=total_files: self.progress_label.config(text=f"正在转换: {c}/{t}"))
                    
                except Exception as e:
                    self.log_message(f"转换失败 {os.path.basename(file_path)}: {str(e)}", "error")
            
            # 完成
            self.log_message(f"转换完成! 成功转换 {converted_count}/{total_files} 个文件", "info")
            
        except Exception as e:
            self.log_message(f"转换过程中出错: {str(e)}", "error")
        finally:
            self.is_running = False
            if self.settings_root:
                self.settings_root.after(0, lambda: self.start_btn.config(state=NORMAL))
                self.settings_root.after(0, lambda: self.stop_btn.config(state=DISABLED))