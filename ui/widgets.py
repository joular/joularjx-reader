from utils.os_config import OSConfig

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
