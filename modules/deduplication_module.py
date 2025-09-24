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

class DeduplicationModule(BaseFunctionModule):
    """图片去重功能模块 (V2)"""

    def __init__(self):
        super().__init__(
            name="deduplication",
            display_name="图片去重",
            description="查找并处理重复或相似的图片。",
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

        # 1. 扫描路径
        path_frame = ttkb.Labelframe(settings_frame, text="扫描路径", padding=10)
        path_frame.pack(fill=X, pady=5, expand=True)

        self.path_var = tk.StringVar(value="")
        path_entry = ttkb.Entry(path_frame, textvariable=self.path_var)
        path_entry.pack(side=LEFT, fill=X, expand=True, padx=(0, 5))

        browse_btn = ttkb.Button(path_frame, text="浏览", command=self.browse_folder, bootstyle='outline-secondary')
        browse_btn.pack(side=LEFT)

        # 2. 检测设置
        options_frame = ttkb.Labelframe(settings_frame, text="检测设置", padding=10)
        options_frame.pack(fill=X, pady=5, expand=True)

        sens_frame = ttkb.Frame(options_frame)
        sens_frame.pack(fill=X, pady=5)
        ttkb.Label(sens_frame, text="相似度阈值:").pack(side=LEFT, padx=(0, 10))
        self.sensitivity_var = tk.DoubleVar(value=95)
        sens_scale = ttkb.Scale(sens_frame, from_=70, to=100, variable=self.sensitivity_var, orient=HORIZONTAL)
        sens_scale.pack(side=LEFT, fill=X, expand=True)
        self.sens_label = ttkb.Label(sens_frame, text="95%", width=5)
        self.sens_label.pack(side=LEFT, padx=(10, 0))
        sens_scale.config(command=lambda val: self.sens_label.config(text=f"{float(val):.0f}%"))

        self.subdirs_var = tk.BooleanVar(value=True)
        subdirs_check = ttkb.Checkbutton(options_frame, text="包含子目录", variable=self.subdirs_var, bootstyle='round-toggle')
        subdirs_check.pack(fill=X, pady=5)

        # 3. 操作控制
        action_frame = ttkb.Labelframe(settings_frame, text="操作控制", padding=10)
        action_frame.pack(fill=X, pady=5, expand=True)

        self.start_btn = ttkb.Button(action_frame, text="▶️ 开始扫描", command=self.start_scan, bootstyle='success')
        self.start_btn.pack(side=LEFT, fill=X, expand=True, padx=(0, 5))

        self.stop_btn = ttkb.Button(action_frame, text="⏹️ 停止", command=self.stop_execution, bootstyle='danger-outline', state=DISABLED)
        self.stop_btn.pack(side=LEFT, fill=X, expand=True, padx=5)
        
        return settings_frame

    def create_workspace_ui(self, parent: ttkb.Frame) -> ttkb.Frame:
        """创建工作区UI面板（右栏）"""
        self.workspace_root = parent
        workspace_frame = ttkb.Frame(parent, padding=10)
        
        stats_frame = ttkb.Frame(workspace_frame)
        stats_frame.pack(fill=X, pady=5)
        self.stats_label = ttkb.Label(stats_frame, text="尚未开始扫描。", font=("", 10))
        self.stats_label.pack(anchor=W)

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

        self.initial_prompt = ttkb.Label(self.scrollable_frame, text="扫描结果将在这里显示...", font=("", 12, 'italic'))
        self.initial_prompt.pack(pady=50)

        return workspace_frame

    def browse_folder(self):
        path = filedialog.askdirectory()
        if path:
            self.path_var.set(path)

    def start_scan(self):
        scan_path = self.path_var.get()
        if not scan_path or not os.path.isdir(scan_path):
            messagebox.showerror("路径无效", "请输入一个有效的文件夹路径。")
            return

        params = {
            'path': scan_path,
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

            scan_path = params['path']
            threshold = 100 - params['sensitivity']
            scan_subdirs = params['subdirs']

            image_files = []
            valid_extensions = ('.png', '.jpg', '.jpeg', '.bmp', '.gif', '.webp')
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

            hashes = {}
            total_files = len(image_files)
            for i, f in enumerate(image_files):
                if not self.is_running: break
                try:
                    with Image.open(f) as img:
                        hashes[f] = imagehash.phash(img)
                except Exception as e:
                    pass
            
            if not self.is_running: return

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
            print(f"Error during execution: {e}")
        finally:
            self.is_running = False
            if self.settings_root:
                self.settings_root.after(0, lambda: self.start_btn.config(state=NORMAL))
                self.settings_root.after(0, lambda: self.stop_btn.config(state=DISABLED))

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
                except Exception as e:
                    print(f"Could not display image {f_path}: {e}")