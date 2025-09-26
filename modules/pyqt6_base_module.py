"""
PyQt6 Function Module Base Class
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from PyQt6.QtWidgets import QWidget

class PyQt6BaseFunctionModule(ABC):
    """
    PyQt6 Function Module Base Class
    - Defines the interface that all function modules must implement
    - Distinguishes between settings UI and workspace UI creation
    """
    def __init__(self, name: str, display_name: str, description: str = "", icon: str = "❓"):
        self.name = name
        self.display_name = display_name
        self.description = description
        self.icon = icon
        self.is_active = False
        self.is_running = False
        self.progress_callback = None
        self.log_callback = None

    def _is_widget_valid(self, widget):
        """Check if a Qt widget is still valid and not deleted"""
        if widget is None:
            return False
        try:
            # Try to access a simple property of the widget
            # If the widget has been deleted, this will raise a RuntimeError
            _ = widget.isVisible()
            return True
        except RuntimeError:
            # Widget has been deleted
            return False

    @abstractmethod
    def create_settings_ui(self, parent: QWidget) -> Optional[QWidget]:
        """
        Create and return the "settings" UI panel for the function (middle column)
        """
        pass

    @abstractmethod
    def create_workspace_ui(self, parent: QWidget) -> Optional[QWidget]:
        """
        Create and return the "workspace" UI panel for the function (right column)
        """
        pass

    @abstractmethod
    def execute(self, params: Dict[str, Any]):
        """
        Execute the core logic of the function in a separate thread.
        UI should be updated through callback functions.
        """
        pass

    @abstractmethod
    def stop_execution(self):
        """
        Stop the currently executing operation
        """
        pass

    def set_callbacks(self, progress_callback, log_callback):
        """Set callback functions to communicate with the main UI"""
        self.progress_callback = progress_callback
        self.log_callback = log_callback

    def on_activate(self):
        """Callback when function is activated"""
        self.is_active = True
        # Only log if the module has a log callback and UI is initialized
        if self.log_callback and hasattr(self, 'log_text') and self.log_text:
            self.log_callback(f"Module '{self.display_name}' activated", "info")

    def on_deactivate(self):
        """Callback when function is deactivated"""
        self.is_active = False
        # Clear any UI references that might become invalid
        self.progress_callback = None
        self.log_callback = None

class PyQt6FunctionManager:
    """PyQt6 Function Manager"""

    def __init__(self):
        self.modules: Dict[str, PyQt6BaseFunctionModule] = {}
        self.active_module: Optional[PyQt6BaseFunctionModule] = None

    def register_module(self, module: PyQt6BaseFunctionModule):
        """Register function module"""
        if module.name in self.modules:
            raise ValueError(f"Module '{module.name}' already exists")
        self.modules[module.name] = module

    def activate_module(self, name: str) -> bool:
        """Activate specified function module"""
        if name not in self.modules:
            return False

        if self.active_module and self.active_module.name != name:
            self.active_module.on_deactivate()

        self.active_module = self.modules[name]
        self.active_module.on_activate()
        return True

    def get_module_names(self) -> list[str]:
        """Get all module names"""
        return list(self.modules.keys())

    def get_module(self, name: str) -> Optional[PyQt6BaseFunctionModule]:
        """Get specified module"""
        return self.modules.get(name)