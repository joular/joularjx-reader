from utils.os_config import OSConfig

def get_base_window_class():
    """Returns the appropriate base window class for the current OS."""
    return OSConfig.get_window_class()


def apply_platform_style(app):
    """Apply platform-specific style to the QApplication."""
    from utils.os_config import OSConfig
    
    if OSConfig.is_macos():
        # Fusion is used instead of the native macOS style so that QSS
        # overrides are applied consistently across the app.
        app.setStyle("Fusion")
        print("[WindowFactory] Using Fusion style (macOS Fluent)")
    elif OSConfig.is_windows():
        # The fluent-widgets library handles styling on Windows; no extra
        # QApplication style override is needed.
        pass
    else:
        app.setStyle("Fusion")
        print("[WindowFactory] Using Fusion style")


