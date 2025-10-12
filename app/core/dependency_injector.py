#!/usr/bin/env python3
"""
依赖注入器
"""

from typing import Dict, Type, Any


class DependencyInjector:
    """
    依赖注入器
    """

    def __init__(self):
        self._services: Dict[str, Any] = {}
        self._singletons: Dict[str, Any] = {}

    def register(self, name: str, service: Any, singleton: bool = False):
        """
        注册服务

        Args:
            name: 服务名称
            service: 服务实例或类
            singleton: 是否为单例
        """
        if singleton:
            self._singletons[name] = service
        else:
            self._services[name] = service

    def get(self, name: str) -> Any:
        """
        获取服务

        Args:
            name: 服务名称

        Returns:
            Any: 服务实例
        """
        if name in self._singletons:
            if isinstance(self._singletons[name], type):
                self._singletons[name] = self._singletons[name]()
            return self._singletons[name]
        elif name in self._services:
            service = self._services[name]
            if isinstance(service, type):
                return service()
            return service
        else:
            raise KeyError(f"Service '{name}' not found")

    def inject(self, cls: Type) -> Any:
        """
        注入依赖并创建实例

        Args:
            cls: 类

        Returns:
            Any: 实例
        """
        # 这里可以实现更复杂的依赖注入逻辑
        return cls()