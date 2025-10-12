#!/usr/bin/env python3
"""
功能管理器
负责功能模块的注册、激活和管理
"""

from typing import Dict, Optional, List
from PyQt6.QtCore import QObject, pyqtSignal
from .base_module import BaseFunctionModule


class FunctionManager(QObject):
    """
    功能管理器
    负责功能模块的注册、激活和管理
    """
    
    # 模块激活信号
    module_activated = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.modules: Dict[str, BaseFunctionModule] = {}
        self.active_module: Optional[BaseFunctionModule] = None

    def register_module(self, module: BaseFunctionModule) -> bool:
        """
        注册功能模块

        Args:
            module: 功能模块实例

        Returns:
            bool: 注册是否成功
        """
        if module.name in self.modules:
            return False
        self.modules[module.name] = module
        return True

    def unregister_module(self, name: str) -> bool:
        """
        注销功能模块

        Args:
            name: 模块名称

        Returns:
            bool: 注销是否成功
        """
        if name in self.modules:
            del self.modules[name]
            return True
        return False

    def activate_module(self, name: str) -> bool:
        """
        激活指定功能模块

        Args:
            name: 模块名称

        Returns:
            bool: 激活是否成功
        """
        if name not in self.modules:
            return False

        if self.active_module and self.active_module.name != name:
            self.active_module.on_deactivate()

        self.active_module = self.modules[name]
        self.active_module.on_activate()
        self.module_activated.emit(name)
        return True

    def deactivate_module(self) -> bool:
        """
        停用当前激活的模块

        Returns:
            bool: 停用是否成功
        """
        if self.active_module:
            self.active_module.on_deactivate()
            self.active_module = None
            return True
        return False

    def get_module_names(self) -> List[str]:
        """
        获取所有模块名称

        Returns:
            List[str]: 模块名称列表
        """
        return list(self.modules.keys())

    def get_module(self, name: str) -> Optional[BaseFunctionModule]:
        """
        获取指定模块

        Args:
            name: 模块名称

        Returns:
            BaseFunctionModule: 模块实例，如果不存在则返回None
        """
        return self.modules.get(name)

    def get_active_module(self) -> Optional[BaseFunctionModule]:
        """
        获取当前激活的模块

        Returns:
            BaseFunctionModule: 当前激活的模块，如果没有则返回None
        """
        return self.active_module