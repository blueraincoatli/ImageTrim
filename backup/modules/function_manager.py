"""
PyQt6功能管理器
"""

from typing import Dict, Optional, List
from PyQt6.QtCore import QObject, pyqtSignal
from modules.base_function_module import BaseFunctionModule


class FunctionManager(QObject):
    """PyQt6功能管理器"""
    
    # 信号定义
    module_activated = pyqtSignal(str)  # 模块激活信号 (模块名称)
    
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

        # 先停用当前模块
        if self.active_module and self.active_module.name != name:
            self.active_module.on_deactivate()

        # 激活新模块
        self.active_module = self.modules[name]
        self.active_module.on_activate()
        self.module_activated.emit(name)
        return True

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
            Optional[BaseFunctionModule]: 模块实例或None
        """
        return self.modules.get(name)