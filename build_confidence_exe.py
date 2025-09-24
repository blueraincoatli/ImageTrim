#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
打包置信度版图片去重工具
"""

import os
import sys
import subprocess

def main():
    # 设置路径
    script_path = "E:\\FFOutput\\ImageDedupUI_Confidence.py"
    python_path = "D:\\CleanPython\\python.exe"
    
    # 检查文件是否存在
    if not os.path.exists(script_path):
        print(f"错误: 找不到脚本文件 {script_path}")
        return
    
    # 构建PyInstaller命令
    cmd = [
        python_path,
        "-m",
        "PyInstaller",
        "--onefile",
        "--windowed",
        "--name=ImageDedup_Confidence",
        "--icon=NONE",
        script_path
    ]
    
    print("开始打包置信度版图片去重工具...")
    print(f"命令: {' '.join(cmd)}")
    
    # 运行打包命令
    try:
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        print("打包成功！")
        print("输出:")
        print(result.stdout)
        
        # 检查输出文件
        exe_path = "E:\\FFOutput\\dist\\ImageDedup_Confidence.exe"
        if os.path.exists(exe_path):
            print(f"\n可执行文件已生成: {exe_path}")
            file_size = os.path.getsize(exe_path)
            print(f"文件大小: {file_size / (1024*1024):.1f} MB")
        else:
            print("警告: 未找到生成的可执行文件")
            
    except subprocess.CalledProcessError as e:
        print("打包失败！")
        print("错误信息:")
        print(e.stderr)
    except Exception as e:
        print(f"发生错误: {str(e)}")

if __name__ == "__main__":
    main()