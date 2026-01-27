from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                            QPushButton, QButtonGroup)
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QIcon
from utils.path_utils import PathUtils
from utils.style_utils import get_theme_button_style

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
        logo_label.setPixmap(QIcon(PathUtils.get_resource_path('ui/img/joularjx.png')).pixmap(200, 120))
        header_layout.addWidget(logo_label)
        header_layout.addStretch()
        layout.addLayout(header_layout)
        
        # Navigation Buttons Group
        self.nav_group = QButtonGroup(self)
        self.nav_group.setExclusive(True)
        
        # Buttons
        self.btn_home = self.create_nav_button("Home", "ui/img/home.png", 0)
        self.btn_home.setChecked(True)
        layout.addWidget(self.btn_home)
        
        self.btn_analyses = self.create_nav_button("Analysis", "ui/img/method.png", 1)
        self.btn_analyses.setEnabled(False)
        layout.addWidget(self.btn_analyses)
        
        self.btn_calltrees = self.create_nav_button("App CallTree", "ui/img/calltrees.png", 2)
        self.btn_calltrees.setEnabled(False)
        layout.addWidget(self.btn_calltrees)
        
        layout.addStretch()
        
        # Footer for PID info
        self.footer_widget = QWidget()
        footer_layout = QVBoxLayout(self.footer_widget)
        footer_layout.setContentsMargins(20, 10, 20, 20)
        footer_layout.setSpacing(10)
        
        # PID & Date Labels (Moved to TOP of footer)
        info_container = QWidget()
        info_layout = QVBoxLayout(info_container)
        info_layout.setContentsMargins(0, 0, 0, 0)
        info_layout.setSpacing(2)
        
        self.pid_label = QLabel("")
        self.pid_label.setObjectName("pid_label")
        
        self.date_label = QLabel("")
        self.date_label.setObjectName("date_label")
        
        info_layout.addWidget(self.pid_label)
        info_layout.addWidget(self.date_label)
        footer_layout.addWidget(info_container)
        
        # Theme Toggle (Moved to BOTTOM of footer)
        self.theme_btn = QPushButton("☀  Thème")
        self.theme_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.theme_btn.setFixedHeight(32)
        self.theme_btn.setStyleSheet(get_theme_button_style(False))
        self.theme_btn.clicked.connect(self.toggle_theme)
        footer_layout.addWidget(self.theme_btn)
        
        layout.addWidget(self.footer_widget)
        # Footer always visible for theme button
        self.footer_widget.setVisible(True) 

    def toggle_theme(self):
        current_text = self.theme_btn.text()
        if "☀" in current_text:
            self.theme_btn.setText("☽ Thème")
            self.theme_btn.setStyleSheet(get_theme_button_style(True))
        else:
            self.theme_btn.setText("☀ Thème")
            self.theme_btn.setStyleSheet(get_theme_button_style(False))

    def update_pid(self, pid_full):
        """Update the sidebar with PID and formatted date."""
        try:
            
            parts = pid_full.split('-')
            pid_id = parts[0]
            
            self.pid_label.setText(f"PID: {pid_id}")
            
            if len(parts) > 1:
                import datetime
                try:

                    timestamp_str = parts[1]
                    timestamp = float(timestamp_str)
                    
                    if timestamp > 1000000000000:
                        timestamp = timestamp / 1000.0
                        
                    dt = datetime.datetime.fromtimestamp(timestamp)
                    date_str = dt.strftime("%d/%m/%Y %H:%M")
                    self.date_label.setText(date_str)
                except Exception as e:
                    self.date_label.setText(parts[1]) # Fallback
            else:
                 self.date_label.setText("Unknown Date")
                 
        except Exception:
            self.pid_label.setText(f"PID: {pid_full}")
            self.date_label.setText("")

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
