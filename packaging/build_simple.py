#!/usr/bin/env python3
"""
ImageTrim Windows 打包构建脚本（简化版）
"""

import os
import sys
import subprocess
import shutil
import platform
from pathlib import Path


def main():
    """主构建函数"""
    root_dir = Path(__file__).parent.parent

    print("=== ImageTrim Windows 打包脚本 ===")

    # 清理构建目录
    print("清理构建目录...")
    build_dir = root_dir / "build"
    dist_dir = root_dir / "dist"

    if build_dir.exists():
        shutil.rmtree(build_dir)
    if dist_dir.exists():
        shutil.rmtree(dist_dir)

    # 创建简单的PyInstaller命令
    print("开始构建可执行文件...")

    cmd = [
        "pyinstaller",
        "--name=ImageTrim",
        "--windowed",
        "--onefile",
        "--icon=app/resources/icons/imageTrim256px.ico",
        "--add-data=app/resources;resources",
        "--hidden-import=PyQt6.QtCore",
        "--hidden-import=PyQt6.QtGui",
        "--hidden-import=PyQt6.QtWidgets",
        "--hidden-import=numpy",
        "--hidden-import=scipy",
        "--hidden-import=PyWavelets",
        "--hidden-import=imagehash",
        "--hidden-import=PIL",
        "--hidden-import=requests",
        "--clean",
        "--noconfirm",
        "app/main.py"
    ]

    try:
        result = subprocess.run(cmd, check=True, cwd=root_dir, capture_output=True, text=True)
        print("构建成功完成！")
        print("输出文件位置:", dist_dir / "ImageTrim.exe")

        # 创建便携版
        create_portable_version(dist_dir)

    except subprocess.CalledProcessError as e:
        print("构建失败:")
        print("错误输出:", e.stderr)
        return 1

    print("\n=== 构建完成 ===")
    print("请检查 dist 目录中的文件")

    return 0


def create_portable_version(dist_dir):
    """创建便携版本"""
    print("创建便携版...")

    portable_dir = dist_dir.parent / "build" / "portable"
    portable_dir.mkdir(parents=True, exist_ok=True)

    # 复制可执行文件
    exe_file = dist_dir / "ImageTrim.exe"
    if exe_file.exists():
        shutil.copy2(exe_file, portable_dir)

    # 创建说明文件
    readme_content = """ImageTrim 1.0.0 便携版

现代化的图片去重和格式转换工具

使用方法：
1. 双击 ImageTrim.exe 启动程序
2. 无需安装，即用即走

功能特点：
- 智能图片去重
- 批量格式转换
- 现代化界面
- 多线程处理

版本：1.0.0
发布日期：2025-10-12
"""

    with open(portable_dir / "README.txt", "w", encoding="utf-8") as f:
        f.write(readme_content)

    # 创建zip文件
    import zipfile
    zip_path = dist_dir / "ImageTrim-1.0.0-windows-portable.zip"

    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for file_path in portable_dir.rglob("*"):
            if file_path.is_file():
                arcname = file_path.relative_to(portable_dir)
                zipf.write(file_path, arcname)

    print(f"便携版已创建: {zip_path}")


if __name__ == "__main__":
    sys.exit(main())