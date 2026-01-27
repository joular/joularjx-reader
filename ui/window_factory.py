import sys
from PyQt6.QtWidgets import QMainWindow

def get_base_window_class():
    """Returns the appropriate base window class for the current OS."""
    if sys.platform == 'win32':
        try:
            from qfluentwidgets import FluentWindow
            return FluentWindow
        except ImportError:
            print("Warning: PyQt6-Fluent-Widgets not installed. Falling back to QMainWindow.")
            return QMainWindow
    elif sys.platform == 'darwin':
        try:
            from qframelesswindow import FramelessWindow
            return FramelessWindow
        except ImportError:
            print("Warning: pyqt-frameless-window not installed. Falling back to QMainWindow.")
            return QMainWindow
    else:
        # Linux and other platforms
        return QMainWindow

def apply_platform_style(app):
    """Apply platform-specific style to the QApplication."""
    if sys.platform.startswith('linux'):
        app.setStyle('Fusion')
