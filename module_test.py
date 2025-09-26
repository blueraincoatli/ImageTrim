import sys
import os
import traceback

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

print("开始测试模块导入...")

try:
    print("1. 测试导入 PyQt6.QtWidgets...")
    from PyQt6.QtWidgets import QApplication
    print("   成功导入 QApplication")
except Exception as e:
    print(f"   导入 QApplication 失败: {e}")
    traceback.print_exc()

try:
    print("2. 测试导入 PyQt6BaseFunctionModule...")
    from modules.pyqt6_base_module import PyQt6BaseFunctionModule
    print("   成功导入 PyQt6BaseFunctionModule")
except Exception as e:
    print(f"   导入 PyQt6BaseFunctionModule 失败: {e}")
    traceback.print_exc()

try:
    print("3. 测试导入 PyQt6FunctionManager...")
    from modules.pyqt6_base_module import PyQt6FunctionManager
    print("   成功导入 PyQt6FunctionManager")
except Exception as e:
    print(f"   导入 PyQt6FunctionManager 失败: {e}")
    traceback.print_exc()

try:
    print("4. 测试导入 PyQt6DeduplicationModule...")
    from modules.pyqt6_deduplication_module import PyQt6DeduplicationModule
    print("   成功导入 PyQt6DeduplicationModule")
except Exception as e:
    print(f"   导入 PyQt6DeduplicationModule 失败: {e}")
    traceback.print_exc()

try:
    print("5. 测试导入 PyQt6AVIFConverterModule...")
    from modules.pyqt6_avif_converter_module import PyQt6AVIFConverterModule
    print("   成功导入 PyQt6AVIFConverterModule")
except Exception as e:
    print(f"   导入 PyQt6AVIFConverterModule 失败: {e}")
    traceback.print_exc()

try:
    print("6. 测试导入 PyQt6ModernApp...")
    from ui.pyqt6_main_window import PyQt6ModernApp
    print("   成功导入 PyQt6ModernApp")
except Exception as e:
    print(f"   导入 PyQt6ModernApp 失败: {e}")
    traceback.print_exc()

print("模块导入测试完成")