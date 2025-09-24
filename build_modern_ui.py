#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
现代化图片处理工具打包脚本
使用PyInstaller打包为可执行文件
"""

import os
import sys
import subprocess
import shutil

def setup_environment():
    """设置环境变量和路径"""
    # 使用cleanPython
    clean_python_path = "D:/cleanPython/python.exe"
    pip_path = "D:/cleanPython/Scripts/pip.exe"
    
    return clean_python_path, pip_path

def install_dependencies():
    """安装依赖包"""
    clean_python, pip = setup_environment()
    
    print("[安装] 安装依赖包...")
    
    # 基础依赖
    dependencies = [
        "pillow",
        "pillow-avif-plugin",
        "numpy",
        "ttkbootstrap",
        "pyinstaller"
    ]
    
    for dep in dependencies:
        print(f"[安装] 正在安装 {dep}...")
        try:
            result = subprocess.run([pip, "install", dep], 
                                  capture_output=True, text=True, check=True)
            print(f"[成功] {dep} 安装成功")
        except subprocess.CalledProcessError as e:
            print(f"[警告] {dep} 安装失败: {e}")
            continue
    
    print("[完成] 依赖包安装完成")

def build_executable():
    """打包可执行文件"""
    clean_python, _ = setup_environment()
    
    print("[打包] 开始打包可执行文件...")
    
    # PyInstaller命令
    cmd = [
        clean_python,
        "-m",
        "PyInstaller",
        "--name=ModernImageTools",
        "--windowed",  # 无控制台窗口
        "--onefile",   # 打包为单个文件
        "--icon=NONE",  # 无图标
        "--clean",     # 清理临时文件
        "--noconfirm", # 不确认
        "modern_ui_framework.py"
    ]
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        print("[成功] 打包成功！")
        print(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print(f"[失败] 打包失败: {e}")
        print(f"[错误] {e.stderr}")
        return False

def post_build():
    """打包后处理"""
    print("[清理] 清理临时文件...")
    
    # 清理build目录
    if os.path.exists("build"):
        try:
            shutil.rmtree("build")
            print("[成功] 清理build目录")
        except Exception as e:
            print(f"[警告] 清理build目录失败: {e}")
    
    # 清理spec文件
    spec_files = [f for f in os.listdir(".") if f.endswith(".spec")]
    for spec_file in spec_files:
        try:
            os.remove(spec_file)
            print(f"[成功] 删除spec文件: {spec_file}")
        except Exception as e:
            print(f"[警告] 删除spec文件失败: {e}")

def main():
    """主函数"""
    print("=" * 50)
    print("[开始] 现代化图片处理工具打包")
    print("=" * 50)
    
    # 检查当前目录
    current_dir = os.getcwd()
    print(f"[信息] 当前目录: {current_dir}")
    
    # 检查必要文件
    required_files = ["modern_ui_framework.py", "function_modules.py"]
    for file in required_files:
        if not os.path.exists(file):
            print(f"[错误] 缺少必要文件: {file}")
            return False
    
    print("[成功] 所有必要文件存在")
    
    # 安装依赖
    install_dependencies()
    
    # 打包
    if build_executable():
        # 打包后处理
        post_build()
        
        # 检查输出文件
        output_file = "dist/ModernImageTools.exe"
        if os.path.exists(output_file):
            file_size = os.path.getsize(output_file)
            print(f"[成功] 打包完成！")
            print(f"[信息] 输出文件: {output_file}")
            print(f"[信息] 文件大小: {file_size / (1024*1024):.2f} MB")
            return True
        else:
            print(f"[错误] 输出文件不存在: {output_file}")
            return False
    else:
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)