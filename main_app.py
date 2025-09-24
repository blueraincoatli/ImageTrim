
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

        # 1. 设置主题和颜色
        self.style = ttkb.Style(theme='superhero')
        self.colors = self.style.colors
        self.root.configure(bg=self.colors.get('bg'))

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
        ttkb.Label(self.left_frame, text="🔧 功能选择", font=("", 16, "bold"), bootstyle='inverse-primary').pack(pady=20)
        self.function_buttons_frame = ttkb.Frame(self.left_frame, style='primary.TFrame')
        self.function_buttons_frame.pack(fill=X, padx=10)

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
            
            # 使用Labelframe作为卡片
            card = ttkb.Labelframe(
                self.function_buttons_frame,
                text=f"{module.icon} {module.display_name}",
                bootstyle='info',
                padding=10
            )
            card.pack(fill=X, pady=5)
            
            desc = ttkb.Label(card, text=module.description, wraplength=220, bootstyle='inverse-info')
            desc.pack(fill=X, pady=(0, 10))

            btn = ttkb.Button(
                card,
                text="选择",
                bootstyle='outline-info',
                command=lambda m=module: self.switch_module(m)
            )
            btn.pack(anchor=E)
            
            self.module_buttons[name] = {'card': card, 'button': btn}

    def switch_module(self, module: BaseFunctionModule):
        """切换功能模块"""
        self.function_manager.activate_module(module.name)
        self.update_ui_for_module(module)

    def update_ui_for_module(self, module: BaseFunctionModule):
        """更新中栏和右栏以反映当前模块"""
        # 更新高亮状态
        for name, widgets in self.module_buttons.items():
            if name == module.name:
                widgets['card'].config(bootstyle='success') # 高亮选中的卡片
                widgets['button'].config(bootstyle='success')
            else:
                widgets['card'].config(bootstyle='info')
                widgets['button'].config(bootstyle='outline-info')

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
