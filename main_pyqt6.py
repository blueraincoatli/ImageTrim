import sys
import os
import traceback

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def main():
    """主程序入口"""
    print("=" * 50)
    print("PyQt6图片处理工具套件启动日志")
    print("=" * 50)
    
    print("1. 开始导入PyQt6模块...")
    try:
        from PyQt6.QtWidgets import QApplication
        print("   成功导入QApplication")
    except Exception as e:
        print(f"   导入QApplication失败: {e}")
        traceback.print_exc()
        return

    try:
        from ui.pyqt6_main_window import PyQt6ModernApp
        print("   成功导入PyQt6ModernApp")
    except Exception as e:
        print(f"   导入PyQt6ModernApp失败: {e}")
        traceback.print_exc()
        return

    print("2. 开始创建PyQt6应用程序实例...")
    try:
        # 创建应用程序实例
        app = QApplication(sys.argv)
        print("   PyQt6应用程序实例创建成功")
    except Exception as e:
        print(f"   创建QApplication实例失败: {e}")
        traceback.print_exc()
        return

    print("3. 开始创建主窗口...")
    try:
        # 创建主窗口
        window = PyQt6ModernApp()
        print("   主窗口创建成功")
        print(f"   窗口标题: {window.windowTitle()}")
        print(f"   窗口大小: {window.size()}")
    except Exception as e:
        print(f"   创建主窗口失败: {e}")
        traceback.print_exc()
        return

    print("4. 开始显示窗口...")
    try:
        # 显示窗口
        window.show()
        print("   窗口显示成功")
        print(f"   窗口是否可见: {window.isVisible()}")
    except Exception as e:
        print(f"   显示窗口失败: {e}")
        traceback.print_exc()
        return

    print("5. 开始运行应用程序事件循环...")
    try:
        # 运行应用程序
        print("   即将进入事件循环...")
        exit_code = app.exec()
        print(f"   应用程序事件循环已退出，退出码: {exit_code}")
        return exit_code
    except Exception as e:
        print(f"   运行应用程序事件循环失败: {e}")
        traceback.print_exc()
        return

if __name__ == "__main__":
    exit_code = main()
    print("=" * 50)
    print(f"程序结束，退出码: {exit_code}")
    print("=" * 50)
    sys.exit(exit_code)