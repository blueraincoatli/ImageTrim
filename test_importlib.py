import importlib
import sys

print("Python version:", sys.version)
print("Has __file__:", hasattr(importlib, '__file__'))
print("Has util:", hasattr(importlib, 'util'))

if hasattr(importlib, 'util'):
    print("importlib.util is available")
else:
    print("importlib.util is NOT available")
    # Let's see what's in importlib
    print("Attributes in importlib:")
    for attr in dir(importlib):
        print(f"  {attr}")