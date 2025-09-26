"""
现代化图片处理工具套件主程序入口
"""

import sys
import os

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from ui.main_window import ImprovedModernApp
import ttkbootstrap as ttkb

def main():
    """主程序入口"""
    # 创建主窗口
    root = ttkb.Window(themename="darkly")
    app = ImprovedModernApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()