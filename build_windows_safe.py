#!/usr/bin/env python3
"""
Windows安全构建脚本 - 避免DLL加载问题
"""

import os
import sys
import platform
import subprocess
from pathlib import Path

def check_requirements():
    """检查必要的依赖"""
    print("检查构建依赖...")

    try:
        import PyInstaller
        print(f"PyInstaller 已安装: {PyInstaller.__version__}")
    except ImportError:
        print("安装PyInstaller...")
        subprocess.run([sys.executable, "-m", "pip", "install", "pyinstaller"], check=True)
        print("PyInstaller 安装完成")

def get_windows_config():
    """获取Windows特定的配置"""
    return {
        "name": "ImageTrim.exe",
        "icon": "app/resources/icons/imagetrim.ico" if os.path.exists("app/resources/icons/imagetrim.ico") else None,
        "add_data": "app/resources;resources",
        "hiddenimports": [
            "PyQt6.QtCore",
            "PyQt6.QtGui",
            "PyQt6.QtWidgets",
            # 确保包含必要的PyQt6模块
            "PyQt6.QtCore.QCoreApplication",
            "PyQt6.QtGui.QGuiApplication",
            "PyQt6.QtWidgets.QApplication",
            "PyQt6.QtCore.Qt",
            "PyQt6.QtCore.QObject",
            "PyQt6.QtCore.QTimer",
            "PIL.Image",
            "PIL.ImageQt",
            "PIL.ImageFilter",
            "PIL.ImageEnhance",
            "PIL.ImageOps",
            "imagehash",
            "numpy.core._multiarray_umath",
            "numpy.linalg.lapack_lite",
            "requests",
            "urllib3",
            "certifi",
            "charset_normalizer",
            "idna",
        ],
        "excludes": [
            # 排除大型依赖
            'matplotlib', 'mpl_toolkits', 'pylab',
            'scipy', 'pandas', 'IPython', 'jupyter',
            'numpy.testing', 'numpy.f2py', 'numpy.distutils',
            'PyQt6.QtWebEngine', 'PyQt6.QtMultimedia',
            'PyQt6.QtOpenGL', 'PyQt6.QtNetwork',
            'tkinter', 'test', 'tests', 'unittest', 'pytest',
            'setuptools', 'wheel', 'pip', 'debugpy',
            'sphinx', 'docutils', 'nose', 'coverage',
            'PyQt6.QtTest', 'PyQt6.QtDesigner', 'PyQt6.QtHelp',
            'PyQt6.QtSql', 'PyQt6.QtXml', 'PyQt6.QtSvg',
        ]
    }

def build_safe_windows():
    """安全构建Windows版本"""
    if platform.system() != "Windows":
        print("此脚本仅适用于Windows平台")
        return False

    print("开始Windows安全构建...")
    config = get_windows_config()

    # 构建PyInstaller命令
    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--onefile",
        "--windowed",
        "--name", config["name"],
        "--add-data", config["add_data"],
        "--hidden-import", "--".join(config["hiddenimports"]),
        "--exclude-module", "--".join(config["excludes"]),
        "app/main.py"
    ]

    # 添加图标（如果存在）
    if config["icon"]:
        cmd.extend(["--icon", config["icon"]])

    # 添加额外的安全参数
    cmd.extend([
        "--noupx",  # 不使用UPX压缩
        "--clean",  # 清理之前的构建
        "--noconfirm",  # 不询问确认
    ])

    print(f"执行命令: {' '.join(cmd)}")

    try:
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        print("Windows构建成功!")

        # 显示构建结果
        show_build_results()
        return True

    except subprocess.CalledProcessError as e:
        print(f"Windows构建失败: {e}")
        if e.stderr:
            print(f"错误输出: {e.stderr}")
        return False

def show_build_results():
    """显示构建结果"""
    dist_dir = Path("dist")
    if not dist_dir.exists():
        print("没有找到dist目录")
        return

    print("\n构建结果:")
    total_size = 0

    for item in dist_dir.iterdir():
        if item.is_file():
            size_mb = item.stat().st_size / (1024 * 1024)
            total_size += size_mb
            print(f"   FILE {item.name} ({size_mb:.1f} MB)")

    print(f"\n总大小: {total_size:.1f} MB")

def main():
    print("ImageTrim Windows安全构建工具")
    print(f"平台: {platform.system()}")
    print("=" * 50)

    # 检查要求
    check_requirements()

    # 构建应用
    if build_safe_windows():
        print("\nWindows安全构建完成!")
        print("输出目录: dist/")
    else:
        print("Windows构建失败!")
        sys.exit(1)

if __name__ == "__main__":
    main()