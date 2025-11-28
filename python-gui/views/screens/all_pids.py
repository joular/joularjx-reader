from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QListWidget, QListWidgetItem
from PyQt6.QtCore import Qt
from controllers.session_controller import SessionController

class AllPidsScreen(QWidget):
    def __init__(self, session: SessionController, parent=None):
        super().__init__(parent)
        self.setObjectName("AllPidsScreen")
        self.session = session

        layout = QVBoxLayout(self)
        layout.setContentsMargins(40, 40, 40, 40)
        layout.setSpacing(20)

        title = QLabel("PIDs")
        title.setObjectName("title")
        title.setAlignment(Qt.AlignmentFlag.AlignLeft)
        layout.addWidget(title)

        self.list_widget = QListWidget()
        self.list_widget.setObjectName("pid_list")
        layout.addWidget(self.list_widget)

        self.populate_pids()

    def populate_pids(self):
        for pid_info in self.session.get_pids():
            item = QListWidgetItem(f"{pid_info['pid']}")
            self.list_widget.addItem(item)
