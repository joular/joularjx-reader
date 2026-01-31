from utils.os_config import OSConfig

def get_base_window_class():
    """Returns the appropriate base window class for the current OS."""
    return OSConfig.get_window_class()


def apply_platform_style(app):
    """Apply platform-specific style to the QApplication."""
    from utils.os_config import OSConfig
    
    if OSConfig.is_macos():
        app.setStyle("Fusion")
        print("[WindowFactory] Using Fusion style (macOS Fluent)")
    elif OSConfig.is_windows():
        pass
    else:
        app.setStyle("Fusion")
        print("[WindowFactory] Using Fusion style")

