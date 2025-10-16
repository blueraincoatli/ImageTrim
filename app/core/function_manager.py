#!/usr/bin/env python3
"""
功能管理器
负责功能模块的注册、激活和管理
"""

from typing import Dict, Optional, List, Callable
from PyQt6.QtCore import QObject, pyqtSignal
from .base_module import BaseFunctionModule


class ModuleInfo:
    """模块信息类，用于懒加载时存储模块元数据"""
    def __init__(self, name: str, display_name: str, icon: str = "", description: str = ""):
        self.name = name
        self.display_name = display_name
        self.icon = icon
        self.description = description


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
        self.module_constructors: Dict[str, Callable[[], BaseFunctionModule]] = {}
        self.module_infos: Dict[str, ModuleInfo] = {}
        self.active_module: Optional[BaseFunctionModule] = None
        self._module_order: List[str] = []

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
        if module.name not in self._module_order:
            self._module_order.append(module.name)
        return True

    def register_module_constructor(self, name: str, constructor: Callable[[], BaseFunctionModule], display_name: str = None) -> bool:
        """
        注册功能模块构造函数（用于懒加载）

        Args:
            name: 模块名称
            constructor: 模块构造函数
            display_name: 显示名称

        Returns:
            bool: 注册是否成功
        """
        if name in self.module_constructors:
            return False
        
        # 临时创建模块实例以获取元数据，但不保存实例
        temp_module = constructor()
        if display_name:
            display_name_to_use = display_name
        else:
            display_name_to_use = temp_module.display_name
            
        # 存储模块信息
        self.module_infos[name] = ModuleInfo(
            name=temp_module.name,
            display_name=display_name_to_use,
            icon=getattr(temp_module, 'icon', ''),
            description=getattr(temp_module, 'description', '')
        )
        
        # 保存构造函数
        self.module_constructors[name] = constructor
        if name not in self._module_order:
            self._module_order.append(name)
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
            if name in self._module_order:
                self._module_order.remove(name)
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
        # 如果模块尚未加载，但有构造函数，则创建实例
        if name not in self.modules and name in self.module_constructors:
            # 使用构造函数创建模块实例
            constructor = self.module_constructors[name]
            module = constructor()
            self.modules[name] = module

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
        获取所有模块名称（包括已加载的和懒加载的）

        Returns:
            List[str]: 模块名称列表
        """
        all_names = set(self.modules.keys())
        all_names.update(self.module_constructors.keys())
        ordered = []
        for name in self._module_order:
            if name in all_names:
                ordered.append(name)
        for name in all_names:
            if name not in ordered:
                ordered.append(name)
        return ordered

    def get_module(self, name: str) -> Optional[BaseFunctionModule]:
        """
        获取指定模块

        Args:
            name: 模块名称

        Returns:
            BaseFunctionModule: 模块实例，如果不存在则返回None
        """
        # 如果模块尚未加载但有构造函数，则先加载模块
        if name not in self.modules and name in self.module_constructors:
            constructor = self.module_constructors[name]
            module = constructor()
            self.modules[name] = module
        
        return self.modules.get(name)
    
    def get_module_display_info(self, name: str) -> Optional[Dict[str, str]]:
        """
        获取模块显示信息（不加载完整模块）

        Args:
            name: 模块名称

        Returns:
            Dict: 包含display_name等显示信息的字典
        """
        # 如果模块已加载，从实例获取信息
        if name in self.modules:
            module = self.modules[name]
            return {
                'name': module.name,
                'display_name': module.display_name,
                'icon': getattr(module, 'icon', ''),
                'description': getattr(module, 'description', '')
            }
        
        # 如果有模块信息（懒加载注册时保存的），从那里获取
        if name in self.module_infos:
            info = self.module_infos[name]
            return {
                'name': info.name,
                'display_name': info.display_name,
                'icon': info.icon,
                'description': info.description
            }
        
        return None

    def get_active_module(self) -> Optional[BaseFunctionModule]:
        """
        获取当前激活的模块

        Returns:
            BaseFunctionModule: 当前激活的模块，如果没有则返回None
        """
        return self.active_module
