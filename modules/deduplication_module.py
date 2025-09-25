import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os
import threading
from typing import Dict, Any
from datetime import datetime

try:
    import ttkbootstrap as ttkb
    from ttkbootstrap.constants import *
    from PIL import Image, ImageTk
except ImportError:
    print("错误: 必要的库未安装。请运行 'pip install ttkbootstrap Pillow'")
    exit()

from function_modules import BaseFunctionModule

class DeduplicationModule(BaseFunctionModule):
    """图片去重功能模块 (V2)"""

    def __init__(self):
        super().__init__(
            name="deduplication",
            display_name="Image Deduplication",
            description="Find and process duplicate or similar images.",
            icon="🔍"
        )
        self.scan_thread = None
        self.is_running = False
        # UI组件的引用
        self.workspace_root = None
        self.settings_root = None

    def create_settings_ui(self, parent: ttkb.Frame) -> ttkb.Frame:
        """创建设置UI面板（中栏）"""
        self.settings_root = parent
        settings_frame = ttkb.Frame(parent, padding=10)

        # 1. 扫描路径（支持多个路径）
        paths_frame = ttkb.Labelframe(settings_frame, text="Scan Paths", padding=10)
        paths_frame.pack(fill=BOTH, pady=5, expand=True)

        # 路径列表显示区域
        self.paths_listbox = tk.Listbox(paths_frame, height=4, relief='flat', highlightthickness=0)
        self.paths_listbox.pack(fill=X, pady=(0, 5))
        
        # 路径操作按钮（使用圆角样式）
        path_btn_frame = ttkb.Frame(paths_frame)
        path_btn_frame.pack(fill=X)
        
        add_path_btn = ttkb.Button(path_btn_frame, text="Add Path", command=self.add_folder, bootstyle='success', width=10)
        add_path_btn.pack(side=LEFT, padx=(0, 5))
        
        remove_path_btn = ttkb.Button(path_btn_frame, text="Remove Path", command=self.remove_folder, bootstyle='danger', width=10)
        remove_path_btn.pack(side=LEFT, padx=5)
        
        clear_paths_btn = ttkb.Button(path_btn_frame, text="Clear Paths", command=self.clear_folders, bootstyle='warning', width=10)
        clear_paths_btn.pack(side=LEFT, padx=5)

        # 2. 检测设置
        options_frame = ttkb.Labelframe(settings_frame, text="Detection Settings", padding=10)
        options_frame.pack(fill=X, pady=5, expand=True)

        sens_frame = ttkb.Frame(options_frame)
        sens_frame.pack(fill=X, pady=5)
        ttkb.Label(sens_frame, text="Similarity Threshold:").pack(side=LEFT, padx=(0, 10))
        self.sensitivity_var = tk.DoubleVar(value=95)
        sens_scale = ttkb.Scale(sens_frame, from_=70, to=100, variable=self.sensitivity_var, orient=HORIZONTAL)
        sens_scale.pack(side=LEFT, fill=X, expand=True)
        self.sens_label = ttkb.Label(sens_frame, text="95%", width=5)
        self.sens_label.pack(side=LEFT, padx=(10, 0))
        sens_scale.config(command=lambda val: self.sens_label.config(text=f"{float(val):.0f}%"))

        self.subdirs_var = tk.BooleanVar(value=True)
        subdirs_check = ttkb.Checkbutton(options_frame, text="Include Subdirectories", variable=self.subdirs_var, bootstyle='round-toggle')
        subdirs_check.pack(fill=X, pady=5)

        # 3. 操作控制
        action_frame = ttkb.Labelframe(settings_frame, text="Operation Control", padding=10)
        action_frame.pack(fill=X, pady=5, expand=True)

        self.start_btn = ttkb.Button(action_frame, text="▶️ Start Scan", command=self.start_scan, bootstyle='success')
        self.start_btn.pack(side=LEFT, fill=X, expand=True, padx=(0, 5))

        self.stop_btn = ttkb.Button(action_frame, text="⏹️ Stop", command=self.stop_execution, bootstyle='danger', state=DISABLED)
        self.stop_btn.pack(side=LEFT, fill=X, expand=True, padx=5)
        
        return settings_frame

    def create_workspace_ui(self, parent: ttkb.Frame) -> ttkb.Frame:
        """创建工作区UI面板（右栏）"""
        self.workspace_root = parent
        workspace_frame = ttkb.Frame(parent, padding=10)
        
        # 进度区域
        progress_frame = ttkb.Frame(workspace_frame)
        progress_frame.pack(fill=X, pady=5)
        self.stats_label = ttkb.Label(progress_frame, text="Scan not started yet.", font=("", 10))
        self.stats_label.pack(anchor=W)
        
        self.progress_bar = ttkb.Progressbar(progress_frame, bootstyle='info-striped')
        self.progress_bar.pack(fill=X, pady=5)
        
        # 日志区域
        log_frame = ttkb.Labelframe(workspace_frame, text="Scan Log", padding=5)
        log_frame.pack(fill=BOTH, expand=True, pady=10)
        
        self.log_text = tk.Text(log_frame, height=8, state='disabled')
        log_scrollbar = ttkb.Scrollbar(log_frame, orient="vertical", command=self.log_text.yview)
        self.log_text.configure(yscrollcommand=log_scrollbar.set)
        
        self.log_text.pack(side="left", fill="both", expand=True)
        log_scrollbar.pack(side="right", fill="y")
        
        # 结果区域
        result_label = ttkb.Label(workspace_frame, text="Scan Results", font=("", 12, "bold"), bootstyle='primary')
        result_label.pack(anchor=W, pady=(10, 5))
        
        result_container = ttkb.Frame(workspace_frame)
        result_container.pack(fill=BOTH, expand=True, pady=10)

        # 使用Canvas和Scrollbar创建自定义滚动框架
        canvas = tk.Canvas(result_container)
        scrollbar = ttkb.Scrollbar(result_container, orient="vertical", command=canvas.yview)
        self.scrollable_frame = ttkb.Frame(canvas)

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(
                scrollregion=canvas.bbox("all")
            )
        )

        canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        self.initial_prompt = ttkb.Label(self.scrollable_frame, text="Scan results will be displayed here...", font=("", 12, 'italic'))
        self.initial_prompt.pack(pady=50)

        # 设置回调函数
        self.set_callbacks(self.update_progress, self.add_log_message)
        
        return workspace_frame

    def browse_folder(self):
        path = filedialog.askdirectory()
        if path:
            self.path_var.set(path)
            
    def add_folder(self):
        path = filedialog.askdirectory()
        if path and path not in self.paths_listbox.get(0, tk.END):
            self.paths_listbox.insert(tk.END, path)
            
    def remove_folder(self):
        selection = self.paths_listbox.curselection()
        if selection:
            self.paths_listbox.delete(selection[0])
            
    def clear_folders(self):
        self.paths_listbox.delete(0, tk.END)

    def start_scan(self):
        # 获取所有扫描路径
        paths = list(self.paths_listbox.get(0, tk.END))
        
        if not paths:
            messagebox.showerror("路径无效", "请至少添加一个有效的文件夹路径。")
            return
            
        # 验证所有路径都有效
        for path in paths:
            if not os.path.isdir(path):
                messagebox.showerror("路径无效", f"路径不存在或无效: {path}")
                return

        params = {
            'paths': paths,
            'sensitivity': self.sensitivity_var.get(),
            'subdirs': self.subdirs_var.get()
        }

        self.is_running = True
        self.start_btn.config(state=DISABLED)
        self.stop_btn.config(state=NORMAL)

        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()

        self.scan_thread = threading.Thread(target=self.execute, args=(params,))
        self.scan_thread.daemon = True
        self.scan_thread.start()

    def stop_execution(self):
        self.is_running = False

    def execute(self, params: Dict[str, Any]):
        try:
            import imagehash
            from collections import defaultdict

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
                        hashes[f] = imagehash.phash(img)
                except Exception as e:
                    if self.log_callback:
                        self.log_callback(f"无法处理图片 {f}: {str(e)}", "warning")
            
            if not self.is_running: return

            # 查找重复项
            if self.log_callback:
                self.log_callback("正在查找重复图片...", "info")
                
            duplicates = defaultdict(list)
            files_to_check = list(hashes.keys())
            
            for i in range(len(files_to_check)):
                if not self.is_running: break
                f1 = files_to_check[i]
                if f1 not in hashes: continue

                for j in range(i + 1, len(files_to_check)):
                    if not self.is_running: break
                    f2 = files_to_check[j]
                    if f2 not in hashes: continue

                    if hashes[f1] - hashes[f2] <= threshold:
                        if not duplicates[f1]:
                            duplicates[f1].append(f1)
                        duplicates[f1].append(f2)
                        if f2 in hashes: del hashes[f2]
            
            if not self.is_running: return

            self.workspace_root.after(0, lambda: self.display_results(duplicates))

        except Exception as e:
            if self.log_callback:
                self.log_callback(f"执行过程中出错: {str(e)}", "error")
            print(f"Error during execution: {e}")
        finally:
            self.is_running = False
            if self.settings_root:
                self.settings_root.after(0, lambda: self.start_btn.config(state=NORMAL))
                self.settings_root.after(0, lambda: self.stop_btn.config(state=DISABLED))
                
            # 完成消息
            if self.log_callback:
                self.log_callback("扫描完成", "info")

    def update_progress(self, value: float, message: str = ""):
        """更新进度条和状态信息"""
        if self.workspace_root:
            self.workspace_root.after(0, lambda: self.progress_bar.config(value=value))
            if message:
                self.workspace_root.after(0, lambda: self.stats_label.config(text=message))
                
    def add_log_message(self, message: str, level: str = "info"):
        """添加日志消息"""
        if self.workspace_root:
            timestamp = datetime.now().strftime("%H:%M:%S")
            formatted_message = f"[{timestamp}] [{level.upper()}] {message}\n"
            self.workspace_root.after(0, lambda: self._append_log(formatted_message))
            
    def _append_log(self, message: str):
        """在日志区域追加消息"""
        self.log_text.config(state='normal')
        self.log_text.insert(tk.END, message)
        self.log_text.see(tk.END)
        self.log_text.config(state='disabled')
        
    def display_results(self, duplicates: Dict):
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()

        if not duplicates:
            self.stats_label.config(text="未找到重复图片。")
            ttkb.Label(self.scrollable_frame, text="恭喜！未在指定目录中找到重复图片。", font=("", 12, 'italic')).pack(pady=50)
            return

        num_groups = len(duplicates)
        num_files = sum(len(v) for v in duplicates.values())
        self.stats_label.config(text=f"找到 {num_groups} 组重复图片，共 {num_files} 个文件。")

        group_counter = 0
        for master, dups in duplicates.items():
            group_counter += 1
            group_frame = ttkb.Labelframe(self.scrollable_frame, text=f"重复组 {group_counter} ({len(dups)} 张图片)", padding=10, bootstyle='info')
            group_frame.pack(fill=X, expand=True, padx=10, pady=10)
            
            # 添加操作按钮
            action_frame = ttkb.Frame(group_frame)
            action_frame.pack(fill=X, pady=(0, 10))
            
            ttkb.Label(action_frame, text="选择操作:", width=10).pack(side=LEFT)
            
            # 为每组创建一个变量来跟踪选择
            selected_files = []
            
            delete_btn = ttkb.Button(action_frame, text="删除选中", bootstyle='danger', 
                                   command=lambda dups=dups: self.delete_selected_files(dups))
            delete_btn.pack(side=LEFT, padx=5)
            
            move_btn = ttkb.Button(action_frame, text="移动选中", bootstyle='warning',
                                 command=lambda dups=dups: self.move_selected_files(dups))
            move_btn.pack(side=LEFT, padx=5)

            canvas = tk.Canvas(group_frame)
            scrollbar = ttk.Scrollbar(group_frame, orient="horizontal", command=canvas.xview)
            scrollable_inner_frame = ttk.Frame(canvas)

            scrollable_inner_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
            canvas.create_window((0, 0), window=scrollable_inner_frame, anchor="nw")
            canvas.configure(xscrollcommand=scrollbar.set)

            canvas.pack(side="top", fill="x", expand=True)
            scrollbar.pack(side="bottom", fill="x")

            for f_path in dups:
                try:
                    img_frame = ttk.Frame(scrollable_inner_frame, padding=5)
                    img_frame.pack(side=LEFT, padx=5, pady=5)

                    img = Image.open(f_path)
                    img.thumbnail((150, 150))
                    photo = ImageTk.PhotoImage(img)

                    img_label = ttk.Label(img_frame, image=photo)
                    img_label.image = photo
                    img_label.pack()

                    filename_label = ttk.Label(img_frame, text=os.path.basename(f_path), wraplength=150)
                    filename_label.pack()
                    
                    # 文件大小信息
                    try:
                        file_size = os.path.getsize(f_path)
                        size_label = ttk.Label(img_frame, text=f"{file_size/1024/1024:.2f} MB", font=("", 8))
                        size_label.pack()
                    except:
                        pass
                        
                except Exception as e:
                    print(f"Could not display image {f_path}: {e}")
                    
    def delete_selected_files(self, file_paths):
        """删除选中的文件"""
        if not file_paths:
            return
            
        result = messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete these {len(file_paths)} files? This action cannot be undone!")
        if result:
            deleted_count = 0
            for file_path in file_paths:
                try:
                    os.remove(file_path)
                    deleted_count += 1
                    self.add_log_message(f"Deleted file: {file_path}", "info")
                except Exception as e:
                    self.add_log_message(f"Failed to delete file {file_path}: {str(e)}", "error")
                    
            self.add_log_message(f"Deletion completed, successfully deleted {deleted_count}/{len(file_paths)} files", "info")
            messagebox.showinfo("Deletion Completed", f"Successfully deleted {deleted_count} files")
            
    def move_selected_files(self, file_paths):
        """移动选中的文件"""
        if not file_paths:
            return
            
        target_dir = filedialog.askdirectory(title="Select Target Folder")
        if not target_dir:
            return
            
        moved_count = 0
        for file_path in file_paths:
            try:
                filename = os.path.basename(file_path)
                target_path = os.path.join(target_dir, filename)
                
                # 处理重名文件
                counter = 1
                base_name, ext = os.path.splitext(filename)
                while os.path.exists(target_path):
                    new_name = f"{base_name}_{counter}{ext}"
                    target_path = os.path.join(target_dir, new_name)
                    counter += 1
                    
                os.rename(file_path, target_path)
                moved_count += 1
                self.add_log_message(f"Moved file: {file_path} -> {target_path}", "info")
            except Exception as e:
                self.add_log_message(f"Failed to move file {file_path}: {str(e)}", "error")
                
        self.add_log_message(f"Move completed, successfully moved {moved_count}/{len(file_paths)} files", "info")
        messagebox.showinfo("Move Completed", f"Successfully moved {moved_count} files")