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
from improved_deduplication_module import ImprovedDeduplicationModule


class ImprovedModernApp:
    """
    改进版现代化图片处理工具套件主程序
    - 采用 ttkbootstrap 实现现代UI
    - 采用左右布局，左侧分为功能选择和设置区，右侧为操作区
    - 插件化架构，动态加载功能模块
    """
    def __init__(self, root):
        self.root = root
        self.root.title("图片处理工具套件 - 改进版 v3.0")
        self.root.geometry("1400x900")
        self.root.minsize(1200, 700)

        # 1. 设置自定义主题和颜色
        self.setup_custom_theme()
        
        # 2. 初始化功能管理器
        self.function_manager = self.setup_function_manager()

        # 3. 创建主布局 (左右布局，左栏分上下两部分)
        self.create_main_layout()

        # 4. 加载并显示功能模块
        self.populate_function_list()

        # 5. 默认激活第一个功能
        if self.function_manager.get_module_names():
            first_module_name = self.function_manager.get_module_names()[0]
            self.function_manager.activate_module(first_module_name)
            self.update_ui_for_module(self.function_manager.get_module(first_module_name))
            
        # 确保所有样式都被正确应用
        self.root.update()

    def setup_custom_theme(self):
        """设置自定义主题"""
        # 使用darkly主题作为基础
        self.style = ttkb.Style(theme='darkly')
        
        # 设置全局字体大小，确保在各种显示器上都能清晰显示
        self.style.configure('.', font=('Arial', 18), foreground='white')
        
        # 配置按钮样式（不设置固定字体大小）
        self.style.configure('Primary.TButton', 
                           background='#FF8C00',  # 橙色
                           foreground='white',
                           bordercolor='#FF8C00')
        
        self.style.configure('Success.TButton',
                           background='#FF8C00',  # 橙色
                           foreground='white',
                           bordercolor='#FF8C00')
        
        self.style.configure('Danger.TButton',
                           background='#FF4500',  # 红色
                           foreground='white',
                           bordercolor='#FF4500')
        
        self.style.configure('Warning.TButton',
                           background='#FF8C00',  # 橙色
                           foreground='white',
                           bordercolor='#FF8C00')
        
        # 配置框架样式 - 统一使用深灰色背景
        self.style.configure('TFrame',
                           background='#1B1B1B')  # 所有框架使用深灰色背景
        
        self.style.configure('Primary.TFrame',
                           background='#1B1B1B')  # 深灰色用于左栏

        self.style.configure('Secondary.TFrame',
                           background='#1B1B1B')  # 深灰色用于右栏
                            
        # 配置卡片框架样式（功能卡片）
        self.style.configure('Card.TFrame',
                           background='#1B1B1B')  # 深灰色背景，与设置区一致
                           
        # 配置选中卡片样式
        self.style.configure('SelectedCard.TFrame',
                           background='#353535',  # 浅灰色背景（选中状态）
                           relief='solid',
                           borderwidth=2,
                           bordercolor='#FF8C00')  # 橙色边框
        
        # 配置标签框架样式 - 标题栏使用深灰色
        self.style.configure('Info.TLabelframe',
                           background='#1B1B1B',  # 深灰色背景
                           foreground='#FF8C00')  # 不设置固定字体
        
        self.style.configure('TLabelframe.Label',
                           background='#1B1B1B',  # 深灰色背景
                           foreground='#FF8C00')  # 不设置固定字体
        
        # 配置标签样式 - 统一使用深灰色背景
        self.style.configure('TLabel',
                           background='#1B1B1B',  # 深灰色背景
                           foreground='#FFFFFF')  # 不设置固定字体
        
        # 配置逆色标签样式
        self.style.configure('Inverse.TLabel',
                           background='#353535',  # 浅灰色背景
                           foreground='#FFFFFF')  # 不设置固定字体
        
        # 配置输入框样式
        self.style.configure('TEntry',
                           fieldbackground='#4B4B4B',  # 深灰色输入框
                           foreground='#FFFFFF')       # 不设置固定字体
        
        # 配置滚动条样式
        self.style.configure('TScrollbar',
                           background='#FF8C00',       # 橙色滚动条
                           troughcolor='#2B2B2B',      # 深灰色滑槽
                           bordercolor='#2B2B2B')
        
        # 配置进度条样式
        self.style.configure('TProgressbar',
                           background='#FF8C00',       # 橙色进度条
                           troughcolor='#4B2B2B',      # 深灰色滑槽
                           bordercolor='#2B2B2B')
        
        # 设置主窗口背景色
        self.root.configure(bg='#1B1B1B')
        
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
        
        # 注册改进版的去重模块
        improved_dedup_module = ImprovedDeduplicationModule()
        manager.register_module(improved_dedup_module)
        
        # 如果modules目录存在，也加载其中的模块
        modules_dir = 'modules'
        if os.path.exists(modules_dir):
            for filename in os.listdir(modules_dir):
                if filename.endswith('_module.py') and filename != 'deduplication_module.py':
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
        """创建左右布局，左栏分为上下两部分"""
        # 主水平PanedWindow，用于分隔左侧功能区和右侧操作区
        self.main_paned_window = ttkb.PanedWindow(self.root, orient=HORIZONTAL)
        self.main_paned_window.pack(fill=BOTH, expand=True, padx=10, pady=10)

        # 左侧框架（功能选择 + 设置控制）
        self.left_frame = ttkb.Frame(self.main_paned_window, style='primary.TFrame')
        self.main_paned_window.add(self.left_frame, weight=30)

        # 左侧垂直PanedWindow，用于分隔功能选择和设置
        self.left_paned_window = ttkb.PanedWindow(self.left_frame, orient=VERTICAL)
        self.left_paned_window.pack(fill=BOTH, expand=True)

        # 左上部分 (功能选择面板)
        self.function_selector_frame = ttkb.Frame(self.left_paned_window, style='primary.TFrame')
        self.left_paned_window.add(self.function_selector_frame, weight=40)

        # 功能选择标题
        ttkb.Label(self.function_selector_frame, text="🔧 Function Selection", font=("", 16, "bold"), style='Inverse.TLabel').pack(pady=10, padx=10, anchor=W)
        
        # 功能按钮容器
        self.function_buttons_frame = ttkb.Frame(self.function_selector_frame, style='Primary.TFrame')
        self.function_buttons_frame.pack(fill=BOTH, expand=True, padx=10, pady=10)

        # 左下部分 (设置控制面板)
        self.settings_frame = ttkb.Frame(self.left_paned_window, style='Primary.TFrame')
        self.left_paned_window.add(self.settings_frame, weight=60)

        # 设置标题
        ttkb.Label(self.settings_frame, text="⚙️ Settings", font=("", 16, "bold"), style='Inverse.TLabel').pack(pady=10, padx=10, anchor=W)
        
        # 设置容器
        self.settings_container = ttkb.Frame(self.settings_frame, style='Primary.TFrame')
        self.settings_container.pack(fill=BOTH, expand=True, padx=10, pady=10)

        # 右侧部分 (操作区)
        self.right_frame = ttkb.Frame(self.main_paned_window, style='Secondary.TFrame')
        self.main_paned_window.add(self.right_frame, weight=70)
        
        # 操作区标题
        self.right_title = ttkb.Label(self.right_frame, text="🎯 Operations & Results", font=("", 16, "bold"), style='Inverse.TLabel')
        self.right_title.pack(pady=10, padx=10, anchor=W)
        
        # 操作区容器
        self.workspace_container = ttkb.Frame(self.right_frame, style='Secondary.TFrame')
        self.workspace_container.pack(fill=BOTH, expand=True, padx=10, pady=10)

    def populate_function_list(self):
        """根据加载的模块创建功能按钮"""
        self.module_buttons = {}
        for name in self.function_manager.get_module_names():
            module = self.function_manager.get_module(name)
            
            # 使用Frame作为卡片，支持点击选择
            card = ttkb.Frame(
                self.function_buttons_frame,
                style='Card.TFrame',  # 使用深灰色背景
                padding=15,
                relief='flat',
                borderwidth=0
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
        """更新界面以反映当前模块"""
        # 更新高亮状态
        for name, widgets in self.module_buttons.items():
            if name == module.name:
                # 选中的卡片使用选中样式（带橙色边框）
                widgets['card'].config(style='SelectedCard.TFrame')
                widgets['title'].config(style='Inverse.TLabel')
                widgets['desc'].config(style='Inverse.TLabel')
            else:
                # 未选中的卡片使用卡片样式（浅灰色背景，无边框）
                widgets['card'].config(style='Card.TFrame')
                widgets['title'].config(style='Inverse.TLabel')
                widgets['desc'].config(style='Inverse.TLabel')

        # 清空现有UI
        for widget in self.settings_container.winfo_children():
            widget.destroy()
        for widget in self.workspace_container.winfo_children():
            widget.destroy()

        # 更新标题
        self.right_title.config(text=f"🎯 {module.display_name} Operations & Results")

        # 加载新UI
        try:
            # 让模块自己创建并返回它的设置UI面板（放在左侧下部）
            settings_panel = module.create_settings_ui(self.settings_container)
            if settings_panel:
                settings_panel.pack(fill=BOTH, expand=True)

            # 让模块创建工作区UI（放在右侧）
            workspace_panel = module.create_workspace_ui(self.workspace_container)
            if workspace_panel:
                workspace_panel.pack(fill=BOTH, expand=True)
            else: # 如果模块没有单独的工作区UI，显示一个提示
                ttkb.Label(self.workspace_container, text=f"'{module.display_name}' function results will be displayed here.", bootstyle='inverse-secondary').pack(pady=20)

        except Exception as e:
            ttkb.Label(self.settings_container, text=f"Failed to load UI: {e}", bootstyle='danger').pack()
            print(f"[ERROR] Failed to load UI for module {module.name}: {e}")


if __name__ == "__main__":
    # 确保在Windows上使用'win'主题类型以获得最佳外观
    if os.name == 'nt':
        root = ttkb.Window(themename="superhero", hdpi=True, scaling=True)
    else:
        root = ttkb.Window(themename="superhero")
        
    app = ImprovedModernApp(root)
    root.mainloop()