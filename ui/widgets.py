from utils.os_config import OSConfig

# On Windows and macOS, use the fluent-design widgets from qfluentwidgets when
# available; fall back to standard PyQt6 equivalents on other platforms or when
# the optional dependency is not installed.
if OSConfig.is_windows() or OSConfig.is_macos():
    try:
        from qfluentwidgets import RadioButton, TableWidget, CheckBox
    except ImportError:
        from PyQt6.QtWidgets import QRadioButton as RadioButton
        from PyQt6.QtWidgets import QTableWidget as TableWidget
        from PyQt6.QtWidgets import QCheckBox as CheckBox
else:
    from PyQt6.QtWidgets import QRadioButton as RadioButton
    from PyQt6.QtWidgets import QTableWidget as TableWidget
    from PyQt6.QtWidgets import QCheckBox as CheckBox

__all__ = ['RadioButton', 'TableWidget', 'CheckBox']

