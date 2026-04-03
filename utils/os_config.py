import sys
import os
from typing import Type


class OSConfig:
    """Centralized OS configuration manager."""

    WINDOWS = 'windows'
    MACOS = 'macos'
    LINUX = 'linux'

    _platform: Type[None] = None

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
            return cls.LINUX

    @classmethod
    def get_platform(cls) -> str:
        if cls._platform is None:
            override = os.environ.get('JOULARJX_OS_OVERRIDE', '').lower()
            if override in [cls.WINDOWS, cls.MACOS, cls.LINUX]:
                cls._platform = override
                print(f"[OSConfig] Using OS override: {override}")
            else:
                cls._platform = cls._detect_platform()
                print(f"[OSConfig] Detected platform: {cls._platform}")
        return cls._platform

    @classmethod
    def is_windows(cls) -> bool:
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
        return QMainWindow

    @classmethod
    def get_table_widget_class(cls) -> Type:
        from PyQt6.QtWidgets import QTableWidget
        return QTableWidget

    @classmethod
    def get_style_file(cls) -> str:
        if cls.get_platform() == cls.WINDOWS:
            return 'ui/style_windows.qss'
        return 'ui/style_linux.qss'

    @classmethod
    def reset(cls):
        cls._platform = None
