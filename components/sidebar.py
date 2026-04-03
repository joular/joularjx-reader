from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                            QPushButton, QButtonGroup)
from PyQt6.QtCore import Qt, QSize, pyqtSignal, QPropertyAnimation, QRect, QParallelAnimationGroup
from PyQt6.QtGui import QIcon, QPainter, QPen, QColor
from utils.path_utils import PathUtils
from utils.os_config import OSConfig
from utils.ui_constants import SIDEBAR_WIDTH_WINDOWS, SIDEBAR_WIDTH_OTHER, LOGO_SIZE_WINDOWS, LOGO_SIZE_OTHER


class HamburgerButton(QPushButton):
    """Modern sidebar toggle button with clean lines."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(36, 36)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setToolTip("Toggle sidebar")
        self.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                border: none;
                border-radius: 7px;
                padding: 0px;
            }
            QPushButton:hover {
                background-color: rgba(0, 0, 0, 0.06);
            }
            QPushButton:pressed {
                background-color: rgba(0, 0, 0, 0.10);
            }
        """)
    
    def paintEvent(self, event):
        """Paint a refined hamburger icon (3 rounded lines), always centered."""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        line_color = QColor("#64748B")
        pen = QPen(line_color, 1.8, Qt.PenStyle.SolidLine)
        pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        painter.setPen(pen)
        
        cx = self.width() // 2
        cy = self.height() // 2
        half_w = 8
        gap = 5
        start_x = cx - half_w
        end_x = cx + half_w
        
        for i in range(-1, 2):
            y = cy + i * gap
            painter.drawLine(start_x, y, end_x, y)
        
        painter.end()


