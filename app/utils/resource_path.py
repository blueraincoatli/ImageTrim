#!/usr/bin/env python3
"""
资源路径工具 - 支持开发环境、PyInstaller 和 Nuitka
"""

import os
import sys
from pathlib import Path


def get_resource_path(relative_path: str) -> str | None:
    """
    获取资源文件的绝对路径
    
    支持三种环境:
    1. 开发环境 - 从 app/resources 加载
    2. PyInstaller - 从 _MEIPASS/resources 加载
    3. Nuitka - 从可执行文件目录/resources 加载
    
    Args:
        relative_path: 相对于 resources 目录的路径，例如 "icons/imagetrim.ico"
    
    Returns:
        str | None: 资源文件的绝对路径，如果不存在返回 None
    """
    
    # 检测打包环境
    is_frozen = getattr(sys, 'frozen', False)
    
    if is_frozen:
        # 打包环境
        if hasattr(sys, '_MEIPASS'):
            # PyInstaller 环境
            base_path = sys._MEIPASS
            possible_paths = [
                os.path.join(base_path, "resources", relative_path),
                os.path.join(base_path, relative_path),
            ]
        else:
            # Nuitka 环境 - 资源文件在可执行文件旁边
            if hasattr(sys, 'argv') and sys.argv:
                exe_dir = os.path.dirname(os.path.abspath(sys.argv[0]))
            else:
                exe_dir = os.path.dirname(os.path.abspath(sys.executable))
            
            possible_paths = [
                os.path.join(exe_dir, "resources", relative_path),
                os.path.join(exe_dir, relative_path),
            ]
    else:
        # 开发环境
        # 尝试从当前文件位置向上查找
        current_file = Path(__file__).resolve()
        project_root = current_file.parent.parent.parent  # app/utils/resource_path.py -> project_root
        
        possible_paths = [
            os.path.join(project_root, "app", "resources", relative_path),
            os.path.join(project_root, "resources", relative_path),
            os.path.join("app", "resources", relative_path),
            os.path.join("resources", relative_path),
            os.path.join(".", "app", "resources", relative_path),
            os.path.join(".", "resources", relative_path),
        ]
    
    # 查找第一个存在的路径
    for path in possible_paths:
        if os.path.exists(path):
            return os.path.abspath(path)
    
    # 如果都不存在，打印调试信息
    print(f"[WARNING] 资源文件未找到: {relative_path}")
    print(f"[DEBUG] 尝试的路径:")
    for path in possible_paths:
        print(f"  - {path} (存在: {os.path.exists(path)})")
    
    return None


def get_resource_dir() -> str:
    """
    获取资源目录的绝对路径
    
    Returns:
        str: 资源目录的绝对路径
    """
    is_frozen = getattr(sys, 'frozen', False)
    
    if is_frozen:
        if hasattr(sys, '_MEIPASS'):
            # PyInstaller
            return os.path.join(sys._MEIPASS, "resources")
        else:
            # Nuitka
            if hasattr(sys, 'argv') and sys.argv:
                exe_dir = os.path.dirname(os.path.abspath(sys.argv[0]))
            else:
                exe_dir = os.path.dirname(os.path.abspath(sys.executable))
            return os.path.join(exe_dir, "resources")
    else:
        # 开发环境
        current_file = Path(__file__).resolve()
        project_root = current_file.parent.parent.parent
        return os.path.join(project_root, "app", "resources")

