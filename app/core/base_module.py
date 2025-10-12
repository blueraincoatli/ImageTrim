#!/usr/bin/env python3
"""
功能模块基类
定义了所有功能模块必须实现的接口
"""

from PyQt6.QtCore import QObject, pyqtSignal
from typing import Optional, Dict, Any
from PyQt6.QtWidgets import QWidget


class BaseFunctionModule(QObject):
    """
    功能模块基类
    继承自QObject以支持信号
    """

    # 定义信号
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

    def create_settings_ui(self) -> Optional[QWidget]:
        """
        创建并返回功能对应的"设置"UI面板

        Returns:
            QWidget: 设置UI面板，如果不需要则返回None
        """
        raise NotImplementedError("子类必须实现 create_settings_ui 方法")

    def create_workspace_ui(self) -> Optional[QWidget]:
        """
        创建并返回功能对应的"工作区"UI面板

        Returns:
            QWidget: 工作区UI面板，如果不需要则返回None
        """
        raise NotImplementedError("子类必须实现 create_workspace_ui 方法")

    def execute(self, params: Dict[str, Any]):
        """
        执行功能的核心逻辑

        Args:
            params: 执行参数
        """
        raise NotImplementedError("子类必须实现 execute 方法")

    def stop_execution(self):
        """
        停止正在执行的操作
        """
        raise NotImplementedError("子类必须实现 stop_execution 方法")

    def on_activate(self):
        """功能被激活时的回调"""
        self.is_active = True
        self.log_message.emit(f"模块 '{self.display_name}' 已激活", "info")

    def on_deactivate(self):
        """功能被停用时的回调"""
        self.is_active = False