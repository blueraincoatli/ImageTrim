
import tkinter as tk
from tkinter import ttk
import os
import importlib
import importlib.util  # 显式导入util模块
import inspect
import sys
import traceback

try:
    import ttkbootstrap as ttkb
    from ttkbootstrap.constants import *
except ImportError:
    print("错误: ttkbootstrap 未安装。请运行 'pip install ttkbootstrap'")
    exit()

# 假设 function_modules.py 在同一目录下
from function_modules import BaseFunctionModule, FunctionManager

class ModernApp:
    """
    现代化图片处理工具套件主程序
    - 采用 ttkbootstrap 实现现代UI
    - 使用 PanedWindow 实现可拖拽的三栏布局
    - 插件化架构，动态加载功能模块
    """
    def __init__(self, root):
        self.root = root
        self.root.title("图片处理工具套件 - v2.0")
        self.root.geometry("1400x800")
        self.root.minsize(1200, 700)

        # 1. 设置自定义主题和颜色
        self.setup_custom_theme()
        
        # 2. 初始化功能管理器
        self.function_manager = self.setup_function_manager()

        # 3. 创建主布局
        self.create_main_layout()

        # 4. 加载并显示功能模块
        self.populate_function_list()

        # 5. 默认激活第一个功能
        if self.function_manager.get_module_names():
            first_module_name = self.function_manager.get_module_names()[0]
            self.function_manager.activate_module(first_module_name)
            self.update_ui_for_module(self.function_manager.get_module(first_module_name))

    def setup_custom_theme(self):
        """设置自定义主题"""
        # 使用darkly主题作为基础
        self.style = ttkb.Style(theme='darkly')
        
        # 自定义颜色配置
        self.style.configure('.', font=('Arial', 14))  # 设置默认字体大小为14px
        
        # 配置按钮样式为橙色
        self.style.configure('Primary.TButton', 
                           background='#FF8C00',  # 橙色
                           foreground='white',
                           bordercolor='#FF8C00',
                           font=('Arial', 14))
        
        self.style.configure('Success.TButton',
                           background='#FFA500',  # 橙色
                           foreground='white',
                           bordercolor='#FFA500',
                           font=('Arial', 14))
        
        self.style.configure('Danger.TButton',
                           background='#FF4500',  # 深橙色
                           foreground='white',
                           bordercolor='#FF4500',
                           font=('Arial', 14))
        
        self.style.configure('Warning.TButton',
                           background='#FFA07A',  # 浅橙色
                           foreground='white',
                           bordercolor='#FFA07A',
                           font=('Arial', 14))
        
        # 配置框架样式
        self.style.configure('Primary.TFrame',
                           background='#1B1B1B')  # 更深的灰色用于左栏
        
        self.style.configure('Secondary.TFrame',
                           background='#2B2B2B')  # 深灰色用于中右栏和主窗口
                           
        # 配置信息框架样式
        self.style.configure('Info.TFrame',
                           background='#3B5998')  # 蓝色用于未选中的功能卡片
                           
        # 配置成功框架样式
        self.style.configure('Success.TFrame',
                           background='#28a745')  # 绿色用于选中的功能卡片
        
        # 配置标签框架样式
        self.style.configure('Info.TLabelframe',
                           background='#2B2B2B',
                           foreground='#FF8C00',  # 橙色文字
                           font=('Arial', 14))
        
        self.style.configure('TLabelframe.Label',
                           background='#2B2B2B',
                           foreground='#FF8C00',  # 橙色文字
                           font=('Arial', 14))
        
        # 配置标签样式
        self.style.configure('TLabel',
                           background='#1B1B1B',  # 左栏背景色
                           foreground='#FFFFFF',  # 白色文字
                           font=('Arial', 14))
        
        # 配置输入框样式
        self.style.configure('TEntry',
                           fieldbackground='#4B4B4B',  # 深灰色输入框
                           foreground='#FFFFFF',       # 白色文字
                           font=('Arial', 14))
        
        # 配置滚动条样式
        self.style.configure('TScrollbar',
                           background='#FF8C00',       # 橙色滚动条
                           troughcolor='#2B2B2B',      # 深灰色滑槽
                           bordercolor='#2B2B2B')
        
        # 配置进度条样式
        self.style.configure('TProgressbar',
                           background='#FF8C00',       # 橙色进度条
                           troughcolor='#4B4B4B',      # 深灰色滑槽
                           bordercolor='#2B2B2B')
        
        # 设置主窗口背景色
        self.root.configure(bg='#2B2B2B')
        
    def setup_rounded_styles(self):
        """设置改进的样式"""
        # 配置按钮样式以获得更好的外观
        self.style.configure('Primary.TButton', 
                           borderwidth=1,
                           relief='flat',
                           padding=(10, 5))
        
        # 配置框架样式
        self.style.configure('Primary.TFrame',
                           borderwidth=1,
                           relief='flat')
        
        # 配置标签框架样式
        self.style.configure('Info.TLabelframe',
                           borderwidth=1,
                           relief='flat',
                           padding=10)
        
        # 配置成功按钮样式
        self.style.configure('Success.TButton',
                           borderwidth=1,
                           relief='flat',
                           padding=(10, 5))
        
        # 配置危险按钮样式
        self.style.configure('Danger.TButton',
                           borderwidth=1,
                           relief='flat',
                           padding=(10, 5))


    def setup_function_manager(self):
        print(f"--- Diagnosing importlib in setup_function_manager ---")
        try:
            print(f"  importlib file: {importlib.__file__}")
        except AttributeError:
            print("  importlib is a built-in module and has no __file__ attribute.")
        print(f"  sys.path: {sys.path}")
        print(f"-----------------------------------------------------")
        manager = FunctionManager()
        modules_dir = 'modules'
        if not os.path.exists(modules_dir):
            print(f"警告: 功能模块目录 '{modules_dir}' 不存在。")
            return manager

        for filename in os.listdir(modules_dir):
            if filename.endswith('_module.py'):
                module_name = filename[:-3]
                try:
                    module_spec = importlib.util.spec_from_file_location(module_name, os.path.join(modules_dir, filename))
                    imported_module = importlib.util.module_from_spec(module_spec)
                    module_spec.loader.exec_module(imported_module)

                    for name, cls in inspect.getmembers(imported_module, inspect.isclass):
                        if issubclass(cls, BaseFunctionModule) and cls is not BaseFunctionModule:
                            instance = cls()
                            manager.register_module(instance)
                            print(f"[OK] 成功加载模块: {instance.display_name}")
                except Exception as e:
                    print(f"[ERROR] Failed to load module {module_name}: {e}")
                    traceback.print_exc()
        return manager

    def create_main_layout(self):
        """创建可拖拽的三栏式布局"""
        # 主 PanedWindow
        self.main_paned_window = ttkb.PanedWindow(self.root, orient=HORIZONTAL)
        self.main_paned_window.pack(fill=BOTH, expand=True, padx=10, pady=10)

        # 左栏 (功能选择)
        self.left_frame = ttkb.Frame(self.main_paned_window, width=280, style='primary.TFrame')
        self.main_paned_window.add(self.left_frame, weight=20)
        self.left_frame.pack_propagate(False)

        # 中栏和右栏的 PanedWindow
        self.center_right_paned = ttkb.PanedWindow(self.main_paned_window, orient=HORIZONTAL)
        self.main_paned_window.add(self.center_right_paned, weight=80)

        # 中栏 (设置与进度)
        self.center_frame = ttkb.Frame(self.center_right_paned, width=350)
        self.center_right_paned.add(self.center_frame, weight=25)
        self.center_frame.pack_propagate(False)

        # 右栏 (功能工作区)
        self.right_frame = ttkb.Frame(self.center_right_paned, style='secondary.TFrame')
        self.center_right_paned.add(self.right_frame, weight=55)

        # 初始化各栏内容
        self.init_left_panel()
        self.init_center_panel()
        self.init_right_panel()

    def init_left_panel(self):
        """初始化左栏内容"""
        # 设置左栏背景为更深的灰色
        self.left_frame.configure(style='Primary.TFrame')
        ttkb.Label(self.left_frame, text="🔧 功能选择", font=("", 16, "bold"), bootstyle='inverse-primary').pack(pady=20)
        self.function_buttons_frame = ttkb.Frame(self.left_frame, style='Primary.TFrame')
        self.function_buttons_frame.pack(fill=BOTH, expand=True, padx=10, pady=10)

    def init_center_panel(self):
        """初始化中栏内容"""
        self.center_title = ttkb.Label(self.center_frame, text="⚙️ 参数设置", font=("", 16, "bold"))
        self.center_title.pack(pady=20)
        self.settings_container = ttkb.Frame(self.center_frame)
        self.settings_container.pack(fill=BOTH, expand=True, padx=10, pady=10)

    def init_right_panel(self):
        """初始化右栏内容"""
        self.right_title = ttkb.Label(self.right_frame, text="🎯 工作区", font=("", 16, "bold"), bootstyle='inverse-secondary')
        self.right_title.pack(pady=20)
        self.workspace_container = ttkb.Frame(self.right_frame, style='secondary.TFrame')
        self.workspace_container.pack(fill=BOTH, expand=True, padx=10, pady=10)

    def populate_function_list(self):
        """根据加载的模块创建功能按钮"""
        self.module_buttons = {}
        for name in self.function_manager.get_module_names():
            module = self.function_manager.get_module(name)
            
            # 使用Frame作为卡片，支持点击选择
            card = ttkb.Frame(
                self.function_buttons_frame,
                bootstyle='info',  # 使用bootstyle而不是style
                padding=15
            )
            card.pack(fill=X, pady=5, padx=5, ipady=10)
            
            # 卡片内容
            title_label = ttkb.Label(
                card, 
                text=f"{module.icon} {module.display_name}", 
                font=("", 14, "bold"),
                bootstyle='inverse-info'
            )
            title_label.pack(anchor=W)
            
            desc_label = ttkb.Label(
                card, 
                text=module.description, 
                wraplength=220, 
                bootstyle='inverse-info'
            )
            desc_label.pack(fill=X, pady=(5, 0))
            
            # 绑定点击事件
            card.bind("<Button-1>", lambda e, m=module: self.switch_module(m))
            title_label.bind("<Button-1>", lambda e, m=module: self.switch_module(m))
            desc_label.bind("<Button-1>", lambda e, m=module: self.switch_module(m))
            
            self.module_buttons[name] = {'card': card, 'title': title_label, 'desc': desc_label}

    def switch_module(self, module: BaseFunctionModule):
        """切换功能模块"""
        # 先停用当前模块
        if self.function_manager.active_module:
            self.function_manager.active_module.on_deactivate()
            
        # 激活新模块
        self.function_manager.activate_module(module.name)
        self.update_ui_for_module(module)

    def update_ui_for_module(self, module: BaseFunctionModule):
        """更新中栏和右栏以反映当前模块"""
        # 更新高亮状态
        for name, widgets in self.module_buttons.items():
            if name == module.name:
                # 选中的卡片使用成功样式
                widgets['card'].config(bootstyle='success')
                widgets['title'].config(bootstyle='inverse-success')
                widgets['desc'].config(bootstyle='inverse-success')
            else:
                # 未选中的卡片使用信息样式
                widgets['card'].config(bootstyle='info')
                widgets['title'].config(bootstyle='inverse-info')
                widgets['desc'].config(bootstyle='inverse-info')

        # 清空现有UI
        for widget in self.settings_container.winfo_children():
            widget.destroy()
        for widget in self.workspace_container.winfo_children():
            widget.destroy()

        # 更新标题
        self.center_title.config(text=f"⚙️ {module.display_name} 设置")
        self.right_title.config(text=f"🎯 {module.display_name} 工作区")

        # 加载新UI
        try:
            # 让模块自己创建并返回它的UI面板
            settings_panel = module.create_settings_ui(self.settings_container)
            if settings_panel:
                settings_panel.pack(fill=BOTH, expand=True)

            # 同样为工作区创建UI
            workspace_panel = module.create_workspace_ui(self.workspace_container)
            if workspace_panel:
                workspace_panel.pack(fill=BOTH, expand=True)
            else: # 如果模块没有单独的工作区UI，显示一个提示
                ttkb.Label(self.workspace_container, text=f"'{module.display_name}' 功能的结果将在这里显示。").pack(pady=20)

        except Exception as e:
            ttkb.Label(self.settings_container, text=f"加载UI失败: {e}", bootstyle='danger').pack()
            print(f"[ERROR] 加载模块 {module.name} 的UI时出错: {e}")


if __name__ == "__main__":
    # 确保在Windows上使用'win'主题类型以获得最佳外观
    if os.name == 'nt':
        root = ttkb.Window(themename="superhero", hdpi=True, scaling=True)
    else:
        root = ttkb.Window(themename="superhero")
        
    app = ModernApp(root)
    root.mainloop()
