# views/main_window.py
from PyQt6.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QLabel
from PyQt6.QtCore import Qt
from main_ui import Ui_MainWindow
from views.navigation.navigation_view import NavigationView
from views.screens.home import HomeScreen
from views.screens.all_pids import AllPidsScreen
from views.screens.selected_pid import SelectedPidScreen
from controllers.session_controller import SessionController


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        # Load UI from generated main_ui.py
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.ui.stackedWidget.setStyleSheet("background-color: transparent;")
        self.statusBar().hide()
        
        # ✅ Create a marginless container for centralwidget
        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        layout.addWidget(self.ui.centralwidget)

        # ✅ Important: set container as the central widget
        self.setCentralWidget(container)

        # ✅ Set window icon and logo
        from PyQt6.QtGui import QIcon, QPixmap
        try:
            self.setWindowIcon(QIcon("./assets/icon/Logo.png"))
            self.ui.title_icon.setPixmap(QPixmap("./assets/icon/Logo.png"))
            self.ui.title_icon.setScaledContents(True)
        except Exception:
            pass

        self.setWindowTitle("JoularJx")

        # ✅ Create navigation façade/controller using the ui
        self.navigation = NavigationView(self.ui)

        # ✅ Prepare pages in stacked widget
        self.session = SessionController()
        self._setup_pages()

    def _setup_pages(self):
        stacked = self.ui.stackedWidget

        while stacked.count() > 0:
            stacked.removeWidget(stacked.widget(0))

        stacked.addWidget(HomeScreen(session=self.session))       # index 0
        stacked.addWidget(AllPidsScreen(session=self.session))    # index 1
        stacked.addWidget(SelectedPidScreen())

        stacked.setCurrentIndex(0)

    # Convenience properties for controllers
    @property
    def stack(self):
        return self.ui.stackedWidget

    @property
    def drawer_controller(self):
        return self.navigation.controller
