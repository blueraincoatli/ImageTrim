# -*- coding: utf-8 -*-
"""
公共UI组件库
统一UI创建模式，消除重复代码
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from typing import Dict, List, Any, Optional, Callable, Union
from pathlib import Path

try:
    import ttkbootstrap as ttkb
    from ttkbootstrap.constants import *
    from PIL import Image, ImageTk
    TTKB_AVAILABLE = True
except ImportError:
    ttkb = None
    ImageTk = None
    TTKB_AVAILABLE = False
    print("Warning: ttkbootstrap not available. Using standard tkinter.")


class UIFactory:
    """UI组件工厂类"""

    @staticmethod
    def create_label_frame(parent: ttk.Widget, text: str, padding: int = 10) -> ttk.Frame:
        """
        创建统一的标签框架

        Args:
            parent: 父组件
            text: 标题文本
            padding: 内边距

        Returns:
            创建的框架组件
        """
        if ttkb:
            return ttkb.Labelframe(parent, text=text, padding=padding)
        else:
            frame = ttk.Frame(parent, relief='ridge', borderwidth=2)
            frame.pack_propagate(False)
            # 添加标题标签
            title_label = ttk.Label(frame, text=text, font=('', 10, 'bold'))
            title_label.pack(anchor='w', padx=5, pady=(2, 5))
            # 内容框架
            content_frame = ttk.Frame(frame)
            content_frame.pack(fill='both', expand=True, padx=padding, pady=(0, padding))
            return content_frame

    @staticmethod
    def create_button_group(parent: ttk.Widget, buttons: List[Dict[str, Any]]) -> ttk.Frame:
        """
        创建按钮组

        Args:
            parent: 父组件
            buttons: 按钮配置列表
                [
                    {"text": "按钮文本", "command": 回调函数, "style": "按钮样式", "width": 宽度},
                    ...
                ]

        Returns:
            按钮框架
        """
        btn_frame = ttk.Frame(parent)

        for i, btn_config in enumerate(buttons):
            text = btn_config.get("text", "Button")
            command = btn_config.get("command", lambda: None)
            style = btn_config.get("style", "")
            width = btn_config.get("width", 10)

            if ttkb and style:
                btn = ttkb.Button(btn_frame, text=text, command=command, bootstyle=style, width=width)
            else:
                btn = ttk.Button(btn_frame, text=text, command=command, width=width)

            btn.pack(side='left', padx=(0 if i == 0 else 5, 0))

        return btn_frame

    @staticmethod
    def create_path_selector(parent: ttk.Widget,
                           add_callback: Callable,
                           remove_callback: Callable,
                           clear_callback: Callable,
                           height: int = 4) -> Dict[str, ttk.Widget]:
        """
        创建路径选择器组件

        Args:
            parent: 父组件
            add_callback: 添加路径回调
            remove_callback: 移除路径回调
            clear_callback: 清空路径回调
            height: 列表框高度

        Returns:
            包含创建组件的字典
        """
        components = {}

        # 路径列表显示区域
        listbox = tk.Listbox(parent, height=height, relief='flat', highlightthickness=0)
        listbox.pack(fill='x', pady=(0, 5))
        components['listbox'] = listbox

        # 按钮配置
        buttons = [
            {"text": "Add Path", "command": add_callback, "style": "success" if ttkb else "", "width": 10},
            {"text": "Remove Path", "command": remove_callback, "style": "danger" if ttkb else "", "width": 10},
            {"text": "Clear Paths", "command": clear_callback, "style": "warning" if ttkb else "", "width": 10}
        ]

        btn_frame = UIFactory.create_button_group(parent, buttons)
        components['button_frame'] = btn_frame

        return components

    @staticmethod
    def create_slider_control(parent: ttk.Widget,
                            label_text: str,
                            from_val: float,
                            to_val: float,
                            initial_val: float,
                            command: Optional[Callable] = None) -> Dict[str, ttk.Widget]:
        """
        创建滑块控制器

        Args:
            parent: 父组件
            label_text: 标签文本
            from_val: 最小值
            to_val: 最大值
            initial_val: 初始值
            command: 值改变时的回调

        Returns:
            包含组件的字典
        """
        components = {}

        frame = ttk.Frame(parent)
        frame.pack(fill='x', pady=5)

        # 标签
        label = ttk.Label(frame, text=f"{label_text}:")
        label.pack(side='left', padx=(0, 10))
        components['label'] = label

        # 变量
        var = tk.DoubleVar(value=initial_val)
        components['variable'] = var

        # 滑块
        if ttkb:
            scale = ttkb.Scale(frame, from_=from_val, to=to_val, variable=var,
                             orient='horizontal', command=command)
        else:
            scale = ttk.Scale(frame, from_=from_val, to=to_val, variable=var,
                            orient='horizontal', command=command)
        scale.pack(side='left', fill='x', expand=True)
        components['scale'] = scale

        # 值显示标签
        value_label = ttk.Label(frame, text=f"{initial_val:.0f}%", width=5)
        value_label.pack(side='left', padx=(10, 0))
        components['value_label'] = value_label

        # 默认命令
        if command is None:
            def default_command(val):
                value_label.config(text=f"{float(val):.0f}%")
            scale.config(command=default_command)

        return components

    @staticmethod
    def create_checkbox(parent: ttk.Widget, text: str, variable: tk.BooleanVar,
                       style: str = None) -> ttk.Checkbutton:
        """
        创建复选框

        Args:
            parent: 父组件
            text: 显示文本
            variable: 关联变量
            style: 样式（仅ttkbootstrap）

        Returns:
            复选框组件
        """
        if ttkb and style:
            return ttkb.Checkbutton(parent, text=text, variable=variable, bootstyle=style)
        else:
            return ttk.Checkbutton(parent, text=text, variable=variable)

    @staticmethod
    def create_progress_area(parent: ttk.Widget) -> Dict[str, ttk.Widget]:
        """
        创建进度显示区域

        Args:
            parent: 父组件

        Returns:
            包含组件的字典
        """
        components = {}

        frame = ttk.Frame(parent)
        frame.pack(fill='x', pady=5)

        # 统计标签
        stats_label = ttk.Label(frame, text="Ready", font=('', 10))
        stats_label.pack(side='left')
        components['stats_label'] = stats_label

        # 选择计数标签
        selection_label = ttk.Label(frame, text="Selected: 0", font=('', 10))
        selection_label.pack(side='right')
        components['selection_label'] = selection_label

        return components

    @staticmethod
    def create_action_buttons(parent: ttk.Widget,
                             start_callback: Callable,
                             stop_callback: Callable,
                             additional_buttons: List[Dict] = None) -> Dict[str, ttk.Widget]:
        """
        创建操作按钮组

        Args:
            parent: 父组件
            start_callback: 开始回调
            stop_callback: 停止回调
            additional_buttons: 额外按钮配置

        Returns:
            包含组件的字典
        """
        components = {}

        frame = UIFactory.create_label_frame(parent, "Operation Control", 10)

        # 主要按钮
        buttons = [
            {"text": "▶️ Start Scan", "command": start_callback, "style": "success" if ttkb else "", "width": 15},
            {"text": "⏹️ Stop", "command": stop_callback, "style": "danger" if ttkb else "", "width": 15}
        ]

        btn_frame = UIFactory.create_button_group(frame, buttons)

        components['frame'] = frame
        components['start_btn'] = btn_frame.winfo_children()[0]  # 第一个按钮
        components['stop_btn'] = btn_frame.winfo_children()[1]    # 第二个按钮

        # 初始状态
        components['stop_btn'].config(state='disabled')

        return components


class ScrollableFrame:
    """可滚动框架类"""

    def __init__(self, parent: ttk.Widget, **kwargs):
        self.parent = parent
        self.canvas = tk.Canvas(parent, bg="#2B2B2B", **kwargs)
        self.v_scrollbar = ttk.Scrollbar(parent, orient='vertical', command=self.canvas.yview)
        self.canvas.configure(yscrollcommand=self.v_scrollbar.set)

        self.canvas.pack(side='left', fill='both', expand=True)
        self.v_scrollbar.pack(side='right', fill='y')

        self.main_container = ttk.Frame(self.canvas)
        self.canvas_window = self.canvas.create_window((0, 0), window=self.main_container, anchor='nw')

        # 绑定事件
        self.main_container.bind('<Configure>', self._on_frame_configure)
        self.canvas.bind('<Configure>', self._on_canvas_configure)

    def _on_frame_configure(self, event=None):
        """框架配置变化时更新滚动区域"""
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def _on_canvas_configure(self, event=None):
        """画布配置变化时调整窗口大小"""
        self.canvas.itemconfig(self.canvas_window, width=event.width)

    def get_container(self) -> ttk.Frame:
        """获取主容器框架"""
        return self.main_container


class ImageDisplayHelper:
    """图片显示辅助类"""

    def __init__(self, max_cache_size: int = 100):
        self.image_cache = {}
        self.max_cache_size = max_cache_size
        self.access_order = []

    def get_thumbnail(self, file_path: str, size: tuple = (80, 80)) -> Optional[Any]:
        """
        获取图片缩略图

        Args:
            file_path: 图片文件路径
            size: 缩略图尺寸

        Returns:
            PhotoImage对象或None
        """
        if ImageTk is None:
            return None
        # 检查缓存
        if file_path in self.image_cache:
            self._update_access_order(file_path)
            return self.image_cache[file_path]

        # 加载图片
        try:
            if not Path(file_path).exists():
                return None

            with Image.open(file_path) as img:
                # 转换格式
                if img.mode in ('RGBA', 'LA', 'P'):
                    img = img.convert('RGB')

                # 创建缩略图
                img.thumbnail(size, Image.Resampling.LANCZOS)
                photo = ImageTk.PhotoImage(img) if ImageTk else None

                # 缓存图片
                self._add_to_cache(file_path, photo)
                return photo

        except Exception:
            return None

    def _update_access_order(self, file_path: str):
        """更新访问顺序"""
        if file_path in self.access_order:
            self.access_order.remove(file_path)
        self.access_order.append(file_path)

    def _add_to_cache(self, file_path: str, photo: Any):
        """添加到缓存"""
        # 清理缓存
        if len(self.image_cache) >= self.max_cache_size:
            oldest_file = self.access_order.pop(0)
            del self.image_cache[oldest_file]

        self.image_cache[file_path] = photo
        self.access_order.append(file_path)

    def clear_cache(self):
        """清空缓存"""
        self.image_cache.clear()
        self.access_order.clear()


class DialogManager:
    """对话框管理器"""

    @staticmethod
    def show_error(title: str, message: str):
        """显示错误对话框"""
        messagebox.showerror(title, message)

    @staticmethod
    def show_info(title: str, message: str):
        """显示信息对话框"""
        messagebox.showinfo(title, message)

    @staticmethod
    def show_warning(title: str, message: str):
        """显示警告对话框"""
        messagebox.showwarning(title, message)

    @staticmethod
    def ask_yes_no(title: str, message: str) -> bool:
        """显示是/否对话框"""
        return messagebox.askyesno(title, message)

    @staticmethod
    def ask_directory(title: str = "选择目录") -> Optional[str]:
        """显示目录选择对话框"""
        return filedialog.askdirectory(title=title)

    @staticmethod
    def ask_save_as(title: str = "保存文件",
                   filetypes: List[tuple] = None) -> Optional[str]:
        """显示保存文件对话框"""
        if filetypes is None:
            filetypes = [("All files", "*.*")]
        return filedialog.asksaveasfilename(title=title, filetypes=filetypes)


class GridLayoutManager:
    """网格布局管理器"""

    def __init__(self, container: ttk.Widget, min_column_width: int = 250, max_columns: int = 6):
        self.container = container
        self.min_column_width = min_column_width
        self.max_columns = max_columns

    def calculate_columns(self) -> int:
        """计算合适的列数"""
        try:
            self.container.update_idletasks()
            container_width = self.container.winfo_width()
            if container_width > 0:
                return max(1, min(self.max_columns, container_width // self.min_column_width))
            return 3
        except:
            return 3

    def setup_grid_weights(self, max_rows: int = 100):
        """设置网格权重"""
        try:
            for i in range(max_rows):
                self.container.grid_rowconfigure(i, weight=1)
            for j in range(self.max_columns):
                self.container.grid_columnconfigure(j, weight=1)
        except:
            pass

    def add_widget(self, widget: ttk.Widget, index: int, padx: int = 5, pady: int = 5):
        """添加组件到网格"""
        columns = self.calculate_columns()
        row = index // columns
        col = index % columns
        widget.grid(row=row, column=col, padx=padx, pady=pady, sticky='nsew')


class StyleManager:
    """样式管理器"""

    @staticmethod
    def configure_standard_styles():
        """配置标准样式"""
        if not ttkb:
            return

        try:
            style = ttkb.Style()

            # 配置标题样式
            style.configure('Title.TLabel', font=('', 12, 'bold'))

            # 配置信息样式
            style.configure('Info.TLabel', font=('', 10))

            # 配置警告样式
            style.configure('Warning.TLabel', font=('', 10), foreground='orange')

            # 配置成功样式
            style.configure('Success.TLabel', font=('', 10), foreground='green')

            # 配置错误样式
            style.configure('Error.TLabel', font=('', 10), foreground='red')

        except Exception:
            pass  # 忽略样式配置错误

    @staticmethod
    def get_button_style(action_type: str) -> str:
        """
        根据操作类型获取按钮样式

        Args:
            action_type: 操作类型 (success, danger, warning, info, primary)

        Returns:
            样式名称
        """
        if not ttkb:
            return ""

        style_map = {
            'success': 'success',
            'danger': 'danger',
            'warning': 'warning',
            'info': 'info',
            'primary': 'primary',
            'secondary': 'secondary'
        }
        return style_map.get(action_type, '')


# 便利函数
def create_standard_settings_ui(parent: ttk.Widget,
                              path_callbacks: Dict[str, Callable],
                              scan_callbacks: Dict[str, Callable]) -> Dict[str, Any]:
    """
    创建标准设置UI

    Args:
        parent: 父组件
        path_callbacks: 路径相关回调 {"add": 添加回调, "remove": 移除回调, "clear": 清空回调}
        scan_callbacks: 扫描相关回调 {"start": 开始回调, "stop": 停止回调}

    Returns:
        包含所有UI组件的字典
    """
    components = {}

    # 路径选择器
    paths_frame = UIFactory.create_label_frame(parent, "Scan Paths")
    path_components = UIFactory.create_path_selector(
        paths_frame,
        path_callbacks['add'],
        path_callbacks['remove'],
        path_callbacks['clear']
    )
    components.update(path_components)

    # 检测设置
    options_frame = UIFactory.create_label_frame(parent, "Detection Settings")

    # 相似度滑块
    slider_components = UIFactory.create_slider_control(
        options_frame,
        "Similarity Threshold",
        70, 100, 95
    )
    components['sensitivity'] = slider_components

    # 子目录复选框
    subdirs_var = tk.BooleanVar(value=True)
    subdirs_check = UIFactory.create_checkbox(
        options_frame,
        "Include Subdirectories",
        subdirs_var,
        "round-toggle" if ttkb else None
    )
    subdirs_check.pack(fill='x', pady=5)
    components['subdirs_var'] = subdirs_var

    # 操作控制
    action_components = UIFactory.create_action_buttons(
        parent,
        scan_callbacks['start'],
        scan_callbacks['stop']
    )
    components.update(action_components)

    return components