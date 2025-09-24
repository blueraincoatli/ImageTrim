
import os
import importlib
import inspect
import sys

# Add the project root to the path to find function_modules
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

# --- Start Diagnosis ---
print("--- Diagnosing importlib ---")
try:
    print(f"importlib file: {importlib.__file__}")
except AttributeError:
    print("importlib is a built-in module and has no __file__ attribute.")

print(f"Attributes in importlib: {dir(importlib)}")
print("--- End Diagnosis ---")
print()

from function_modules import BaseFunctionModule

def test_load():
    modules_dir = 'modules'
    filename = 'deduplication_module.py'
    module_name = filename[:-3]
    
    print(f"Attempting to load {module_name} from {modules_dir}/{filename}")
    
    # Check the state of importlib right before the failing call
    print(f"Does importlib have 'util'? {'util' in dir(importlib)}")
    
    try:
        # The exact code that fails
        module_spec = importlib.util.spec_from_file_location(
            module_name, 
            os.path.join(modules_dir, filename)
        )
        
        if module_spec is None:
            print("Failed to create module spec.")
            return

        imported_module = importlib.util.module_from_spec(module_spec)
        module_spec.loader.exec_module(imported_module)
        
        print("Module loaded successfully!")

        # Optional: Verify the loaded class
        for name, cls in inspect.getmembers(imported_module, inspect.isclass):
            if issubclass(cls, BaseFunctionModule) and cls is not BaseFunctionModule:
                print(f"Found class: {name}")


    except Exception as e:
        print(f"An error occurred: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_load()
