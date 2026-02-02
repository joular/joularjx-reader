import sys
import os
from typing import Type, Optional
import contextlib

# suppr startup message
if sys.platform == 'win32':
    try:
        with contextlib.redirect_stdout(None):
            import qfluentwidgets
    except ImportError:
        pass

class OSConfig:
    """Centralized OS configuration manager."""
    
    WINDOWS = 'windows'
    MACOS = 'macos'
    LINUX = 'linux'
    
    _platform: Optional[str] = None
    _override_platform: Optional[str] = None
    
    @classmethod
    def _detect_platform(cls) -> str:
        """Detect the current platform."""
        if sys.platform == 'win32':
            return cls.WINDOWS
        elif sys.platform == 'darwin':
            return cls.MACOS
        elif sys.platform.startswith('linux'):
            return cls.LINUX
        else:
            # Fallback to Linux for unknown platforms
            return cls.LINUX
    
    @classmethod
    def get_platform(cls) -> str:
        if cls._platform is None:
            override = os.environ.get('JOULARJX_OS_OVERRIDE', '').lower()
            if override in [cls.WINDOWS, cls.MACOS, cls.LINUX]:
                cls._override_platform = override
                cls._platform = override
                print(f"[OSConfig] Using OS override: {override}")
            else:
                cls._platform = cls._detect_platform()
                print(f"[OSConfig] Detected platform: {cls._platform}")
        
        return cls._platform
    
    @classmethod
    def is_windows(cls) -> bool:
        """Check if current platform is Windows."""
        return cls.get_platform() == cls.WINDOWS
    
    @classmethod
    def is_macos(cls) -> bool:
        return cls.get_platform() == cls.MACOS
    
    @classmethod
    def is_linux(cls) -> bool:
        return cls.get_platform() == cls.LINUX
    
    @classmethod
    def get_window_class(cls) -> Type:
        from PyQt6.QtWidgets import QMainWindow
        
        if cls.is_windows() or cls.is_macos():
            try:
                from qfluentwidgets import FluentWindow
                return FluentWindow
            except ImportError:
                print("[OSConfig] qfluentwidgets not available, falling back to QMainWindow")
                return QMainWindow
                 
        if cls.is_macos():
            try:
                from qframelesswindow import FramelessWindow
                return FramelessWindow
            except ImportError:
                 print("[OSConfig] qframelesswindow not available, falling back to QMainWindow")
                 return QMainWindow
        
        return QMainWindow
    
    @classmethod
    def get_table_widget_class(cls) -> Type:
        from PyQt6.QtWidgets import QTableWidget
        
        if cls.is_windows() or cls.is_macos():
            try:
                from qfluentwidgets import TableWidget as FluentTableWidget
                return FluentTableWidget
            except ImportError:
                print("[OSConfig] qfluentwidgets not available, falling back to QTableWidget")
                return QTableWidget
        
        return QTableWidget
    
    @classmethod
    def get_style_file(cls) -> str:
        platform = cls.get_platform()
        
        if platform == cls.WINDOWS or platform == cls.MACOS:
            return 'ui/style_windows.qss'
        elif platform == cls.LINUX:
            return 'ui/style_linux.qss'
        else:
            # Fallback
            return 'ui/style_linux.qss'
    
    @classmethod
    def reset(cls):
        cls._platform = None
        cls._override_platform = None
