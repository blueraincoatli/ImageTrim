import os
import sys
import importlib

print("--- Checking importlib directory ---")

importlib_path = os.path.dirname(importlib.__file__)
print(f"Importlib directory: {importlib_path}")

try:
    print("Contents of importlib directory:")
    for item in os.listdir(importlib_path):
        print(f"- {item}")
except Exception as e:
    print(f"Error listing directory: {e}")

print("\n--- Content of importlib/__init__.py ---")
try:
    with open(os.path.join(importlib_path, '__init__.py'), 'r', encoding='utf-8') as f:
        print(f.read())
except Exception as e:
    print(f"Error reading __init__.py: {e}")

print("\n--- Content of importlib/util.py (if exists) ---")
util_path = os.path.join(importlib_path, 'util.py')
if os.path.exists(util_path):
    try:
        with open(util_path, 'r', encoding='utf-8') as f:
            print(f.read())
    except Exception as e:
        print(f"Error reading util.py: {e}")
else:
    print("util.py not found.")

print("\n--- sys.path from check_importlib.py ---")
print(sys.path)
print("----------------------------------------")
