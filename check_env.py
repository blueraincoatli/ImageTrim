import sys
print("Python executable:", sys.executable)
print("Python version:", sys.version)

try:
    import tkinter
    print("tkinter: OK")
except ImportError:
    print("tkinter: NOT AVAILABLE")

try:
    import ttkbootstrap
    print("ttkbootstrap: OK")
except ImportError:
    print("ttkbootstrap: NOT AVAILABLE")

try:
    import PIL
    print("PIL: OK")
except ImportError:
    print("PIL: NOT AVAILABLE")