#!/usr/bin/env python3
"""
简化的跨平台打包脚本
"""

import os
import sys
import platform
import subprocess
from pathlib import Path

# 项目配置
PROJECT_NAME = "ImageTrim"
MAIN_SCRIPT = "app/main.py"
VERSION = "1.0.0"

def get_platform_config():
    """获取平台配置"""
    current_platform = platform.system().lower()

    if current_platform == "windows":
        return {
            "name": f"{PROJECT_NAME}.exe",
            "icon": "app/resources/icons/imagetrim.ico",
            "add_data": "app/resources;resources"
        }
    elif current_platform == "darwin":  # macOS
        return {
            "name": PROJECT_NAME,
            "icon": "app/resources/icons/imagetrim.icns",
            "add_data": "app/resources:resources",
            "bundle_id": "com.imagetrim.imagetrim"
        }
    elif current_platform == "linux":
        return {
            "name": PROJECT_NAME.lower(),
            "icon": "app/resources/icons/imagetrim.png",
            "add_data": "app/resources:resources"
        }
    else:
        raise ValueError(f"不支持的平台: {current_platform}")

def build_app():
    """构建应用"""
    config = get_platform_config()
    current_platform = platform.system().lower()

    print(f"🚀 开始为 {current_platform.upper()} 构建应用程序...")

    # 构建 PyInstaller 命令
    cmd = [
        "pyinstaller",
        "--onefile",
        "--windowed",
        "--name", config["name"],
        "--add-data", config["add_data"],
        "--hidden-import", "PyQt6.QtCore",
        "--hidden-import", "PyQt6.QtGui",
        "--hidden-import", "PyQt6.QtWidgets",
        "--collect-all", "PIL",
        "--exclude-module", "tkinter",
        "--exclude-module", "matplotlib",
        "--exclude-module", "numpy.testing",
        "--exclude-module", "scipy.tests",
        MAIN_SCRIPT
    ]

    # 添加图标（如果存在）
    if config["icon"] and os.path.exists(config["icon"]):
        cmd.extend(["--icon", config["icon"]])
        print(f"✅ 使用图标: {config['icon']}")
    else:
        print(f"⚠️  图标文件不存在: {config['icon']}")

    # macOS 特定配置
    if current_platform == "darwin" and "bundle_id" in config:
        cmd.extend(["--osx-bundle-identifier", config["bundle_id"]])

    print(f"📦 执行命令: {' '.join(cmd)}")

    try:
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        print("✅ 构建成功!")

        # 显示输出文件
        dist_dir = Path("dist")
        if dist_dir.exists():
            output_files = list(dist_dir.glob("*"))
            print(f"📁 输出文件:")
            for file_path in output_files:
                size_mb = file_path.stat().st_size / (1024 * 1024)
                print(f"   - {file_path.name} ({size_mb:.1f} MB)")

    except subprocess.CalledProcessError as e:
        print(f"❌ 构建失败: {e}")
        if e.stderr:
            print(f"错误输出: {e.stderr}")
        sys.exit(1)

def main():
    print(f"🔧 {PROJECT_NAME} 简化构建工具 v{VERSION}")
    print(f"🖥️  当前平台: {platform.system()}")
    print("=" * 50)

    # 检查主脚本是否存在
    if not os.path.exists(MAIN_SCRIPT):
        print(f"❌ 错误: 找不到主脚本 {MAIN_SCRIPT}")
        sys.exit(1)

    # 构建应用
    build_app()

    print("=" * 50)
    print("🎉 构建完成!")
    print(f"📁 输出目录: dist/")

if __name__ == "__main__":
    main()