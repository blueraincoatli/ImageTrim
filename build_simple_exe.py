#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简单的打包脚本 - 生成单个exe文件用于测试
"""

import os
import sys
import subprocess

def build_simple_exe():
    """构建单个exe文件"""

    # 创建主入口文件
    main_py = '''#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
现代图片处理工具套件 - 主入口点
"""

import sys
import os

def main():
    # 添加项目根目录到路径
    project_root = os.path.dirname(os.path.abspath(__file__))
    sys.path.insert(0, project_root)

    try:
        # 尝试导入现代UI框架
        from modern_ui_framework import main as modern_main
        modern_main()
    except ImportError as e:
        print(f"无法导入现代UI框架: {e}")
        print("请确保modern_ui_framework.py文件存在")
        input("按回车键退出...")
        sys.exit(1)

if __name__ == "__main__":
    main()
'''

    # 写入主文件
    with open("main_entry.py", "w", encoding="utf-8") as f:
        f.write(main_py)

    # 检查主文件是否存在
    if not os.path.exists("modern_ui_framework.py"):
        print("错误: 找不到modern_ui_framework.py")
        return

    # 构建PyInstaller命令
    cmd = [
        sys.executable,
        "-m",
        "PyInstaller",
        "--onefile",
        "--windowed",
        "--name=ModernImageTools",
        "--clean",
        "main_entry.py"
    ]

    print("开始打包现代图片处理工具...")
    print(f"命令: {' '.join(cmd)}")

    # 运行打包命令
    try:
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        print("打包成功！")
        print("输出:")
        print(result.stdout)

        # 检查输出文件
        exe_path = os.path.join("dist", "ModernImageTools.exe")
        if os.path.exists(exe_path):
            file_size = os.path.getsize(exe_path)
            print(f"\\n可执行文件已生成: {exe_path}")
            print(f"文件大小: {file_size / (1024*1024):.1f} MB")

            # 清理临时文件
            if os.path.exists("main_entry.py"):
                os.remove("main_entry.py")

            print("\\n打包完成！你可以运行dist/ModernImageTools.exe进行测试")
        else:
            print("警告: 未找到生成的可执行文件")

    except subprocess.CalledProcessError as e:
        print("打包失败！")
        print("错误信息:")
        print(e.stderr)
    except Exception as e:
        print(f"发生错误: {str(e)}")

if __name__ == "__main__":
    build_simple_exe()