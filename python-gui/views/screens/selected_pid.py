# screens/products.py
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel
from PyQt6.QtCore import Qt

class SelectedPidScreen(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        label = QLabel("PID Selected")
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(label)
