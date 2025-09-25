import tkinter
print("tkinter imported successfully")

try:
    import ttkbootstrap
    print("ttkbootstrap imported successfully")
except ImportError as e:
    print(f"ttkbootstrap import failed: {e}")

try:
    from PIL import Image
    print("PIL imported successfully")
except ImportError as e:
    print(f"PIL import failed: {e}")

try:
    import importlib.util
    print("importlib.util imported successfully")
except ImportError as e:
    print(f"importlib.util import failed: {e}")