#!/usr/bin/env python3
"""
配置管理器
"""

import json
import os
from typing import Dict, Any


class ConfigManager:
    """
    配置管理器
    """

    def __init__(self, config_file: str = "config.json"):
        self.config_file = config_file
        self.config: Dict[str, Any] = self._load_config()

    def _load_config(self) -> Dict[str, Any]:
        """
        加载配置

        Returns:
            Dict[str, Any]: 配置字典
        """
        if os.path.exists(self.config_file):
            with open(self.config_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return self._get_default_config()

    def _get_default_config(self) -> Dict[str, Any]:
        """
        获取默认配置

        Returns:
            Dict[str, Any]: 默认配置
        """
        return {
            "theme": "dark",
            "language": "zh_CN",
            "thumbnail_size": 80,
            "scan_subdirs": True,
            "similarity_threshold": 95
        }

    def get(self, key: str, default=None) -> Any:
        """
        获取配置值

        Args:
            key: 配置键
            default: 默认值

        Returns:
            Any: 配置值
        """
        return self.config.get(key, default)

    def set(self, key: str, value: Any):
        """
        设置配置值

        Args:
            key: 配置键
            value: 配置值
        """
        self.config[key] = value
        self._save_config()

    def _save_config(self):
        """保存配置"""
        with open(self.config_file, 'w', encoding='utf-8') as f:
            json.dump(self.config, f, ensure_ascii=False, indent=2)