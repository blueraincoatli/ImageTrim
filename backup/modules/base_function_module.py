"""
PyQt6功能模块基类
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from PyQt6.QtWidgets import QWidget
from PyQt6.QtCore import QObject, pyqtSignal


class BaseFunctionModule(QObject):
    """
    PyQt6功能模块基类
    - 定义所有功能模块必须实现的接口
    - 使用PyQt6信号槽机制进行通信
    """
    
    # 信号定义
    progress_updated = pyqtSignal(float, str)  # 进度更新 (百分比, 消息)
    log_message = pyqtSignal(str, str)         # 日志消息 (消息, 级别)
    execution_finished = pyqtSignal(dict)      # 执行完成 (结果数据)
    
    def __init__(self, name: str, display_name: str, description: str = "", icon: str = "❓"):
        super().__init__()
        self.name = name
        self.display_name = display_name
        self.description = description
        self.icon = icon
        self.is_active = False
        self.is_running = False

    @abstractmethod
    def create_settings_ui(self) -> Optional[QWidget]:
        """
        创建并返回功能对应的"设置"UI面板 (中栏)
        """
        pass

    @abstractmethod
    def create_workspace_ui(self) -> Optional[QWidget]:
        """
        创建并返回功能对应的"工作区"UI面板 (右栏)
        """
        pass

    @abstractmethod
    def execute(self, params: Dict[str, Any]):
        """
        执行功能的核心逻辑
        应在后台线程中执行，通过信号与主线程通信
        """
        pass

    @abstractmethod
    def stop_execution(self):
        """
        停止正在执行的操作
        """
        pass

    def on_activate(self):
        """当功能模块被激活时调用"""
        self.is_active = True
        self.log_message.emit(f"模块 '{self.display_name}' 已激活", "info")

    def on_deactivate(self):
        """当功能模块被停用时调用"""
        self.is_active = False