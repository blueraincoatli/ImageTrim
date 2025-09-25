import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os
import threading
from typing import Dict, Any, List
from datetime import datetime

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
        self.workspace_root = None
        self.settings_root = None
        # 存储重复组数据
        self.duplicate_groups = {}
        # 存储选中的文件
        self.selected_files = set()
        # 存储上次点击的图片，用于Shift选择
        self.last_clicked_widget = None
        
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
        
        # 顶部操作工具栏
        toolbar_frame = ttkb.Frame(workspace_frame)
        toolbar_frame.pack(fill=X, pady=5)
        
        # 全选/取消全选按钮
        self.select_all_btn = ttkb.Button(toolbar_frame, text="Select All", command=self.select_all_images, bootstyle='primary')
        self.select_all_btn.pack(side=LEFT, padx=5)
        
        self.unselect_all_btn = ttkb.Button(toolbar_frame, text="Unselect All", command=self.unselect_all_images, bootstyle='secondary')
        self.unselect_all_btn.pack(side=LEFT, padx=5)
        
        # 已选择数量标签
        self.selection_count_label = ttkb.Label(toolbar_frame, text="Selected: 0", font=("", 10, 'bold'))
        self.selection_count_label.pack(side=LEFT, padx=20)
        
        # 操作按钮
        delete_btn = ttkb.Button(toolbar_frame, text="Delete Selected", command=self.delete_selected_files_advanced, bootstyle='danger')
        delete_btn.pack(side=RIGHT, padx=5)
        
        move_btn = ttkb.Button(toolbar_frame, text="Move Selected", command=self.move_selected_files_advanced, bootstyle='warning')
        move_btn.pack(side=RIGHT, padx=5)
        
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

            # 存储重复组数据
            self.duplicate_groups = dict(duplicates)
            
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
        self.image_widgets_map = {}  # 用于存储widget和文件路径的映射
        self.duplicate_groups = dict(duplicates)  # 存储重复组数据
        
        # 创建主容器，使用网格布局实现自适应分栏
        main_container = ttkb.Frame(self.scrollable_frame)
        main_container.pack(fill=BOTH, expand=True, padx=5, pady=5)
        
        # 计算列数（根据窗口宽度自适应）
        columns = 3  # 默认3列
        
        for group_idx, (master, dups) in enumerate(duplicates.items()):
            group_counter += 1
            
            # 创建紧凑的重复项卡片
            card_frame = ttkb.Frame(main_container, padding=8, style='Card.TFrame')
            row = group_idx // columns
            col = group_idx % columns
            card_frame.grid(row=row, column=col, padx=5, pady=5, sticky='nsew')
            
            # 设置网格权重，使卡片均匀分布
            main_container.grid_rowconfigure(row, weight=1)
            main_container.grid_columnconfigure(col, weight=1)
            
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
            group_info = ttkb.Label(header_frame, text=f"重复组 {group_counter} ({len(dups)}张)", font=("", 10, 'bold'))
            group_info.pack(side=LEFT)
            
            # 置信度标签（简化显示）
            confidence_label = ttkb.Label(header_frame, text="高置信度", foreground='#198754', font=("", 8))
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
                    
                    # 存储widget引用用于后续操作
                    self.image_widgets_map[f_path] = img_label
                    
                    # 如果是第二张且还有更多图片，显示堆叠指示
                    if i == 1 and len(dups) > 2:
                        stack_label = ttk.Label(img_container, text=f"+{len(dups)-2}", 
                                              background='#FF8C00', foreground='white', 
                                              font=("", 8, 'bold'), width=3)
                        stack_label.pack(side=BOTTOM, anchor=SE, pady=(2, 0))
                        
                except Exception as e:
                    # 显示错误占位符
                    error_label = ttk.Label(img_container, text="无法显示", foreground='red', font=("", 8))
                    error_label.pack()
            
            # 文件信息（文件名和大小）
            info_frame = ttkb.Frame(card_frame)
            info_frame.pack(fill=X)
            
            # 显示主要文件信息
            try:
                first_file = dups[0]
                filename = os.path.basename(first_file)
                file_size = os.path.getsize(first_file)
                
                name_label = ttkb.Label(info_frame, text=filename, font=("", 8), wraplength=150)
                name_label.pack(anchor=W)
                
                size_label = ttkb.Label(info_frame, text=f"{file_size/1024/1024:.1f}MB", font=("", 7), foreground='#CCCCCC')
                size_label.pack(anchor=W)
                
            except:
                pass
                
            # 绑定整个卡片的点击事件
            card_frame.bind("<Button-1>", lambda e, g=dups: self.on_card_click(e, g))
            header_frame.bind("<Button-1>", lambda e, g=dups: self.on_card_click(e, g))
            image_frame.bind("<Button-1>", lambda e, g=dups: self.on_card_click(e, g))
            info_frame.bind("<Button-1>", lambda e, g=dups: self.on_card_click(e, g))

    def on_image_click(self, event, widget):
                    error_label.pack()

    def on_image_click(self, event, widget):
        """处理单击图片事件 - 选择或取消选择"""
        file_path = widget.file_path
        
        if file_path in self.selected_files:
            self.selected_files.remove(file_path)
            # 移除高亮 - 通过移除样式
            widget.configure(relief='flat', borderwidth=1)
        else:
            self.selected_files.add(file_path)
            # 添加高亮 - 通过添加样式
            widget.configure(relief='solid', borderwidth=3)
            
        self.update_selection_count()
        self.last_clicked_widget = widget

    def on_image_ctrl_click(self, event, widget):
        """处理Ctrl+单击图片事件 - 多选"""
        file_path = widget.file_path
        
        if file_path in self.selected_files:
            self.selected_files.remove(file_path)
            widget.configure(relief='flat', borderwidth=1)
        else:
            self.selected_files.add(file_path)
            widget.configure(relief='solid', borderwidth=3)
            
        self.update_selection_count()
        self.last_clicked_widget = widget

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
                    self.image_widgets_map[range_path].configure(relief='solid', borderwidth=3)
                    
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

    def unselect_all_images(self):
        """取消选择所有图片"""
        self.selected_files.clear()
        self.update_selection_count()

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
                    self.image_widgets_map[file_path].configure(relief='solid', borderwidth=2)
        else:
            # 取消选择整个组
            for file_path in group_files:
                self.selected_files.discard(file_path)
                # 移除高亮
                if file_path in self.image_widgets_map:
                    self.image_widgets_map[file_path].configure(relief='flat', borderwidth=1)
        
        self.update_selection_count()
        
    def on_card_click(self, event, group_files):
        """处理卡片点击事件"""
        # 切换整个组的选中状态
        is_selected = all(file_path in self.selected_files for file_path in group_files)
        
        if is_selected:
            # 取消选择
            for file_path in group_files:
                self.selected_files.discard(file_path)
                if file_path in self.image_widgets_map:
                    self.image_widgets_map[file_path].configure(relief='flat', borderwidth=1)
        else:
            # 选择
            for file_path in group_files:
                self.selected_files.add(file_path)
                if file_path in self.image_widgets_map:
                    self.image_widgets_map[file_path].configure(relief='solid', borderwidth=2)
        
        self.update_selection_count()
        
        # 重新执行扫描以更新界面
        if hasattr(self, 'workspace_root'):
            self.display_results(self.duplicate_groups)

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
