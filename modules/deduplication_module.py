import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os
import threading
from typing import Dict, Any, List
from datetime import datetime
from collections import defaultdict

try:
    import ttkbootstrap as ttkb
    from ttkbootstrap.constants import *
    from PIL import Image, ImageTk
except ImportError:
    print("错误: 必要的库未安装。请运行 'pip install ttkbootstrap Pillow'")
    exit()

from function_modules import BaseFunctionModule

class ImprovedDeduplicationModule(BaseFunctionModule):
    """改进版图片去重功能模块"""

    def __init__(self):
        super().__init__(
            name="improved_deduplication",
            display_name="Improved Image Deduplication",
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
        
        # 移除模块中的字体设置，使用主应用的全局字体设置
        # self.default_font = ("Arial", 18)
        # self.large_font = ("Arial", 20, "bold")
        # self.small_font = ("Arial", 16)
        
        # 使用主应用的全局字体设置
        self.default_font = None
        self.large_font = None
        self.small_font = None
        
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
        self.stats_label = ttkb.Label(progress_frame, text="Scan not started yet.")
        self.stats_label.pack(anchor=W)
        
        self.progress_bar = ttkb.Progressbar(progress_frame, bootstyle='info-striped')
        self.progress_bar.pack(fill=X, pady=5)
        
        # 顶部操作工具栏
        toolbar_frame = ttkb.Frame(workspace_frame)
        toolbar_frame.pack(fill=X, pady=5)
        
        # 全选/取消全选按钮
        self.select_all_btn = ttkb.Button(toolbar_frame, text="Select All", command=self.select_all_images, bootstyle='primary')
        self.select_all_btn.pack(side=LEFT, padx=5)
        
        self.unselect_all_btn = ttkb.Button(toolbar_frame, text="Unselect All", command=self.unselect_all_images, bootstyle='secondary')
        self.unselect_all_btn.pack(side=LEFT, padx=5)
        
        # 已选择数量标签
        self.selection_count_label = ttkb.Label(toolbar_frame, text="Selected: 0")
        self.selection_count_label.pack(side=LEFT, padx=20)
        
        # 操作按钮
        delete_btn = ttkb.Button(toolbar_frame, text="Delete Selected", command=self.delete_selected_files_advanced, bootstyle='danger')
        delete_btn.pack(side=RIGHT, padx=5)
        
        move_btn = ttkb.Button(toolbar_frame, text="Move Selected", command=self.move_selected_files_advanced, bootstyle='warning')
        move_btn.pack(side=RIGHT, padx=5)
        
        # 日志区域（默认隐藏，带展开按钮）
        self.log_frame = ttkb.Frame(workspace_frame, style='Secondary.TFrame')
        # 默认不显示单行日志，用户可以通过展开按钮查看详细日志
        # log_frame.pack(fill=X, pady=5)  # 注释掉这行来隐藏单行日志

        self.log_label = ttkb.Label(self.log_frame, text="Scan not started yet.", font=self.small_font, foreground='white')
        self.log_label.pack(side=LEFT, anchor=W, fill=X, expand=True)

        # 添加展开/折叠按钮 - 放在工具栏
        self.log_expanded = False
        self.expand_btn = ttkb.Button(toolbar_frame, text="Show Log", command=lambda: self.toggle_log_expansion(None), bootstyle='info', width=8)
        self.expand_btn.pack(side=RIGHT, padx=5)
        
        # 详细日志文本框（初始隐藏）
        self.log_text = tk.Text(workspace_frame, height=8, state='disabled', font=self.small_font, bg='#1B1B1B', fg='white')
        self.log_scrollbar = ttkb.Scrollbar(workspace_frame, orient="vertical", command=self.log_text.yview)
        self.log_text.configure(yscrollcommand=self.log_scrollbar.set)
        self.log_text.pack_forget()  # 初始隐藏
        self.log_scrollbar.pack_forget()  # 初始隐藏
        
        # 结果区域
        result_label = ttkb.Label(workspace_frame, text="Scan Results", font=self.large_font, bootstyle='primary')
        result_label.pack(anchor=W, pady=(10, 5))
        
        result_container = ttkb.Frame(workspace_frame)
        result_container.pack(fill=BOTH, expand=True, pady=10)

        # 使用Canvas和Scrollbar创建自定义滚动框架
        canvas = tk.Canvas(result_container, highlightthickness=0)  # 移除高亮边框
        scrollbar = ttkb.Scrollbar(result_container, orient="vertical", command=canvas.yview)
        self.scrollable_frame = ttkb.Frame(canvas)

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(
                scrollregion=canvas.bbox("all")
            )
        )

        # 创建窗口对象，使用标签便于管理
        self.canvas_window = canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw", tags='canvas_window')
        canvas.configure(yscrollcommand=scrollbar.set)

        # 存储canvas引用
        self.selection_canvas = canvas

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        self.initial_prompt = ttkb.Label(self.scrollable_frame, text="Scan results will be displayed here...", style='info.TLabel')
        self.initial_prompt.pack(pady=50)

        # 设置回调函数
        self.set_callbacks(self.update_progress, self.add_log_message)
        
        # 绑定鼠标事件用于框选功能
        canvas.bind("<Button-1>", self.on_canvas_click)
        canvas.bind("<B1-Motion>", self.on_canvas_drag)
        canvas.bind("<ButtonRelease-1>", self.on_canvas_release)
        
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
                        hash_value = imagehash.phash(img)
                        hashes[f] = hash_value
                        # 添加调试信息
                        if self.log_callback and i < 5:  # 只显示前5个文件的哈希值
                            self.log_callback(f"文件 {f} 的哈希值: {hash_value} (类型: {type(hash_value)})", "debug")
                except Exception as e:
                    if self.log_callback:
                        self.log_callback(f"无法处理图片 {f}: {str(e)}", "warning")
            
            if not self.is_running: return

            # 查找重复项 - 优化算法
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
            self.workspace_root.after(0, lambda: self.display_results_async(duplicates))

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
            formatted_message = f"[{timestamp}] [{level.upper()}] {message}"
            self.workspace_root.after(0, lambda: self.update_log_label(formatted_message))
            
    def update_log_label(self, message: str):
        """更新日志标签 - 只更新详细日志，单行日志已隐藏"""
        # 单行日志已隐藏，不再更新
        # self.log_label.config(text=message)

        # 直接添加到详细日志
        self.log_text.config(state='normal')
        self.log_text.insert(tk.END, message + "\n")
        self.log_text.see(tk.END)
        self.log_text.config(state='disabled')
        
    def clear_log(self):
        """清除日志"""
        # 单行日志已隐藏，不再更新
        # self.log_label.config(text="Log cleared.")

        # 清除详细日志
        self.log_text.config(state='normal')
        self.log_text.delete(1.0, tk.END)
        self.log_text.config(state='disabled')
        
    def toggle_log_expansion(self, event=None):
        """切换日志区域的展开/折叠状态"""
        self.log_expanded = not self.log_expanded

        if self.log_expanded:
            self.expand_btn.config(text="Hide Log")
            # 显示详细日志文本框
            self.log_text.pack(fill=X, pady=5)
            self.log_scrollbar.pack(side="right", fill="y", pady=5, padx=(0, 10))
            # 将滚动条与文本框关联
            self.log_text.configure(yscrollcommand=self.log_scrollbar.set)
        else:
            self.expand_btn.config(text="Show Log")
            self.log_text.pack_forget()
            self.log_scrollbar.pack_forget()
        
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
        self.image_widgets_map = {}  # 用于存储widget和文件路径的映射
        self.duplicate_groups = dict(duplicates)  # 存储重复组数据
        self.card_frames_map = {}  # 用于存储卡片框架和文件组的映射
        
        # 创建主容器，使用网格布局实现自适应分栏
        main_container = ttkb.Frame(self.scrollable_frame)
        main_container.pack(fill=BOTH, expand=True, padx=5, pady=5)
        
        # 计算列数（根据窗口宽度自适应）
        # 获取主容器的宽度
        main_container.update_idletasks()  # 确保窗口大小已更新
        container_width = main_container.winfo_width()
        
        # 根据容器宽度计算列数
        # 假设每列最小宽度为250像素（更合理的值）
        min_column_width = 250
        if container_width > 0:
            columns = max(1, min(6, container_width // min_column_width))  # 最少1列，最多6列
        else:
            columns = 3  # 默认3列
        
        for group_idx, (master, dups) in enumerate(duplicates.items()):
            group_counter += 1
            
            # 创建紧凑的重复项卡片
            card_frame = ttkb.Frame(main_container, padding=8, style='Card.TFrame')
            row = group_idx // columns
            col = group_idx % columns
            card_frame.grid(row=row, column=col, padx=5, pady=5, sticky='nsew')
            
            # 设置网格权重，使卡片均匀分布
            # 为所有可能的行列设置权重，避免重新配置时闪烁
            for i in range(100):  # 假设最多100行
                main_container.grid_rowconfigure(i, weight=1)
            for j in range(6):  # 最多6列
                main_container.grid_columnconfigure(j, weight=1)
            
            # 存储卡片框架引用
            self.card_frames_map[card_frame] = dups
            
            # 卡片头部：选择状态和组信息
            header_frame = ttkb.Frame(card_frame)
            header_frame.pack(fill=X, pady=(0, 8))
            
            # 选择复选框
            self.selected_groups = set()
            group_var = tk.BooleanVar()
            group_check = ttk.Checkbutton(header_frame, variable=group_var, 
                                        command=lambda g=dups, v=group_var: self.toggle_group_selection(g, v))
            group_check.pack(side=LEFT, padx=(0, 8))
            
            # 组信息
            group_info = ttkb.Label(header_frame, text=f"重复组 {group_counter} ({len(dups)}张)", font=self.default_font)
            group_info.pack(side=LEFT)

            # 置信度标签（简化显示）
            confidence_label = ttkb.Label(header_frame, text="高置信度", foreground='#198754', font=self.small_font)
            confidence_label.pack(side=RIGHT)
            
            # 图片显示区域 - 水平排列，最多显示2张
            image_frame = ttkb.Frame(card_frame)
            image_frame.pack(fill=X, pady=5)
            
            # 显示前2张图片（或堆叠显示）
            for i in range(min(2, len(dups))):
                img_container = ttkb.Frame(image_frame, padding=2)
                img_container.pack(side=LEFT, padx=2)
                
                try:
                    f_path = dups[i]
                    img = Image.open(f_path)
                    # 更小的缩略图
                    img.thumbnail((80, 80))  # 缩小图片尺寸
                    photo = ImageTk.PhotoImage(img)

                    # 创建图片标签，添加选择功能
                    img_label = ttk.Label(img_container, image=photo)
                    img_label.image = photo
                    img_label.file_path = f_path
                    img_label.pack()
                    
                    # 绑定点击事件
                    img_label.bind("<Button-1>", lambda e, widget=img_label: self.on_image_click(e, widget))
                    img_label.bind("<Button-3>", lambda e, widget=img_label: self.on_image_click(e, widget))  # 右键点击
                    img_label.bind("<Double-Button-1>", lambda e, widget=img_label: self.on_image_click(e, widget))  # 双击左键
                    
                    # 存储widget引用用于后续操作
                    self.image_widgets_map[f_path] = img_label
                    
                    # 如果是第二张且还有更多图片，显示堆叠效果
                    if i == 1 and len(dups) > 2:
                        # 创建堆叠效果 - 显示剩余图片的小缩略图
                        stack_frame = ttkb.Frame(img_container)
                        stack_frame.pack(fill=BOTH, expand=True)
                        
                        # 计算需要显示的堆叠图片数量（最多显示3张额外的缩略图）
                        stack_count = min(3, len(dups) - 2)
                        
                        for j in range(stack_count):
                            stack_path = dups[2 + j]
                            try:
                                stack_img = Image.open(stack_path)
                                # 更小的堆叠缩略图
                                stack_img.thumbnail((20, 20))
                                stack_photo = ImageTk.PhotoImage(stack_img)
                                
                                # 创建堆叠图片标签
                                stack_label = ttk.Label(stack_frame, image=stack_photo, borderwidth=1, relief='solid')
                                stack_label.image = stack_photo  # 保持引用
                                stack_label.file_path = stack_path
                                stack_label.pack(anchor=SE, pady=1)
                                
                                # 绑定点击事件
                                stack_label.bind("<Button-1>", lambda e, widget=stack_label: self.on_image_click(e, widget))
                                stack_label.bind("<Button-3>", lambda e, widget=stack_label: self.on_image_click(e, widget))  # 右键点击
                                stack_label.bind("<Double-Button-1>", lambda e, widget=stack_label: self.on_image_click(e, widget))  # 双击左键
                                
                                # 存储widget引用
                                self.image_widgets_map[stack_path] = stack_label
                            except Exception as stack_e:
                                # 显示小的错误占位符
                                stack_error = ttk.Label(stack_frame, text="?", font=("Arial", max(8, int(8 * getattr(self, 'dpi_scaling', 1.0)))), foreground='red')
                                stack_error.pack(anchor=SE, pady=1)
                        
                        # 如果还有更多未显示的图片，显示数字指示
                        remaining = len(dups) - 2 - stack_count
                        if remaining > 0:
                            more_label = ttk.Label(stack_frame, text=f"+{remaining}", 
                                                 background='#FF8C00', foreground='white')
                            more_label.pack(anchor=SE, pady=1)
                        
                except Exception as e:
                    # 显示错误占位符
                    error_label = ttk.Label(img_container, text="无法显示", foreground='red')
                    error_label.pack()
            
            # 文件信息（文件名和大小）
            info_frame = ttkb.Frame(card_frame)
            info_frame.pack(fill=X)
            
            # 显示主要文件信息
            try:
                first_file = dups[0]
                filename = os.path.basename(first_file)
                file_size = os.path.getsize(first_file)
                
                name_label = ttkb.Label(info_frame, text=filename, font=self.small_font, wraplength=150)
                name_label.pack(anchor=W)

                size_label = ttkb.Label(info_frame, text=f"{file_size/1024/1024:.1f}MB", font=self.small_font, foreground='#CCCCCC')
                size_label.pack(anchor=W)
                
            except:
                pass
                
            # 绑定整个卡片的点击事件
            card_frame.bind("<Button-1>", lambda e, g=dups: self.on_card_click(e, g))
            header_frame.bind("<Button-1>", lambda e, g=dups: self.on_card_click(e, g))
            image_frame.bind("<Button-1>", lambda e, g=dups: self.on_card_click(e, g))
            info_frame.bind("<Button-1>", lambda e, g=dups: self.on_card_click(e, g))
            
        # 存储主容器引用用于框选
        self.main_container = main_container
        
        # 绑定窗口大小变化事件
        main_container.bind("<Configure>", self.on_container_configure)

    def on_image_click(self, event, widget):
        """处理单击图片事件 - 选择或取消选择"""
        file_path = widget.file_path

        # 检查是否按下了Ctrl键
        if event.state & 0x4:  # Ctrl键被按下
            if file_path in self.selected_files:
                self.selected_files.remove(file_path)
                self._update_widget_selection_state(widget, False)
            else:
                self.selected_files.add(file_path)
                self._update_widget_selection_state(widget, True)
        # 检查是否按下了Shift键
        elif event.state & 0x1:  # Shift键被按下
            self.on_image_shift_click(event, widget)
        # 检查是否是右键点击
        elif event.num == 3:  # 右键点击
            self.show_image_context_menu(event, widget)
        # 检查是否是双击
        elif event.num == 1 and event.type == "4":  # 双击左键
            self.show_image_preview(file_path)
        else:
            # 普通点击，只选择当前图片
            # 先取消选择所有图片
            self.unselect_all_images()
            # 再选择当前图片
            self.selected_files.add(file_path)
            self._update_widget_selection_state(widget, True)

        self.update_selection_count()
        self.last_clicked_widget = widget

    def on_image_ctrl_click(self, event, widget):
        """处理Ctrl+单击图片事件 - 多选"""
        file_path = widget.file_path
        
        if file_path in self.selected_files:
            self.selected_files.remove(file_path)
            self._update_widget_selection_state(widget, False)
        else:
            self.selected_files.add(file_path)
            self._update_widget_selection_state(widget, True)
            
        self.update_selection_count()
        self.last_clicked_widget = widget
        
    def show_image_context_menu(self, event, widget):
        """显示图片右键菜单"""
        file_path = widget.file_path
        
        # 创建右键菜单
        context_menu = tk.Menu(self.workspace_root, tearoff=0)
        context_menu.add_command(label="Show in Folder", command=lambda: self.open_file_in_explorer(file_path))
        context_menu.add_command(label="Image Info", command=lambda: self.show_image_info(file_path))
        
        # 在鼠标位置显示菜单
        try:
            context_menu.post(event.x_root, event.y_root)
        except Exception as e:
            pass  # 忽略错误
            
    def open_file_in_explorer(self, file_path):
        """在文件资源管理器中打开文件所在目录并选中文件"""
        try:
            import subprocess
            import platform
            
            # 调试信息
            if self.log_callback:
                self.log_callback(f"Attempting to open file in explorer: {file_path}", "info")
            
            # 检查文件是否存在
            if not os.path.exists(file_path):
                if self.log_callback:
                    self.log_callback(f"File does not exist: {file_path}", "error")
                return
                
            # 根据操作系统执行不同的命令
            system = platform.system()
            if system == "Windows":
                # Windows: 使用 explorer /select 命令
                if self.log_callback:
                    self.log_callback(f"Executing: explorer /select, {file_path}", "info")
                subprocess.run(["explorer", "/select,", file_path], check=True)
            elif system == "Darwin":  # macOS
                # macOS: 使用 open -R 命令
                if self.log_callback:
                    self.log_callback(f"Executing: open -R {file_path}", "info")
                subprocess.run(["open", "-R", file_path], check=True)
            else:  # Linux
                # Linux: 打开文件所在目录
                directory = os.path.dirname(file_path)
                if self.log_callback:
                    self.log_callback(f"Executing: xdg-open {directory}", "info")
                subprocess.run(["xdg-open", directory], check=True)
        except Exception as e:
            if self.log_callback:
                self.log_callback(f"Failed to open file in explorer: {str(e)}", "error")
                
    def show_image_info(self, file_path):
        """显示图片信息"""
        try:
            from PIL import Image
            img = Image.open(file_path)
            info = f"File: {os.path.basename(file_path)}\n"
            info += f"Path: {file_path}\n"
            info += f"Size: {img.size[0]}x{img.size[1]}\n"
            info += f"Format: {img.format}\n"
            info += f"File Size: {os.path.getsize(file_path) / 1024:.1f} KB"
            
            messagebox.showinfo("Image Info", info)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to get image info: {str(e)}")
            
    def show_image_preview(self, file_path):
        """显示图片全屏预览"""
        try:
            # 创建预览窗口
            preview_window = tk.Toplevel(self.workspace_root)
            preview_window.title(f"Image Preview - {os.path.basename(file_path)}")
            preview_window.geometry("800x600")
            preview_window.minsize(400, 300)
            
            # 设置窗口居中
            preview_window.update_idletasks()
            x = (preview_window.winfo_screenwidth() // 2) - (800 // 2)
            y = (preview_window.winfo_screenheight() // 2) - (600 // 2)
            preview_window.geometry(f"800x600+{x}+{y}")
            
            # 创建主框架
            main_frame = ttkb.Frame(preview_window)
            main_frame.pack(fill=BOTH, expand=True, padx=10, pady=10)
            
            # 图片信息栏
            info_frame = ttkb.Frame(main_frame)
            info_frame.pack(fill=X, pady=(0, 10))
            
            # 显示文件名和路径
            filename_label = ttkb.Label(info_frame, text=os.path.basename(file_path), font=self.large_font)
            filename_label.pack(anchor=W)

            path_label = ttkb.Label(info_frame, text=file_path, font=self.default_font, foreground="#CCCCCC")
            path_label.pack(anchor=W)
            
            # 图片显示区域
            image_frame = ttkb.Frame(main_frame)
            image_frame.pack(fill=BOTH, expand=True)
            
            # 创建画布和滚动条
            canvas = tk.Canvas(image_frame, bg="#1B1B1B")
            v_scrollbar = ttkb.Scrollbar(image_frame, orient=VERTICAL, command=canvas.yview)
            h_scrollbar = ttkb.Scrollbar(image_frame, orient=HORIZONTAL, command=canvas.xview)
            canvas.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
            
            # 打包滚动条和画布
            canvas.pack(side=LEFT, fill=BOTH, expand=True)
            v_scrollbar.pack(side=RIGHT, fill=Y)
            h_scrollbar.pack(side=BOTTOM, fill=X)
            
            # 加载并显示图片
            img = Image.open(file_path)
            
            # 获取图片原始尺寸
            original_width, original_height = img.size
            
            # 计算缩放比例以适应窗口
            canvas.update_idletasks()
            canvas_width = canvas.winfo_width()
            canvas_height = canvas.winfo_height()
            
            # 如果画布尺寸为0（初始状态），使用默认尺寸
            if canvas_width == 0:
                canvas_width = 780
            if canvas_height == 0:
                canvas_height = 500
            
            # 计算缩放比例
            scale_x = canvas_width / original_width
            scale_y = canvas_height / original_height
            scale = min(scale_x, scale_y, 1.0)  # 不放大图片
            
            # 计算缩放后的尺寸
            new_width = int(original_width * scale)
            new_height = int(original_height * scale)
            
            # 缩放图片
            img_resized = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
            photo = ImageTk.PhotoImage(img_resized)
            
            # 在画布中心显示图片
            canvas.create_image(canvas_width//2, canvas_height//2, image=photo, anchor=CENTER)
            
            # 保存图片引用以防止被垃圾回收
            canvas.image = photo
            
            # 配置滚动区域
            canvas.config(scrollregion=canvas.bbox(ALL))
            
            # 添加缩放功能
            def on_mousewheel(event):
                """处理鼠标滚轮缩放"""
                if event.delta > 0:
                    # 放大
                    scale_factor = 1.1
                else:
                    # 缩小
                    scale_factor = 0.9
                
                # 获取鼠标位置
                mouse_x = canvas.canvasx(event.x)
                mouse_y = canvas.canvasy(event.y)
                
                # 缩放图片
                nonlocal new_width, new_height, img_resized, photo
                new_width = int(new_width * scale_factor)
                new_height = int(new_height * scale_factor)
                
                # 限制最小尺寸
                new_width = max(new_width, 100)
                new_height = max(new_height, 100)
                
                # 重新缩放图片
                img_resized = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
                photo = ImageTk.PhotoImage(img_resized)
                canvas.delete("all")
                canvas.create_image(mouse_x, mouse_y, image=photo, anchor=CENTER)
                canvas.image = photo
                canvas.config(scrollregion=canvas.bbox(ALL))
            
            # 绑定鼠标滚轮事件
            canvas.bind("<MouseWheel>", on_mousewheel)
            
            # 添加键盘快捷键
            def on_key_press(event):
                """处理键盘事件"""
                if event.keysym == "Escape":
                    preview_window.destroy()
                elif event.keysym == "plus" or event.keysym == "equal":
                    # 放大 (+)
                    on_mousewheel(type('Event', (), {'delta': 120, 'x': canvas.winfo_width()//2, 'y': canvas.winfo_height()//2})())
                elif event.keysym == "minus":
                    # 缩小 (-)
                    on_mousewheel(type('Event', (), {'delta': -120, 'x': canvas.winfo_width()//2, 'y': canvas.winfo_height()//2})())
            
            preview_window.bind("<Key>", on_key_press)
            preview_window.focus_set()  # 确保窗口能接收键盘事件
            
            # 添加工具栏
            toolbar_frame = ttkb.Frame(main_frame)
            toolbar_frame.pack(fill=X, pady=(10, 0))
            
            # 添加操作按钮
            open_btn = ttkb.Button(toolbar_frame, text="Show in Folder", command=lambda: self.open_file_in_explorer(file_path))
            open_btn.pack(side=LEFT, padx=(0, 5))
            
            info_btn = ttkb.Button(toolbar_frame, text="Image Info", command=lambda: self.show_image_info(file_path))
            info_btn.pack(side=LEFT, padx=5)
            
            close_btn = ttkb.Button(toolbar_frame, text="Close", command=preview_window.destroy)
            close_btn.pack(side=RIGHT, padx=(5, 0))
            
        except Exception as e:
            if self.log_callback:
                self.log_callback(f"无法显示图片预览: {str(e)}", "error")
            messagebox.showerror("错误", f"无法显示图片预览: {str(e)}")

    def on_image_shift_click(self, event, widget):
        """处理Shift+单击图片事件 - 范围选择"""
        file_path = widget.file_path
        
        if not self.last_clicked_widget:
            self.on_image_click(event, widget)
            return
            
        # 找到当前组中的所有图片
        current_group = None
        for master, dups in self.duplicate_groups.items():
            if file_path in dups and self.last_clicked_widget.file_path in dups:
                current_group = dups
                break
        
        if not current_group:
            return
            
        # 找到开始位置和结束位置
        try:
            start_idx = current_group.index(self.last_clicked_widget.file_path)
            end_idx = current_group.index(file_path)
            
            # 确保start_idx <= end_idx
            if start_idx > end_idx:
                start_idx, end_idx = end_idx, start_idx
                
            # 选择范围内的所有图片
            for i in range(start_idx, end_idx + 1):
                range_path = current_group[i]
                self.selected_files.add(range_path)
                # 高亮对应的widget
                if range_path in self.image_widgets_map:
                    self._update_widget_selection_state(self.image_widgets_map[range_path], True)
                    
        except ValueError:
            # 如果找不到索引，执行正常的单击操作
            self.on_image_click(event, widget)
            return
            
        self.update_selection_count()
        self.last_clicked_widget = widget

    def find_widget_for_path(self, path):
        """查找对应文件路径的widget"""
        # 遍历所有组和图片来找到对应的widget
        for group_widget in self.scrollable_frame.winfo_children():
            if not hasattr(group_widget, 'winfo_children'):
                continue
            for img_grid_frame in group_widget.winfo_children():
                if not hasattr(img_grid_frame, 'winfo_children'):
                    continue
                for img_frame in img_grid_frame.winfo_children():
                    for widget in img_frame.winfo_children():
                        if isinstance(widget, ttk.Label) and widget.winfo_ismapped():
                            # 这里我们难以直接关联，所以简化实现
                            pass
        return None

    def get_image_widgets_in_group(self, group_files):
        """获取组中所有图片的widgets"""
        widgets = []
        # 这个方法需要在实际实现中追踪widgets
        return widgets

    def select_group(self, group_files):
        """选择整个组的图片"""
        for file_path in group_files:
            self.selected_files.add(file_path)
        self.update_selection_count()

    def unselect_group(self, group_files):
        """取消选择整个组的图片"""
        for file_path in group_files:
            self.selected_files.discard(file_path)
        self.update_selection_count()

    def select_all_images(self):
        """选择所有图片"""
        for group_files in self.duplicate_groups.values():
            for file_path in group_files:
                self.selected_files.add(file_path)
        self.update_selection_count()
        # 更新所有图片的显示状态
        self.update_all_image_widgets()

    def unselect_all_images(self):
        """取消选择所有图片"""
        self.selected_files.clear()
        self.update_selection_count()
        # 更新所有图片的显示状态
        self.update_all_image_widgets()

    def update_selection_count(self):
        """更新选择计数标签"""
        count = len(self.selected_files)
        self.selection_count_label.config(text=f"Selected: {count}")

    def delete_selected_files_advanced(self):
        """高级删除功能 - 保留未选中的，删除选中的，但确保至少保留一张图片"""
        if not self.selected_files:
            messagebox.showinfo("提示", "请先选择要删除的图片。")
            return
            
        # 检查是否有组将要删除所有图片
        groups_with_all_selected = []
        for group_master, group_files in self.duplicate_groups.items():
            selected_in_group = [f for f in group_files if f in self.selected_files]
            if len(selected_in_group) == len(group_files):
                groups_with_all_selected.append((group_master, group_files))
        
        if groups_with_all_selected:
            # 每个组至少保留一张图片
            for master, group_files in groups_with_all_selected:
                # 询问用户是否要保留一张图片
                result = messagebox.askyesnocancel(
                    "警告", 
                    f"组 '{os.path.basename(master)}' 中的所有图片都被选中。\n" +
                    f"是否保留其中一张（随机选择）并删除其他图片？\n" +
                    f"点击'是'保留一张，'否'删除全部，'取消'中止操作。"
                )
                
                if result is True:  # 保留一张
                    # 从这个组的选中文件中移除一张
                    for file_path in group_files:
                        if file_path in self.selected_files:
                            self.selected_files.remove(file_path)
                            # 移除高亮
                            if file_path in self.image_widgets_map:
                                self.image_widgets_map[file_path].configure(relief='flat', borderwidth=1)
                            break
                elif result is False:  # 删除全部
                    continue
                else:  # 取消操作
                    return
        
        # 统计要删除的文件数
        files_to_delete = list(self.selected_files)
        total_files = len(files_to_delete)
        
        if not files_to_delete:
            messagebox.showinfo("提示", "没有要删除的文件。")
            return

        result = messagebox.askyesno("Confirm Delete", f"确定要删除选中的 {total_files} 个文件吗？此操作无法撤销！")
        if not result:
            return

        deleted_count = 0
        for file_path in files_to_delete:
            try:
                os.remove(file_path)
                deleted_count += 1
                self.add_log_message(f"已删除文件: {file_path}", "info")
            except Exception as e:
                self.add_log_message(f"删除文件失败 {file_path}: {str(e)}", "error")
                
        self.add_log_message(f"删除完成，成功删除 {deleted_count}/{total_files} 个文件", "info")
        messagebox.showinfo("删除完成", f"成功删除 {deleted_count} 个文件")
        
        # 清空选择并更新界面
        self.selected_files.clear()
        self.update_selection_count()
        
    def toggle_log_expansion(self, event):
        """切换日志区域的展开/折叠状态"""
        self.log_expanded = not self.log_expanded
        
        if self.log_expanded:
            self.log_frame.configure(text="📋 日志 (点击折叠)")
            self.log_text.pack(side="left", fill="both", expand=True)
            self.log_scrollbar.pack(side="right", fill="y")
        else:
            self.log_frame.configure(text="📋 日志 (点击展开)")
            self.log_text.pack_forget()
            self.log_scrollbar.pack_forget()
            
    def toggle_group_selection(self, group_files, checkbox_var):
        """切换整个组的选中状态"""
        if checkbox_var.get():
            # 选择整个组
            for file_path in group_files:
                self.selected_files.add(file_path)
                # 高亮对应的widget
                if file_path in self.image_widgets_map:
                    self._update_widget_selection_state(self.image_widgets_map[file_path], True)
        else:
            # 取消选择整个组
            for file_path in group_files:
                self.selected_files.discard(file_path)
                # 移除高亮
                if file_path in self.image_widgets_map:
                    self._update_widget_selection_state(self.image_widgets_map[file_path], False)
        
        self.update_selection_count()
        
    def update_all_image_widgets(self):
        """更新所有图片widget的显示状态"""
        for file_path, widget in self.image_widgets_map.items():
            is_selected = file_path in self.selected_files
            self._update_widget_selection_state(widget, is_selected)

    def _update_widget_selection_state(self, widget, is_selected):
        """更新单个widget的选中状态显示"""
        try:
            if is_selected:
                # 选中状态：明显的视觉反馈
                widget.configure(
                    relief='solid',
                    borderwidth=4,
                    background='#FF8C00',  # 橙色背景
                    foreground='white'     # 白色前景
                )

                # 如果支持，添加选中效果
                try:
                    # 创建选中效果的外发光
                    widget.configure(highlightbackground='#FF8C00', highlightcolor='#FFD700', highlightthickness=2)
                except:
                    pass

                # 如果是图片标签，保持图片显示但添加选中覆盖效果
                try:
                    if hasattr(widget, 'image') and widget.image:
                        # 添加半透明覆盖效果（如果可能）
                        pass
                except:
                    pass

            else:
                # 未选中状态：恢复默认外观
                widget.configure(
                    relief='flat',
                    borderwidth=1,
                    background='SystemButtonFace',  # 默认背景
                    foreground='SystemButtonText'  # 默认前景
                )

                # 移除高亮效果
                try:
                    widget.configure(highlightbackground='SystemButtonFace', highlightcolor='SystemButtonFace', highlightthickness=0)
                except:
                    pass

        except Exception as e:
            print(f"更新widget选中状态时出错: {e}")
            # 降级到简单的方式
            try:
                if is_selected:
                    widget.configure(relief='solid', borderwidth=3)
                else:
                    widget.configure(relief='flat', borderwidth=1)
            except:
                pass
        
    def on_card_click(self, event, group_files):
        """处理卡片点击事件"""
        # 检查是否按下了Ctrl键
        if event.state & 0x4:  # Ctrl键被按下
            # 切换整个组的选中状态
            is_selected = all(file_path in self.selected_files for file_path in group_files)
            
            if is_selected:
                # 取消选择
                for file_path in group_files:
                    self.selected_files.discard(file_path)
                    if file_path in self.image_widgets_map:
                        self._update_widget_selection_state(self.image_widgets_map[file_path], False)
            else:
                # 选择
                for file_path in group_files:
                    self.selected_files.add(file_path)
                    if file_path in self.image_widgets_map:
                        self._update_widget_selection_state(self.image_widgets_map[file_path], True)
        # 检查是否按下了Shift键
        elif event.state & 0x1:  # Shift键被按下
            # 对于卡片的Shift选择，我们暂时不实现复杂逻辑
            # 直接切换整个组的选中状态
            is_selected = all(file_path in self.selected_files for file_path in group_files)
            
            if is_selected:
                # 取消选择
                for file_path in group_files:
                    self.selected_files.discard(file_path)
                    if file_path in self.image_widgets_map:
                        self._update_widget_selection_state(self.image_widgets_map[file_path], False)
            else:
                # 选择
                for file_path in group_files:
                    self.selected_files.add(file_path)
                    if file_path in self.image_widgets_map:
                        self._update_widget_selection_state(self.image_widgets_map[file_path], True)
        else:
            # 普通点击，只选择当前组
            # 先取消选择所有图片
            self.unselect_all_images()
            # 再选择当前组
            for file_path in group_files:
                self.selected_files.add(file_path)
                if file_path in self.image_widgets_map:
                    self._update_widget_selection_state(self.image_widgets_map[file_path], True)
        
        self.update_selection_count()

    def move_selected_files_advanced(self):
        """高级移动功能 - 移动选中的图片"""
        if not self.selected_files:
            messagebox.showinfo("提示", "请先选择要移动的图片。")
            return
            
        target_dir = filedialog.askdirectory(title="选择目标文件夹")
        if not target_dir:
            return
            
        total_files = len(self.selected_files)
        moved_count = 0
        
        for file_path in self.selected_files:
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
                self.add_log_message(f"已移动文件: {file_path} -> {target_path}", "info")
            except Exception as e:
                self.add_log_message(f"移动文件失败 {file_path}: {str(e)}", "error")
                
        self.add_log_message(f"移动完成，成功移动 {moved_count}/{total_files} 个文件", "info")
        messagebox.showinfo("移动完成", f"成功移动 {moved_count} 个文件")
        
        # 清空选择并更新界面
        self.selected_files.clear()
        self.update_selection_count()
        
    def on_canvas_click(self, event):
        """处理画布点击事件 - 开始框选"""
        # 获取画布坐标
        canvas = event.widget
        self.start_x = canvas.canvasx(event.x)
        self.start_y = canvas.canvasy(event.y)

        # 创建选择矩形，使用特殊标签确保在最顶层
        self.is_selecting = True

        # 删除旧的矩形（如果存在）
        if hasattr(self, 'selection_rect') and self.selection_rect:
            try:
                canvas.delete(self.selection_rect)
            except:
                pass

        # 创建新的选择矩形
        self.selection_rect = canvas.create_rectangle(
            self.start_x, self.start_y, self.start_x, self.start_y,
            outline='#FF8C00', fill='#FF8C00', stipple='gray25', width=2,
            tags='selection_rect'  # 使用标签便于管理
        )

        # 确保矩形在canvas_window之上
        canvas.tag_raise('selection_rect')
        canvas.tag_raise('selection_rect', 'canvas_window')
        
    def on_canvas_drag(self, event):
        """处理画布拖动事件 - 更新框选区域"""
        if not self.is_selecting:
            return

        # 获取画布坐标
        canvas = event.widget
        cur_x = canvas.canvasx(event.x)
        cur_y = canvas.canvasy(event.y)

        # 更新选择矩形
        canvas.coords(self.selection_rect, self.start_x, self.start_y, cur_x, cur_y)

        # 确保矩形始终在canvas_window之上
        canvas.tag_raise('selection_rect')
        canvas.tag_raise('selection_rect', 'canvas_window')
        
    def on_canvas_release(self, event):
        """处理画布释放事件 - 完成框选"""
        if not self.is_selecting:
            return
            
        # 获取画布坐标
        canvas = event.widget
        end_x = canvas.canvasx(event.x)
        end_y = canvas.canvasy(event.y)
        
        # 删除选择矩形
        canvas.delete(self.selection_rect)
        self.is_selecting = False
        
        # 计算框选区域
        min_x = min(self.start_x, end_x)
        max_x = max(self.start_x, end_x)
        min_y = min(self.start_y, end_y)
        max_y = max(self.start_y, end_y)
        
        # 检查哪些卡片在框选区域内
        selected_groups = []
        for card_frame, group_files in self.card_frames_map.items():
            # 获取卡片在画布中的位置
            card_x = card_frame.winfo_x()
            card_y = card_frame.winfo_y()
            card_width = card_frame.winfo_width()
            card_height = card_frame.winfo_height()
            
            # 检查卡片是否与框选区域相交
            if (card_x < max_x and card_x + card_width > min_x and
                card_y < max_y and card_y + card_height > min_y):
                selected_groups.append(group_files)
        
        # 如果有卡片被选中，更新选择状态
        if selected_groups:
            # 按住Ctrl键时添加到现有选择，否则替换现有选择
            if not (event.state & 0x4):  # Ctrl未按下
                self.unselect_all_images()
            
            # 选择所有被框选的组
            for group_files in selected_groups:
                for file_path in group_files:
                    self.selected_files.add(file_path)
            
            # 更新显示
            self.update_all_image_widgets()
            self.update_selection_count()
            
    def on_container_configure(self, event):
        """处理容器大小变化事件"""
        # 防止在初始化时触发
        if not hasattr(self, 'duplicate_groups') or not self.duplicate_groups:
            return
            
        # 延迟执行重新排列，避免频繁触发
        if hasattr(self, '_resize_timer'):
            self.main_container.after_cancel(self._resize_timer)
            
        self._resize_timer = self.main_container.after(300, self._rearrange_cards)
        
    def _rearrange_cards(self):
        """重新排列卡片"""
        # 重新显示结果以应用新的列数
        if hasattr(self, 'duplicate_groups') and self.duplicate_groups:
            # 保存当前选中状态
            selected_before = set(self.selected_files)

            # 重新计算列数并重新布局
            if hasattr(self, 'main_container') and self.main_container.winfo_exists():
                # 清除现有的网格配置
                for i in range(self.main_container.grid_size()[1]):
                    self.main_container.grid_rowconfigure(i, weight=0)
                for j in range(self.main_container.grid_size()[0]):
                    self.main_container.grid_columnconfigure(j, weight=0)

                # 重新显示结果以应用新的列数
                self.display_results(self.duplicate_groups)

                # 恢复选中状态
                self.selected_files = selected_before
                self.update_all_image_widgets()

  
    def display_results_async(self, duplicates: Dict):
        """
        异步显示结果，避免UI线程阻塞
        分批处理UI组件创建，提供实时进度反馈
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
        
        # 如果需要异步处理大量数据，可以取消注释下面的代码
        # # 分批异步创建UI组件
        # self._create_ui_components_batch(main_container, duplicates)

    def _clear_results_fast(self):
        """快速清空现有UI组件"""
        try:
            for widget in self.scrollable_frame.winfo_children():
                widget.destroy()
        except Exception:
            pass  # 忽略清理错误

    def _show_no_results_message(self):
        """显示无结果消息"""
        self.stats_label.config(text="未找到重复图片。")
        message_label = ttkb.Label(
            self.scrollable_frame,
            text="恭喜！未在指定目录中找到重复图片。",
            font=("", 12, 'italic')
        )
        message_label.pack(pady=50)

    def _init_display_data(self, duplicates: Dict):
        """初始化显示数据"""
        num_groups = len(duplicates)
        num_files = sum(len(v) for v in duplicates.values())
        self.stats_label.config(text=f"找到 {num_groups} 组重复图片，共 {num_files} 个文件。")

        # 重置数据结构
        self.image_widgets_map = {}
        self.card_frames_map = {}
        self.selected_groups = set()

    def _create_main_container(self):
        """创建主容器"""
        main_container = ttkb.Frame(self.scrollable_frame)
        main_container.pack(fill=BOTH, expand=True, padx=5, pady=5)

        # 确保容器能够响应大小变化
        main_container.bind('<Configure>', lambda e: self.on_container_configure(e))

        # 设置最小宽度以确保有足够空间显示多列
        main_container.update_idletasks()
        min_width = max(400, self.scrollable_frame.winfo_width() - 20)
        main_container.configure(width=min_width)

        return main_container

    def _create_ui_components_batch(self, main_container, duplicates: Dict):
        """
        分批创建UI组件，避免界面冻结
        """
        import threading
        import time

        def create_components():
            """在后台线程中创建组件"""
            try:
                # 计算列数
                columns = self._calculate_columns(main_container)
                self._setup_grid_weights(main_container)

                # 分批处理，每批10个组
                batch_size = 10
                group_items = list(duplicates.items())

                for batch_start in range(0, len(group_items), batch_size):
                    if not self.is_running:
                        break

                    batch_end = min(batch_start + batch_size, len(group_items))
                    current_batch = group_items[batch_start:batch_end]

                    # 在主线程中创建这批UI组件
                    self.workspace_root.after(0, lambda batch=current_batch, cols=columns: self._create_ui_batch(main_container, batch, cols))

                    # 批次间短暂休息，让UI有机会响应
                    time.sleep(0.01)

                    # 更新进度
                    progress = (batch_end / len(group_items)) * 100
                    if self.log_callback:
                        self.workspace_root.after(0, lambda p=progress: self.log_callback(f"创建界面: {p:.0f}%", "info"))

                # 完成后最终更新
                if self.is_running:
                    self.workspace_root.after(0, lambda: self.log_callback("界面创建完成", "success"))

            except Exception as e:
                if self.log_callback:
                    self.workspace_root.after(0, lambda: self.log_callback(f"创建界面时出错: {str(e)}", "error"))

        # 在后台线程中执行
        threading.Thread(target=create_components, daemon=True).start()
        
    def _create_ui_components_sync(self, main_container, duplicates: Dict):
        """
        同步创建UI组件，确保能正确显示结果
        """
        try:
            # 计算列数
            columns = self._calculate_columns(main_container)
            self._setup_grid_weights(main_container)

            # 直接创建所有UI组件
            group_items = list(duplicates.items())
            
            # 分批处理，每批20个组
            batch_size = 20
            for batch_start in range(0, len(group_items), batch_size):
                if not self.is_running:
                    break

                batch_end = min(batch_start + batch_size, len(group_items))
                current_batch = group_items[batch_start:batch_end]

                # 创建这批UI组件
                self._create_ui_batch(main_container, current_batch, columns)

                # 更新进度
                progress = (batch_end / len(group_items)) * 100
                if self.log_callback:
                    self.log_callback(f"创建界面: {progress:.0f}%", "info")

            # 完成后最终更新
            if self.log_callback:
                self.log_callback("界面创建完成", "success")

        except Exception as e:
            if self.log_callback:
                self.log_callback(f"创建界面时出错: {str(e)}", "error")

    def _calculate_columns(self, main_container):
        """计算合适的列数"""
        try:
            main_container.update_idletasks()
            container_width = main_container.winfo_width()

            # 更合理的卡片最小宽度，包含边距
            min_card_width = 220  # 卡片实际最小宽度
            margin_padding = 20    # 边距和内边距总宽度
            effective_min_width = min_card_width + margin_padding

            if container_width > 0:
                # 计算最大可能的列数
                max_columns = max(1, min(8, container_width // effective_min_width))

                # 根据容器宽度智能调整列数
                if container_width < 400:
                    return 1
                elif container_width < 600:
                    return 2
                elif container_width < 900:
                    return 3
                elif container_width < 1200:
                    return 4
                elif container_width < 1500:
                    return 5
                else:
                    return max_columns
            else:
                # 默认值，基于常见屏幕尺寸
                return 3
        except Exception as e:
            print(f"计算列数时出错: {e}")
            return 3

    def _setup_grid_weights(self, main_container):
        """设置网格权重"""
        try:
            # 清除旧的行列配置
            for i in range(main_container.grid_size()[1]):
                main_container.grid_rowconfigure(i, weight=0)
            for j in range(main_container.grid_size()[0]):
                main_container.grid_columnconfigure(j, weight=0)

            # 设置新的行列权重
            for i in range(100):  # 最多100行
                main_container.grid_rowconfigure(i, weight=1)
            for j in range(8):  # 最多8列
                main_container.grid_columnconfigure(j, weight=1)
        except Exception as e:
            print(f"设置网格权重时出错: {e}")

    def _create_ui_batch(self, main_container, batch_items, columns):
        """创建一批UI组件"""
        try:
            for group_idx, (master, dups) in enumerate(batch_items):
                if not self.is_running:
                    break  # 改为break，继续处理其他组

                # 计算网格位置
                batch_start_idx = batch_items.index((master, dups))
                actual_group_idx = group_idx  # 在批次中的相对位置

                # 创建卡片
                card_frame = self._create_single_card(main_container, dups, actual_group_idx, columns)

            # 强制更新UI
            main_container.update_idletasks()

        except Exception as e:
            if self.log_callback:
                self.log_callback(f"创建UI批次时出错: {str(e)}", "warning")

    def _create_single_card(self, main_container, dups, group_idx, columns):
        """创建单个卡片"""
        try:
            # 计算网格位置
            row = group_idx // columns
            col = group_idx % columns

            # 创建卡片框架
            card_frame = ttkb.Frame(main_container, padding=8, style='Card.TFrame')

            # 设置卡片的网格布局，确保能够自适应
            card_frame.grid(row=row, column=col, padx=5, pady=5, sticky='nsew')

            # 配置列的权重，确保卡片能够均匀分布
            for j in range(columns):
                main_container.grid_columnconfigure(j, weight=1, uniform='card_cols')

            # 配置行的权重，确保卡片能够垂直拉伸
            main_container.grid_rowconfigure(row, weight=1)

            # 存储引用
            self.card_frames_map[card_frame] = dups

            # 创建卡片内容
            self._create_card_header(card_frame, dups, group_idx + 1)
            self._create_card_images(card_frame, dups)

            return card_frame

        except Exception as e:
            print(f"创建单个卡片时出错: {e}")
            # 返回一个简单的框架以防出错
            error_frame = ttkb.Frame(main_container)
            error_frame.pack(fill=BOTH, expand=True)
            return error_frame

    def _create_card_header(self, card_frame, dups, group_number):
        """创建卡片头部"""
        header_frame = ttkb.Frame(card_frame)
        header_frame.pack(fill=X, pady=(0, 8))

        # 选择复选框
        group_var = tk.BooleanVar()
        group_check = ttkb.Checkbutton(
            header_frame,
            variable=group_var,
            command=lambda g=dups, v=group_var: self.toggle_group_selection(g, v)
        )
        group_check.pack(side=LEFT, padx=(0, 8))

        # 组信息
        group_info = ttkb.Label(
            header_frame,
            text=f"重复组 {group_number} ({len(dups)}张)"
        )
        group_info.pack(side=LEFT)

        # 置信度标签
        confidence_label = ttkb.Label(
            header_frame,
            text="高置信度",
            foreground='#198754'
        )
        confidence_label.pack(side=RIGHT)

    def _create_card_images(self, card_frame, dups):
        """创建卡片图片区域"""
        image_frame = ttkb.Frame(card_frame)
        image_frame.pack(fill=X, pady=5)

        # 显示前2张图片
        for i in range(min(2, len(dups))):
            self._create_single_image(image_frame, dups[i], i == 1 and len(dups) > 2, dups)

    def _create_single_image(self, parent_frame, file_path, show_stack, dups):
        """创建单个图片显示，保持原始比例"""
        # 创建固定大小的容器，确保布局一致
        img_container = ttkb.Frame(parent_frame, padding=2, width=90, height=90)
        img_container.pack(side=LEFT, padx=2)
        img_container.pack_propagate(False)  # 防止容器被内容撑大

        try:
            # 使用保持比例的图片加载
            img = self._get_cached_image_with_aspect_ratio(file_path, max_size=80)
            if img:
                photo = ImageTk.PhotoImage(img)

                # 创建图片标签
                img_label = ttk.Label(img_container, image=photo)
                img_label.image = photo  # 保持引用防止垃圾回收
                img_label.file_path = file_path

                # 居中显示图片
                img_label.place(relx=0.5, rely=0.5, anchor='center')

                # 绑定事件
                self._bind_image_events(img_label)

                # 存储引用
                self.image_widgets_map[file_path] = img_label

                # 如果需要显示堆叠效果
                if show_stack:
                    self._create_stack_images(img_container, dups)

        except Exception as e:
            # 错误占位符
            error_label = ttk.Label(img_container, text="无法显示", foreground='red', font=self.small_font)
            error_label.place(relx=0.5, rely=0.5, anchor='center')

    def _create_stack_images(self, img_container, dups):
        """创建堆叠图片效果"""
        stack_frame = ttkb.Frame(img_container)
        stack_frame.pack(fill=BOTH, expand=True)

        # 显示最多3张额外的缩略图
        stack_count = min(3, len(dups) - 2)

        for j in range(stack_count):
            stack_path = dups[2 + j]
            try:
                stack_img = self._get_cached_image(stack_path, (20, 20))
                if stack_img:
                    stack_photo = ImageTk.PhotoImage(stack_img)
                    stack_label = ttk.Label(
                        stack_frame,
                        image=stack_photo,
                        borderwidth=1,
                        relief='solid'
                    )
                    stack_label.image = stack_photo
                    stack_label.file_path = stack_path
                    stack_label.pack(anchor=SE, pady=1)

                    self._bind_image_events(stack_label)
                    self.image_widgets_map[stack_path] = stack_label

            except Exception:
                stack_error = ttk.Label(stack_frame, text="?", font=("", 6), foreground='red')
                stack_error.pack(anchor=SE, pady=1)

        # 显示剩余数量
        remaining = len(dups) - 2 - stack_count
        if remaining > 0:
            more_label = ttk.Label(
                stack_frame,
                text=f"+{remaining}",
                background='#FF8C00',
                foreground='white',
                font=("", 6, 'bold')
            )
            more_label.pack(anchor=SE, pady=1)

    def _bind_image_events(self, img_label):
        """绑定图片事件"""
        img_label.bind("<Button-1>", lambda e, widget=img_label: self.on_image_click(e, widget))
        img_label.bind("<Button-3>", lambda e, widget=img_label: self.on_image_click(e, widget))
        img_label.bind("<Double-Button-1>", lambda e, widget=img_label: self.on_image_click(e, widget))

    def _get_cached_image(self, file_path, size=(80, 80)):
        """
        获取缓存的图片，减少重复加载和内存占用
        """
        return self._image_cache.get_image(file_path, size)

    def _get_cached_image_with_aspect_ratio(self, file_path, max_size=80):
        """
        获取保持原始比例的缓存图片
        """
        return self._image_cache.get_image_with_aspect_ratio(file_path, max_size)

    class _ImageCache:
        """
        图片缓存管理器
        使用弱引用和大小限制来管理内存使用
        """
        def __init__(self, max_size=100):
            self.max_size = max_size
            self._cache = {}  # 缓存字典
            self._access_order = []  # 访问顺序，用于LRU淘汰

        def get_image(self, file_path, size=(80, 80)):
            """
            获取图片，优先从缓存读取
            """
            cache_key = f"{file_path}_{size[0]}x{size[1]}"

            # 检查缓存
            if cache_key in self._cache:
                # 更新访问顺序
                self._access_order.remove(cache_key)
                self._access_order.append(cache_key)
                return self._cache[cache_key]

            # 缓存未命中，加载图片
            try:
                with Image.open(file_path) as img:
                    # 创建缩略图
                    thumbnail = img.resize(size, Image.Resampling.LANCZOS)

                    # 检查缓存大小，必要时清理
                    self._cleanup_cache()

                    # 添加到缓存
                    self._cache[cache_key] = thumbnail
                    self._access_order.append(cache_key)

                    return thumbnail

            except Exception as e:
                # 记录错误但不影响主流程
                print(f"无法加载图片 {file_path}: {e}")
                return None

        def get_image_with_aspect_ratio(self, file_path, max_size=80):
            """
            获取保持原始比例的图片
            """
            cache_key = f"{file_path}_aspect_{max_size}"

            # 检查缓存
            if cache_key in self._cache:
                # 更新访问顺序
                self._access_order.remove(cache_key)
                self._access_order.append(cache_key)
                return self._cache[cache_key]

            # 缓存未命中，加载图片
            try:
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

                    # 创建保持比例的缩略图
                    thumbnail = img.resize((new_width, new_height), Image.Resampling.LANCZOS)

                    # 检查缓存大小，必要时清理
                    self._cleanup_cache()

                    # 添加到缓存
                    self._cache[cache_key] = thumbnail
                    self._access_order.append(cache_key)

                    return thumbnail

            except Exception as e:
                # 记录错误但不影响主流程
                print(f"无法加载图片 {file_path}: {e}")
                return None

        def _cleanup_cache(self):
            """
            清理缓存，保持大小限制
            使用LRU（最近最少使用）策略
            """
            while len(self._cache) >= self.max_size:
                if self._access_order:
                    # 移除最久未使用的项目
                    oldest_key = self._access_order.pop(0)
                    if oldest_key in self._cache:
                        del self._cache[oldest_key]

        def clear(self):
            """清空缓存"""
            self._cache.clear()
            self._access_order.clear()

        def size(self):
            """获取当前缓存大小"""
            return len(self._cache)

    def _find_duplicates_optimized(self, hashes, threshold):
        """
        优化后的重复图片查找算法

        为了保证正确性，采用保守的优化策略：
        1. 小数据集（<1000文件）：使用原始O(n²)算法，确保正确性
        2. 大数据集（≥1000文件）：使用分组优化，但有完善的边界检查

        Args:
            hashes: 图片路径到哈希值的映射
            threshold: 相似度阈值

        Returns:
            重复组字典
        """
        from collections import defaultdict

        if not hashes:
            return {}

        files_to_check = list(hashes.keys())

        if self.log_callback:
            self.log_callback(f"开始查找重复项，文件数量: {len(files_to_check)}, 阈值: {threshold}", "info")

        # 对于个人桌面程序，文件数量通常不会太大
        # 使用保守阈值，确保正确性优先
        if len(files_to_check) < 1000:
            # 文件数量较少时，使用原始精确算法确保正确性
            if self.log_callback:
                self.log_callback(f"文件数量 {len(files_to_check)} 较少，使用精确算法", "info")
            result = self._find_duplicates_naive(hashes, threshold)
            if self.log_callback:
                self.log_callback(f"精确算法找到 {len(result)} 组重复项", "info")
            return result

        # 对于大数据集，使用安全的分组优化
        duplicates = defaultdict(list)
        comparison_count = 0

        # 按哈希值排序，这样相似的文件会相邻
        sorted_files = sorted(hashes.items(), key=lambda x: x[1])

        if self.log_callback:
            self.log_callback(f"排序完成，开始安全分组比较", "info")

        # 使用更安全的策略：确保不遗漏任何可能的相似对
        processed_files = set()

        i = 0
        while i < len(sorted_files):
            if not self.is_running:
                break

            f1, h1 = sorted_files[i]

            # 如果文件已被处理，跳过
            if f1 in processed_files:
                i += 1
                continue

            processed_files.add(f1)

            # 向后检查所有可能的相似文件
            j = i + 1
            while j < len(sorted_files):
                if not self.is_running:
                    break

                f2, h2 = sorted_files[j]

                # 如果文件已被处理，跳过
                if f2 in processed_files:
                    j += 1
                    continue

                comparison_count += 1

                # 使用绝对值比较，确保对称性
                if abs(h1 - h2) <= threshold:
                    if not duplicates[f1]:
                        duplicates[f1].append(f1)
                    duplicates[f1].append(f2)
                    processed_files.add(f2)
                elif h2 - h1 > threshold:
                    # 由于已排序，后面的文件哈希值会更大，可以提前终止
                    break

                j += 1

            i += 1

        # 输出性能统计
        original_comparisons = len(files_to_check) * (len(files_to_check) - 1) // 2
        if original_comparisons > 0:
            improvement = (1 - comparison_count / original_comparisons) * 100
        else:
            improvement = 0

        if self.log_callback:
            self.log_callback(
                f"算法优化完成: 原始比较 {original_comparisons:,} 次, "
                f"实际比较 {comparison_count:,} 次, "
                f"减少 {improvement:.1f}%, "
                f"找到 {len(duplicates)} 组重复项",
                "info"
            )

        return duplicates

    def _find_duplicates_naive(self, hashes, threshold):
        """
        原始的O(n²)算法，用于小规模数据集
        """
        duplicates = defaultdict(list)
        files_to_check = list(hashes.keys())

        if self.log_callback:
            self.log_callback(f"开始执行原始算法，文件数量: {len(files_to_check)}, 阈值: {threshold}", "info")

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

        if self.log_callback:
            self.log_callback(f"原始算法完成，找到 {len(duplicates)} 组重复项", "info")

        return duplicates

    def _find_duplicates_progressive(self, hashes, threshold):
        """
        逐组查找重复图片，支持实时显示
        找到一组重复图片就立即在UI中显示
        """
        from collections import defaultdict

        if not hashes:
            return {}

        files_to_check = list(hashes.keys())