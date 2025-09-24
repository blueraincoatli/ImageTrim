
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
import tkinter as tk
from tkinter import ttk, Frame

class BaseFunctionModule(ABC):
    """
    功能模块基类 V2
    - 定义了所有功能模块必须实现的接口
    - 区分了设置UI和工作区UI的创建
    """
    def __init__(self, name: str, display_name: str, description: str = "", icon: str = "❓"):
        self.name = name
        self.display_name = display_name
        self.description = description
        self.icon = icon
        self.is_active = False
        self.is_running = False
        self.progress_callback = None
        self.log_callback = None

    @abstractmethod
    def create_settings_ui(self, parent: Frame) -> Optional[Frame]:
        """
        创建并返回功能对应的“设置”UI面板（中栏）
        """
        pass

    @abstractmethod
    def create_workspace_ui(self, parent: Frame) -> Optional[Frame]:
        """
        创建并返回功能对应的“工作区”UI面板（右栏）
        """
        pass

    @abstractmethod
    def execute(self, params: Dict[str, Any]):
        """
        在独立线程中执行功能的核心逻辑。
        应通过回调函数更新UI。
        """
        pass

    @abstractmethod
    def stop_execution(self):
        """
        停止正在执行的操作
        """
        pass

    def set_callbacks(self, progress_callback, log_callback):
        """设置回调函数以与主UI通信"""
        self.progress_callback = progress_callback
        self.log_callback = log_callback

    def on_activate(self):
        """功能被激活时的回调"""
        self.is_active = True
        if self.log_callback:
            self.log_callback(f"模块 '{self.display_name}' 已激活", "info")

    def on_deactivate(self):
        """功能被停用时的回调"""
        self.is_active = False

class FunctionManager:
    """功能管理器"""

    def __init__(self):
        self.modules: Dict[str, BaseFunctionModule] = {}
        self.active_module: Optional[BaseFunctionModule] = None

    def register_module(self, module: BaseFunctionModule):
        """注册功能模块"""
        if module.name in self.modules:
            raise ValueError(f"模块 '{module.name}' 已存在")
        self.modules[module.name] = module

    def activate_module(self, name: str) -> bool:
        """激活指定功能模块"""
        if name not in self.modules:
            return False

        if self.active_module and self.active_module.name != name:
            self.active_module.on_deactivate()

        self.active_module = self.modules[name]
        self.active_module.on_activate()
        return True

    def get_module_names(self) -> list[str]:
        """获取所有模块名称"""
        return list(self.modules.keys())

    def get_module(self, name: str) -> Optional[BaseFunctionModule]:
        """获取指定模块"""
        return self.modules.get(name)
