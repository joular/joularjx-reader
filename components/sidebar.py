from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                            QPushButton, QButtonGroup)
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QIcon
from utils.path_utils import PathUtils

class SidebarWidget(QWidget):
    """ Custom sidebar widget for navigation. """
    
    SIDEBAR_WIDTH = 250

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("sidebar")
        self.setFixedWidth(self.SIDEBAR_WIDTH)
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(5)
        
        # Header / Logo
        header_layout = QHBoxLayout()
        header_layout.setContentsMargins(20, 20, 20, 20)
        logo_label = QLabel()
        logo_label.setPixmap(QIcon(PathUtils.get_resource_path('ui/img/logo.png')).pixmap(32, 32))
        title_label = QLabel("JoularJX Reader")
        title_label.setObjectName("sidebar_title")
        header_layout.addWidget(logo_label)
        header_layout.addWidget(title_label)
        header_layout.addStretch()
        layout.addLayout(header_layout)
        
        # Navigation Buttons Group
        self.nav_group = QButtonGroup(self)
        self.nav_group.setExclusive(True)
        
        # Buttons
        self.btn_home = self.create_nav_button("Accueil", "ui/img/home.png", 0)
        self.btn_home.setChecked(True)
        layout.addWidget(self.btn_home)
        
        self.btn_analyses = self.create_nav_button("Analyses", "ui/img/method.png", 1)
        self.btn_analyses.setEnabled(False)
        layout.addWidget(self.btn_analyses)
        
        self.btn_calltrees = self.create_nav_button("App Calltree", "ui/img/calltrees.png", 2)
        self.btn_calltrees.setEnabled(False)
        layout.addWidget(self.btn_calltrees)
        
        layout.addStretch()
        layout.addSpacing(20)

    def create_nav_button(self, text, icon_path, index):
        btn = QPushButton(text)
        btn.setProperty("index", index)
        btn.setCheckable(True)
        btn.setProperty("class", "nav-button")
        if icon_path:
             btn.setIcon(QIcon(PathUtils.get_resource_path(icon_path)))
             btn.setIconSize(QSize(20, 20))
        self.nav_group.addButton(btn)
        return btn

    def enable_navigation(self):
        """ Enable PID-dependent navigation items. """
        self.btn_analyses.setEnabled(True)
        self.btn_calltrees.setEnabled(True)
