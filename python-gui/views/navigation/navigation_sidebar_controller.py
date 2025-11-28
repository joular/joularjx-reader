from PyQt6.QtWidgets import QListWidgetItem
from PyQt6 import QtWidgets
from PyQt6.QtCore import QObject, pyqtSignal as Signal, QPropertyAnimation, QEasingCurve, QSize
from PyQt6.QtGui import QIcon

class NavigationSidebarController(QObject):
    view_home = Signal()
    view_all_pids = Signal()
    view_pid_selected = Signal()
    toggle_requested = Signal()

    def __init__(self, ui):
        super().__init__()
        self.ui = ui
        self.list_full = self.ui.listWidget
        self.list_icon = self.ui.listWidget_icon_only
        self.menu_btn = self.ui.menu_btn
        self.title_icon = self.ui.title_icon
        self.stacked = self.ui.stackedWidget
        self.sidebar = self.ui.sidebar_frame
        self.title_frame = self.sidebar.findChild(QtWidgets.QFrame, "title_frame")
        self.stack = self.ui.sidebarStack

        self._expanded_width = 200
        self._collapsed_width = 55
        self._anim_duration = 250
        self.expanded = True
        self._running_animations = []

        self.menu_list = [
            {"name": "Dashboard", "icon": "./assets/icon/dashboard.svg"},
            {"name": "All PIDs", "icon": "./assets/icon/all_pids_logo.svg"},
            {"name": "PID Selected", "icon": "./assets/icon/selected_pid_logo.svg"}
        ]

        self._populate_menus()
        self._connect_slots()
        self._apply_initial_sizes()
        self.stack.setCurrentIndex(1 if self.expanded else 0)
        
        try:
            icon_path = "./assets/icon/close.svg" if self.expanded else "./assets/icon/open.svg"            
            self.menu_btn.setIcon(QIcon(icon_path))
            self.menu_btn.setFixedSize(40, 40)
            self.menu_btn.setIconSize(QSize(40, 40))
        except Exception:
            pass

    def _populate_menus(self):
        self.list_icon.clear()
        self.list_full.clear()
        for menu in self.menu_list:
            item_icon = QListWidgetItem()
            item_icon.setIcon(QIcon(menu["icon"]))
            item_icon.setSizeHint(QSize(40, 40))
            self.list_icon.addItem(item_icon)
            item_full = QListWidgetItem()
            item_full.setIcon(QIcon(menu["icon"]))
            item_full.setText(menu["name"])
            self.list_full.addItem(item_full)
        self.list_full.setCurrentRow(0)
        self.list_icon.setCurrentRow(0)

    def _connect_slots(self):
        self.menu_btn.setCheckable(True)
        self.menu_btn.toggled.connect(self._on_menu_toggled)
        self.list_full.currentRowChanged.connect(self._on_row_changed)
        self.list_icon.currentRowChanged.connect(self._on_row_changed)
        self.list_full.currentRowChanged.connect(self.list_icon.setCurrentRow)
        self.list_icon.currentRowChanged.connect(self.list_full.setCurrentRow)

    def _apply_initial_sizes(self):
        self.list_full.setMinimumWidth(self._expanded_width)
        self.list_full.setMaximumWidth(self._expanded_width)

    def _on_menu_toggled(self, checked: bool):
        self.animate_toggle(not checked)
        self.title_icon.setHidden(checked)
        self.toggle_requested.emit()

    def animate_toggle(self, expand: bool):
        self.title_frame.setFixedWidth(self._expanded_width if expand else self._collapsed_width)
        anim = QPropertyAnimation(self.sidebar, b"maximumWidth")
        anim.setDuration(self._anim_duration)
        anim.setStartValue(self.sidebar.width())
        anim.setEndValue(self._expanded_width if expand else self._collapsed_width)
        anim.setEasingCurve(QEasingCurve.Type.InOutCubic)
        anim.start()
        self._running_animations.append(anim)
        self.expanded = expand
        self.stack.setCurrentIndex(0 if not expand else 1)
        
        # Update button icon to reflect new state
        try:
            icon_path = "./assets/icon/close.svg" if expand else "./assets/icon/open.svg"
            self.menu_btn.setIcon(QIcon(icon_path))
        except Exception:
            pass

    def _on_row_changed(self, row: int):
        if row < 0:
            return
        self.stacked.setCurrentIndex(row)
        name = self.menu_list[row]["name"]
        if name == "Dashboard": self.view_home.emit()
        elif name == "All PIDs": self.view_all_pids.emit()
        elif name == "PID Selected": self.view_pid_selected.emit()
