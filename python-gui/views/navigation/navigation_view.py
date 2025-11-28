# views/navigation/navigation_view.py
from PyQt6.QtWidgets import QWidget, QVBoxLayout
from .navigation_sidebar_controller import NavigationSidebarController

class NavigationView(QWidget):
    """
    Façade légère : contient une instance de NavigationSidebarController (qui lui-même manipule l'UI générée).
    Fournit un accès propre aux signaux et au contrôleur.
    """
    def __init__(self, ui, parent=None):
        super().__init__(parent)
        self.ui = ui
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)

        # create controller that manipulates ui widgets
        self.controller = NavigationSidebarController(self.ui)
        # NOTE: controller is a plain Python object controlling UI widgets (not a QWidget)
        # but it manipulates actual QWidget instances from ui.

        # expose semantic signals directly for the application controller
        self.view_home = self.controller.view_home
        self.view_all_pids = self.controller.view_all_pids
        self.view_pid_selected = self.controller.view_pid_selected

        self.toggle_requested = self.controller.toggle_requested

        # We won't add controller to a layout because controller doesn't return a QWidget.
        # The widgets already belong to the main_ui layout (listWidget and listWidget_icon_only).
        # NavigationView acts as a logical wrapper only.
