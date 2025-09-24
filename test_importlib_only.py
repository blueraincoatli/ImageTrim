import importlib

print("--- Testing importlib.util access ---")

try:
    # Attempt to access importlib.util immediately after import
    util_module = importlib.util
    print(f"Successfully accessed importlib.util: {util_module}")
    print(f"Does importlib.util have spec_from_file_location? {hasattr(importlib.util, 'spec_from_file_location')}")
except AttributeError as e:
    print(f"AttributeError: {e}")
    import traceback
    traceback.print_exc()
except Exception as e:
    print(f"An unexpected error occurred: {e}")
    import traceback
    traceback.print_exc()

print("-------------------------------------")