class SidebarWidget(QWidget):
    """ Custom sidebar widget for navigation. """
    
    # Signals
    toggle_requested = pyqtSignal(bool)  # Emits True if expanded, False if collapsed
    
    SIDEBAR_WIDTH_WINDOWS = 70
    SIDEBAR_WIDTH_OTHER = 200
    SIDEBAR_WIDTH_COLLAPSED = 70  # Width when collapsed
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("sidebar")
        self.is_expanded = False  # Start collapsed on all platforms
        
        self.setMinimumWidth(self.SIDEBAR_WIDTH_COLLAPSED)
        self.setMaximumWidth(self.SIDEBAR_WIDTH_COLLAPSED)
            
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(2)
        
        # Header row: Logo + Hamburger button inline (expanded) or hamburger centered (collapsed)
        self.header_widget = QWidget()
        self.header_widget.setObjectName("sidebar_header")
        self.header_layout = QHBoxLayout(self.header_widget)
        # Right margin: 17 centers the hamburger button in collapsed state (70 - 36) / 2
        collapsed_right_margin = (self.SIDEBAR_WIDTH_COLLAPSED - 36) // 2
        self.header_layout.setContentsMargins(10, 10, collapsed_right_margin, 6)
        self.header_layout.setSpacing(0)
        
        self.logo_label = QLabel()
        self.logo_label.setAlignment(Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft)
        
        if OSConfig.is_windows():
            logo_size = (50, 30)
        else:
            logo_size = (100, 60)
            
        self.logo_pixmap = QIcon(PathUtils.get_resource_path('ui/img/joularjx.png')).pixmap(*logo_size)
        self.logo_label.setPixmap(self.logo_pixmap)
        
        self.hamburger_btn = HamburgerButton()
        self.hamburger_btn.clicked.connect(self.toggle_sidebar)
        
        # Build header once: logo + stretch + hamburger (never rebuilt)
        self.header_layout.addWidget(self.logo_label)
        self.header_layout.addStretch()
        self.header_layout.addWidget(self.hamburger_btn)
        
        # Store the logo's natural width for animation
        self._logo_natural_width = logo_size[0]
        
        layout.addWidget(self.header_widget)
        
        # Navigation Buttons Group container
        nav_container = QWidget()
        nav_layout = QVBoxLayout(nav_container)
        nav_layout.setContentsMargins(0, 0, 0, 0)
        nav_layout.setSpacing(2)
        
        # Setup button group for nav buttons only
        self.nav_group = QButtonGroup(self)
        self.nav_group.setExclusive(True)
        
        show_text = self.is_expanded
        
        self.btn_home = self.create_nav_button("Home" if show_text else "", "ui/img/home.png", 0)
        self.btn_home.setChecked(True)
        nav_layout.addWidget(self.btn_home)
        
        self.btn_analyses = self.create_nav_button("Analysis" if show_text else "", "ui/img/method.png", 1)
        self.btn_analyses.setEnabled(False)
        nav_layout.addWidget(self.btn_analyses)
        
        self.btn_calltrees = self.create_nav_button("App CallTree" if show_text else "", "ui/img/calltrees.png", 2)
        self.btn_calltrees.setEnabled(False)
        nav_layout.addWidget(self.btn_calltrees)
        
        # Set initial collapsed icon size and property
        if not self.is_expanded:
            for btn in (self.btn_home, self.btn_analyses, self.btn_calltrees):
                btn.setIconSize(QSize(24, 24))
                btn.setProperty("collapsed", True)
        
        layout.addWidget(nav_container)
        layout.addStretch()
        
        # Footer for PID info
        self.footer_widget = QWidget()
        footer_layout = QVBoxLayout(self.footer_widget)
        footer_layout.setContentsMargins(10, 5, 10, 10)
        footer_layout.setSpacing(5)
        
        info_container = QWidget()
        info_layout = QVBoxLayout(info_container)
        info_layout.setContentsMargins(0, 0, 0, 0)
        info_layout.setSpacing(2)
        
        self.pid_label = QLabel("")
        self.pid_label.setObjectName("pid_label")
        
        self.date_label = QLabel("")
        self.date_label.setObjectName("date_label")
        
        # Compact PID label for collapsed state
        self.pid_label_compact = QLabel("")
        self.pid_label_compact.setObjectName("pid_label")
        self.pid_label_compact.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.pid_label_compact.setVisible(False)
        
        info_layout.addWidget(self.pid_label)
        info_layout.addWidget(self.date_label)
        info_layout.addWidget(self.pid_label_compact)
        footer_layout.addWidget(info_container)
        
        layout.addWidget(self.footer_widget)
        # Footer always visible for theme button
        self.footer_widget.setVisible(True)
        
        # Set initial logo state (start collapsed)
        self.logo_label.setMaximumWidth(0)
        
        # Set initial footer visibility (collapsed = compact PID only)
        self.pid_label.setVisible(False)
        self.date_label.setVisible(False)
        self.pid_label_compact.setVisible(False)

    def update_pid(self, pid_full):
        """Update the sidebar with PID and formatted date."""
        try:
            
            parts = pid_full.split('-')
            pid_id = parts[0]
            
            self.pid_label.setText(f"PID: {pid_id}")
            self.pid_label_compact.setText(f"PID\n{pid_id}")
            
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
            self.pid_label_compact.setText(f"PID\n{pid_full}")
            self.date_label.setText("")
        
        # Show the appropriate label based on current sidebar state
        self.pid_label.setVisible(self.is_expanded)
        self.date_label.setVisible(self.is_expanded)
        self.pid_label_compact.setVisible(not self.is_expanded)

    def toggle_sidebar(self):
        """Toggle sidebar expansion/collapse."""
        self.is_expanded = not self.is_expanded
        self.update_sidebar_state()
        self.toggle_requested.emit(self.is_expanded)
    
    def update_sidebar_state(self):
        """Update sidebar width and button text based on is_expanded state."""
        if self.is_expanded:
            new_width = self.SIDEBAR_WIDTH_OTHER
            show_text = True
            icon_size = 20
            target_logo_width = self._logo_natural_width
        else:
            new_width = self.SIDEBAR_WIDTH_COLLAPSED
            show_text = False
            icon_size = 24
            target_logo_width = 0
        
        # Animate width + logo in parallel for a smooth transition
        self._animate_sidebar(new_width, target_logo_width)
        
        # Update button texts
        self.btn_home.setText("Home" if show_text else "")
        self.btn_analyses.setText("Analysis" if show_text else "")
        self.btn_calltrees.setText("App CallTree" if show_text else "")
        
        # Update icon sizes
        self.btn_home.setIconSize(QSize(icon_size, icon_size))
        self.btn_analyses.setIconSize(QSize(icon_size, icon_size))
        self.btn_calltrees.setIconSize(QSize(icon_size, icon_size))

        is_collapsed = not show_text
        for btn in (self.btn_home, self.btn_analyses, self.btn_calltrees):
            btn.setProperty("collapsed", is_collapsed)
            btn.style().unpolish(btn)
            btn.style().polish(btn)
            btn.update()
        
        # Update footer visibility
        self.pid_label.setVisible(show_text)
        self.date_label.setVisible(show_text)
        self.pid_label_compact.setVisible(not show_text)
    
    def _animate_sidebar(self, new_width, target_logo_width):
        """Animate sidebar width and logo width in parallel for a smooth transition."""
        if hasattr(self, '_anim_group') and self._anim_group.state() == self._anim_group.State.Running:
            self._anim_group.stop()
        
        from PyQt6.QtCore import QEasingCurve
        
        duration = 300
        easing = QEasingCurve.Type.InOutCubic
        
        # Compute right margin to center the hamburger when collapsed
        # hamburger_left = left_margin + stretch = sidebar_width - right_margin - hamburger_width
        # For centered: right_margin = sidebar_width - hamburger_width/2 - sidebar_width/2 - hamburger_width/2
        #             = (sidebar_width - hamburger_width) / 2 - left_margin... simplified:
        # collapsed centered right_margin = sidebar_width - left_margin - hamburger_width - (sidebar_width - hamburger_width) / 2 + left_margin
        # Actually: for hamburger centered, right = sidebar - 36 - (sidebar-36)/2 - left + left... 
        # Let's just compute: collapsed_right = COLLAPSED_W - 10 - 36 - ((COLLAPSED_W - 36) // 2 - 10)
        # Simpler: hamburger_left_from_edge = (COLLAPSED_W - 36) // 2 = 17
        # hamburger_left_from_edge = left_margin + stretch = sidebar_w - right_margin - 36
        # 17 = 70 - right_margin - 36 → right_margin = 17
        self._margin_right_expanded = 10
        self._margin_right_collapsed = (self.SIDEBAR_WIDTH_COLLAPSED - 36) // 2  # = 17
        
        # Sidebar width animation
        self._width_anim = QPropertyAnimation(self, b"minimumWidth")
        self._width_anim.setDuration(duration)
        self._width_anim.setEasingCurve(easing)
        self._width_anim.setStartValue(self.minimumWidth())
        self._width_anim.setEndValue(new_width)
        self._width_anim.valueChanged.connect(self._on_width_changed)
        
        # Logo width animation
        self._logo_anim = QPropertyAnimation(self.logo_label, b"maximumWidth")
        self._logo_anim.setDuration(duration)
        self._logo_anim.setEasingCurve(easing)
        self._logo_anim.setStartValue(self.logo_label.maximumWidth())
        self._logo_anim.setEndValue(target_logo_width)
        
        self._anim_group = QParallelAnimationGroup(self)
        self._anim_group.addAnimation(self._width_anim)
        self._anim_group.addAnimation(self._logo_anim)
        
        def on_finished():
            self.setMaximumWidth(new_width)
            self.logo_label.setMaximumWidth(target_logo_width)
            # Ensure final margin is exact
            final_right = self._margin_right_collapsed if new_width == self.SIDEBAR_WIDTH_COLLAPSED else self._margin_right_expanded
            self.header_layout.setContentsMargins(10, 10, final_right, 6)
        
        self._anim_group.finished.connect(on_finished)
        self._anim_group.start()
    
    def _on_width_changed(self, value):
        """Update max width and interpolate header right margin to keep hamburger centered."""
        self.setMaximumWidth(value)
        # Interpolate: t=0 → collapsed, t=1 → expanded
        width_range = self.SIDEBAR_WIDTH_OTHER - self.SIDEBAR_WIDTH_COLLAPSED
        if width_range > 0:
            t = (value - self.SIDEBAR_WIDTH_COLLAPSED) / width_range
            t = max(0.0, min(1.0, t))
            right_margin = int(self._margin_right_collapsed + t * (self._margin_right_expanded - self._margin_right_collapsed))
            self.header_layout.setContentsMargins(10, 10, right_margin, 6)

    def create_nav_button(self, text, icon_path, index):
        btn = QPushButton(text)
        btn.setProperty("index", index)
        btn.setProperty("collapsed", not bool(text))
        btn.setCheckable(True)
        btn.setProperty("class", "nav-button")
        if icon_path:
             btn.setIcon(QIcon(PathUtils.get_resource_path(icon_path)))
             btn.setIconSize(QSize(20, 20))
        self.nav_group.addButton(btn, index)  # Add button with ID for exclusive behavior
        return btn

    def enable_navigation(self):
        """ Enable PID-dependent navigation items. """
        self.btn_analyses.setEnabled(True)
        self.btn_calltrees.setEnabled(True)
