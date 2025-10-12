#!/usr/bin/env python3
"""
ImageTrim 环境检查工具
检查运行ImageTrim所需的Python环境和依赖
"""

import sys
import importlib
import subprocess
import os

def print_status(message, status):
    """打印状态信息"""
    status_icon = "OK" if status else "ERROR"
    print(f"[{status_icon}] {message}")

def check_python_version():
    """检查Python版本"""
    print("=== Python版本检查 ===")
    version = sys.version_info
    if version.major >= 3 and version.minor >= 8:
        print_status(f"Python {version.major}.{version.minor}.{version.micro}", True)
        return True
    else:
        print_status(f"Python {version.major}.{version.minor}.{version.micro} (需要3.8+)", False)
        return False

def check_module(module_name, package_name=None):
    """检查模块是否可用"""
    if package_name is None:
        package_name = module_name

    try:
        importlib.import_module(module_name)
        print_status(f"{package_name} 已安装", True)
        return True
    except ImportError:
        print_status(f"{package_name} 未安装", False)
        return False

def check_pip_package(package_name):
    """检查pip包是否安装"""
    try:
        result = subprocess.run([sys.executable, "-m", "pip", "show", package_name],
                              capture_output=True, text=True)
        if result.returncode == 0:
            print_status(f"{package_name} 已安装", True)
            return True
        else:
            print_status(f"{package_name} 未安装", False)
            return False
    except:
        print_status(f"{package_name} 检查失败", False)
        return False

def main():
    """主检查流程"""
    print("ImageTrim 环境检查工具")
    print("=" * 50)

    # 检查Python版本
    python_ok = check_python_version()

    # 检查必要的模块
    print("\n=== 核心依赖检查 ===")
    pyqt6_ok = check_module("PyQt6", "PyQt6")

    # 检查可选模块
    print("\n=== 可选依赖检查 ===")
    pil_ok = check_module("PIL", "Pillow")
    requests_ok = check_module("requests", "requests")

    print("\n=== 应用程序结构检查 ===")
    # 检查应用结构
    app_path = os.path.join(os.path.dirname(__file__), "app")
    if os.path.exists(app_path):
        print_status("app目录存在", True)

        # 检查关键文件
        main_file = os.path.join(app_path, "main.py")
        if os.path.exists(main_file):
            print_status("app/main.py存在", True)
        else:
            print_status("app/main.py不存在", False)

        # 检查核心模块
        core_path = os.path.join(app_path, "core")
        if os.path.exists(core_path):
            print_status("app/core目录存在", True)
        else:
            print_status("app/core目录不存在", False)

        modules_path = os.path.join(app_path, "modules")
        if os.path.exists(modules_path):
            print_status("app/modules目录存在", True)
        else:
            print_status("app/modules目录不存在", False)

    else:
        print_status("app目录不存在", False)

    # 总结
    print("\n" + "=" * 50)
    print("检查结果总结:")

    if python_ok and pyqt6_ok:
        print("[OK] 基本环境满足要求，可以运行ImageTrim")
        print("\n启动方法:")
        print("1. 双击 start.bat 文件")
        print("2. 在命令行运行: python -m app.main")
    else:
        print("[ERROR] 环境不满足要求，请先安装必要的依赖")

        if not python_ok:
            print("\n需要安装 Python 3.8 或更高版本")
            print("下载地址: https://python.org/downloads/")

        if not pyqt6_ok:
            print("\n需要安装 PyQt6:")
            print("pip install PyQt6")

        if not pil_ok:
            print("\n建议安装 Pillow (用于图片处理):")
            print("pip install Pillow")

        if not requests_ok:
            print("\n建议安装 requests (用于网络请求):")
            print("pip install requests")

    print("\n按回车键退出...")
    try:
        input()
    except:
        pass

if __name__ == "__main__":
    main()