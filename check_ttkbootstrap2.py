import ttkbootstrap
print("ttkbootstrap attributes:")
for attr in dir(ttkbootstrap):
    if not attr.startswith('_'):
        print(f"  {attr}")