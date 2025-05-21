import os
import sys

class PathUtils:
    @staticmethod
    def get_base_path():
        """Return the base path of the application."""
        if getattr(sys, 'frozen', False):
            # If the application is frozen (e.g., PyInstaller), use the executable's directory
            return os.path.dirname(sys.executable)
        else:
            # If the application is not frozen, use the script's directory
            return os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

    @staticmethod
    def get_resource_path(relative_path):
        """Return the absolute path to a resource, given its relative path."""
        base_path = PathUtils.get_base_path()
        resource_path = os.path.join(base_path, relative_path)
        if not os.path.exists(resource_path):
            raise FileNotFoundError(f"Resource not found: {resource_path}")
        return resource_path