import sys
import os
import traceback
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                            QHBoxLayout, QStackedWidget, QLineEdit, QRadioButton, 
                            QLabel, QMessageBox, QFileDialog, QPushButton)
from PyQt6.QtCore import Qt, QSize, pyqtSignal, QLoggingCategory
from PyQt6.QtGui import QIcon, QFont, QAction

from reader import JoularReader
from directory_history import DirectoryHistory

from components import (
    MethodTable,
    CallTreeCardInterface,
    ConsumptionGraphDialog,
    CallTreeDetailsDialog,
    RecentDirectories,
    SidebarWidget,
    DashboardWidget,
    AnalysisPage
)
from utils import ErrorHandler
from utils.path_utils import PathUtils
from utils.os_config import OSConfig
from utils.date_utils import get_directory_date, format_pid_date_short
from ui.window_factory import get_base_window_class


BaseWindowClass = get_base_window_class()

class PidDisplayWidget(QWidget):
    """Compact sidebar widget that shows the currently loaded PID and its date.

    Switches between two views depending on whether the sidebar is expanded:
    - **Compact**: a small ``PID`` icon label.
    - **Expanded**: the full PID string plus a short date beneath it.
    """

    clicked = pyqtSignal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.isSelectable = False
        
        # Main layout for the widget
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)
        self.setStyleSheet("background-color: transparent;")
        
        # The stack
        self.stack = QStackedWidget()
        self.main_layout.addWidget(self.stack)
        
        # Expanded View
        self.expanded_widget = QWidget()
        expanded_layout = QVBoxLayout(self.expanded_widget)
        expanded_layout.setContentsMargins(10, 5, 10, 5)
        expanded_layout.setSpacing(2)
        
        self.pid_label = QLabel("No PID")
        self.pid_label.setObjectName("pid_label")
        self.pid_label.setStyleSheet("color: #666; font-weight: bold; font-family: 'Segoe UI', Arial;")
        
        self.date_label = QLabel("")
        self.date_label.setObjectName("date_label")
        self.date_label.setStyleSheet("color: #999; font-size: 11px; font-family: 'Segoe UI', Arial;")
        
        expanded_layout.addWidget(self.pid_label)
        expanded_layout.addWidget(self.date_label)
        
        # Compact View
        self.compact_widget = QWidget()
        compact_layout = QVBoxLayout(self.compact_widget)
        compact_layout.setContentsMargins(0, 0, 0, 0)
        compact_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        self.icon_label = QLabel("PID") 
        self.icon_label.setStyleSheet("color: #666; font-weight: bold; font-size: 10px;")
        self.icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        compact_layout.addWidget(self.icon_label)
        
        self.stack.addWidget(self.compact_widget)
        self.stack.addWidget(self.expanded_widget)
        
        # Set fixed height to match navigation items
        self.setFixedHeight(50)
        
        # Initial State (Collapsed by default)
        self.set_expanded(False)

    def set_expanded(self, expanded: bool):
        self.stack.setCurrentIndex(1 if expanded else 0)
        
    def update_data(self, pid_text, date_text, full_tooltip):
        self.pid_label.setText(pid_text)
        self.date_label.setText(date_text)
        self.setToolTip(full_tooltip)



class MainWindow(BaseWindowClass):
    """Application main window.

    Selects the appropriate window base class at runtime (standard
    ``QMainWindow`` on Linux, ``FramelessWindow`` on macOS, ``FluentWindow``
    on Windows) and builds the shared page stack with:
    - Dashboard (home / directory picker)
    - Method Analysis (interactive graph + method table)
    - App CallTree (hierarchical call-tree browser)
    """

    def __init__(self):
        super().__init__()
        self.setWindowTitle("JoularJX GUI")
        
        if OSConfig.is_windows() or OSConfig.is_macos():
            self.resize(1020, 680)
            self.setMinimumSize(960, 640)
        else:
            self.resize(1015, 650)
            self.setMinimumSize(1045, 680)
            
        self.setWindowIcon(QIcon(PathUtils.get_resource_path('ui/img/logo.png')))
        
        # Core State
        self.reader = None
        self.current_pid = None
        self.current_path = None
        
        # Services
        self.setup_directory_history()
        self.recent_dirs_manager = RecentDirectories(self.dir_history, self)
        
        # UI Setup
        self.setup_ui()
        self.load_styles()
        
        # Set initial window size and position
        self.move(0, 0)
        
        # Initial Data
        self.recent_dirs_manager.update_recent_dirs(self.dashboard.recent_layout)

    def setup_directory_history(self):
        """Setup the directory history."""
        if sys.platform == 'win32' and getattr(sys, 'frozen', False):
            app_data_path = os.path.join(os.getenv('APPDATA'), 'JoularJX-Reader')
            os.makedirs(app_data_path, exist_ok=True)
            history_file = os.path.join(app_data_path, 'directory_history.json')
        elif sys.platform == 'linux' and getattr(sys, 'frozen', False):
            app_data_path = "/var/cache/JoularJX-reader"
            history_file = os.path.join(app_data_path, 'directory_history.json')
        else:
            history_file = "directory_history.json"
        self.dir_history = DirectoryHistory(history_file)

    def load_styles(self):
        """Load and apply the QSS stylesheets (common + OS-specific)."""
        style_content = ""
        common_path = PathUtils.get_resource_path('ui/style_common.qss')
        if os.path.exists(common_path):
            try:
                with open(common_path, "r", encoding="utf-8") as f:
                    common_qss = f.read()
                    style_content += common_qss
            except Exception as e:
                print(f"Failed to load common styles: {e}")

        os_style_file = OSConfig.get_style_file()
        os_path = PathUtils.get_resource_path(os_style_file)
        
        if os.path.exists(os_path):
            try:
                with open(os_path, "r", encoding="utf-8") as f:
                    style_content += "\n/* OS Specific Overrides */\n"
                    style_content += f.read()
            except Exception as e:
                print(f"Failed to load OS specific styles ({os_style_file}): {e}")

        # Apply combined stylesheet
        if style_content:
            self.setStyleSheet(style_content)

    def setup_ui(self):
        """Dispatch UI initialisation to the correct platform-specific method."""
        is_fluent = hasattr(self, 'navigationInterface')
        
        if is_fluent:
            self._setup_fluent_ui()
        elif hasattr(self, 'setTitleBar'):
            self._setup_frameless_ui()
        else:
            self._setup_standard_ui()
    
    def _setup_frameless_ui(self):
        """Setup UI for FramelessWindow (macOS)."""
        # Setup Title Bar
        from qframelesswindow import StandardTitleBar
        self.setTitleBar(StandardTitleBar(self))
        
        self.titleBar.minBtn.show()
        self.titleBar.maxBtn.show()
        self.titleBar.closeBtn.show()
        
        self.titleBar.raise_()
        
        # Setup standard UI content
        self._setup_standard_ui()
        
        # Specific tweaks for frameless
        if self.layout():
             self.layout().setContentsMargins(0, 0, 0, 0)
    
    def _setup_fluent_ui(self):
        """Setup UI for FluentWindow (Windows only)."""
        self.stack = self.stackedWidget
        
        # Setup pages
        self.setup_pages()
        
        nav_panel = self.navigationInterface.panel

        # ── Larger icons and title bar BEFORE adding nav items ─────────
        self._patch_nav_icon_size(nav_panel)
        self._customize_title_bar()

        # Add navigation items
        from qfluentwidgets import NavigationItemPosition, FluentIcon, NavigationDisplayMode
        
        # Helper to get icon
        def get_icon(name):
            return QIcon(PathUtils.get_resource_path(f'ui/img/{name}'))

        # Store navigation items for enabling/disabling
        self.nav_home = self.navigationInterface.addItem(
            routeKey='dashboard',
            icon=get_icon('home.png'),
            text='Home',
            onClick=lambda: self.stack.setCurrentIndex(0)
        )
        
        self.nav_analysis = self.navigationInterface.addItem(
            routeKey='methods',
            icon=get_icon('method.png'),
            text='Analysis',
            onClick=lambda: self.stack.setCurrentIndex(1)
        )
        self.nav_analysis.setVisible(False) # Hide until PID selected
        
        self.nav_calltrees = self.navigationInterface.addItem(
            routeKey='calltrees',
            icon=get_icon('calltrees.png'),
            text='App CallTree',
            onClick=lambda: self.stack.setCurrentIndex(2)
        )
        self.nav_calltrees.setVisible(False) # Hide until PID selected
        
        self.navigationInterface.setCurrentItem('dashboard')
        
        # Hide the back button/return arrow
        self.navigationInterface.setReturnButtonVisible(False)

        # Resize all nav buttons now that items have been added
        self._resize_nav_buttons(nav_panel)

        # Align hamburger button with title bar center
        self._align_menu_button(nav_panel)

        self.pid_widget = PidDisplayWidget()
        self.pid_widget.setVisible(False)
        
        bottom_layout = getattr(nav_panel, 'bottomLayout', None)
        if bottom_layout:
            bottom_layout.insertWidget(0, self.pid_widget)
        elif nav_panel.layout():
            nav_panel.layout().addWidget(self.pid_widget)

        self.navigationInterface.displayModeChanged.connect(self.on_display_mode_changed)
        
        # Connect signals with error handling
        try:
            self.dashboard.browse_btn.clicked.connect(self.select_directory)
            self.dashboard.pid_selected.connect(self.load_pid_data_direct)
        except Exception as e:
            print(f"Error connecting dashboard signals: {e}")
            traceback.print_exc()

    def on_display_mode_changed(self, mode):
        from qfluentwidgets import NavigationDisplayMode
        is_expanded = (mode == NavigationDisplayMode.EXPAND or mode == NavigationDisplayMode.MENU)
        
        if hasattr(self, 'pid_widget'):
            self.pid_widget.set_expanded(is_expanded)

    def _patch_nav_icon_size(self, nav_panel):
        """Monkey-patch NavigationPushButton.paintEvent to draw 20×20 icons."""
        from qfluentwidgets import NavigationPushButton
        from qfluentwidgets.common.icon import drawIcon
        from qfluentwidgets.common.config import isDarkTheme
        from qfluentwidgets.common.color import autoFallbackThemeColor
        from PyQt6.QtGui import QPainter, QColor, QCursor
        from PyQt6.QtCore import QRectF, QRect, QPoint

        _original_paintEvent = NavigationPushButton.paintEvent

        def _bigger_icon_paintEvent(self_btn, e):
            painter = QPainter(self_btn)
            painter.setRenderHints(
                QPainter.RenderHint.Antialiasing
                | QPainter.RenderHint.TextAntialiasing
                | QPainter.RenderHint.SmoothPixmapTransform
            )
            painter.setPen(Qt.PenStyle.NoPen)

            if self_btn.isPressed:
                painter.setOpacity(0.7)
            if not self_btn.isEnabled():
                painter.setOpacity(0.4)

            c = 255 if isDarkTheme() else 0
            m = self_btn._margins()
            pl, pr = m.left(), m.right()
            globalRect = QRect(self_btn.mapToGlobal(QPoint()), self_btn.size())

            if self_btn._canDrawIndicator():
                painter.setBrush(QColor(c, c, c, 6 if self_btn.isEnter else 10))
                painter.drawRoundedRect(self_btn.rect(), 5, 5)
                painter.setBrush(autoFallbackThemeColor(
                    self_btn.lightIndicatorColor, self_btn.darkIndicatorColor))
                # Center indicator vertically (default indicatorRect uses hardcoded y=10)
                ind_h = 18
                ind_y = (self_btn.height() - ind_h) / 2
                painter.drawRoundedRect(QRectF(pl, ind_y, 3, ind_h), 1.5, 1.5)
            elif ((self_btn.isEnter and globalRect.contains(QCursor.pos()))
                  or self_btn.isAboutSelected) and self_btn.isEnabled():
                painter.setBrush(QColor(c, c, c,
                                        6 if self_btn.isAboutSelected else 10))
                painter.drawRoundedRect(self_btn.rect(), 5, 5)

            # Draw icon at 26×26, always vertically centred;
            # horizontally centred in compact mode, left-aligned in expanded mode
            icon_size = 26
            icon_x = (self_btn.width() - icon_size) / 2 if self_btn.isCompacted else (9 + pl)
            icon_y = (self_btn.height() - icon_size) / 2
            drawIcon(self_btn._icon, painter, QRectF(icon_x, icon_y, icon_size, icon_size))

            if self_btn.isCompacted:
                return

            # Force bold font regardless of any stylesheet override
            from PyQt6.QtGui import QFont as _QFont
            _f = _QFont('Segoe UI', 12)
            _f.setWeight(_QFont.Weight.DemiBold)
            painter.setFont(_f)
            painter.setPen(self_btn.textColor())
            left = 9 + icon_size + 12 + pl  # left-margin + icon + 12 px gap
            painter.drawText(
                QRectF(left, 0, self_btn.width() - 13 - left - pr, self_btn.height()),
                Qt.AlignmentFlag.AlignVCenter,
                self_btn.text(),
            )

        NavigationPushButton.paintEvent = _bigger_icon_paintEvent

    def _resize_nav_buttons(self, nav_panel):
        """Set font on nav buttons after items are added."""
        from qfluentwidgets import NavigationPushButton, NavigationToolButton
        font = QFont('Segoe UI', 13)
        for btn in nav_panel.findChildren(NavigationPushButton):
            if isinstance(btn, NavigationToolButton):
                continue
            btn.setFont(font)
            btn.update()

    def _align_menu_button(self, nav_panel):
        """Make the hamburger button 48 px tall so its icon aligns with the title bar centre."""
        from qfluentwidgets import NavigationToolButton
        from qfluentwidgets.common.icon import drawIcon
        from qfluentwidgets.common.config import isDarkTheme
        from qfluentwidgets.common.color import autoFallbackThemeColor
        from PyQt6.QtGui import QPainter, QColor, QCursor
        from PyQt6.QtCore import QRectF, QRect, QPoint

        menu_btn = getattr(nav_panel, 'menuButton', None)
        if not menu_btn:
            return

        # Monkey-patch paintEvent to vertically centre the 16×16 icon
        def _centered_tool_paintEvent(self_btn, e):
            painter = QPainter(self_btn)
            painter.setRenderHints(
                QPainter.RenderHint.Antialiasing
                | QPainter.RenderHint.TextAntialiasing
                | QPainter.RenderHint.SmoothPixmapTransform
            )
            painter.setPen(Qt.PenStyle.NoPen)

            if self_btn.isPressed:
                painter.setOpacity(0.7)
            if not self_btn.isEnabled():
                painter.setOpacity(0.4)

            c = 255 if isDarkTheme() else 0
            m = self_btn._margins()
            pl, pr = m.left(), m.right()
            globalRect = QRect(self_btn.mapToGlobal(QPoint()), self_btn.size())

            if self_btn._canDrawIndicator():
                painter.setBrush(QColor(c, c, c, 6 if self_btn.isEnter else 10))
                painter.drawRoundedRect(self_btn.rect(), 5, 5)
                painter.setBrush(autoFallbackThemeColor(
                    self_btn.lightIndicatorColor, self_btn.darkIndicatorColor))
                painter.drawRoundedRect(self_btn.indicatorRect(), 1.5, 1.5)
            elif ((self_btn.isEnter and globalRect.contains(QCursor.pos()))
                  or self_btn.isAboutSelected) and self_btn.isEnabled():
                painter.setBrush(QColor(c, c, c,
                                        6 if self_btn.isAboutSelected else 10))
                painter.drawRoundedRect(self_btn.rect(), 5, 5)

            # Centre the 16×16 icon vertically (default hardcodes y=10)
            icon_size = 16
            icon_x = 11.5 + pl
            icon_y = (self_btn.height() - icon_size) / 2
            drawIcon(self_btn._icon, painter, QRectF(icon_x, icon_y, icon_size, icon_size))

            if self_btn.isCompacted:
                return

            painter.setFont(self_btn.font())
            painter.setPen(self_btn.textColor())
            left = 44 + pl if not self_btn.icon().isNull() else pl + 16
            painter.drawText(
                QRectF(left, 0, self_btn.width() - 13 - left - pr, self_btn.height()),
                Qt.AlignmentFlag.AlignVCenter,
                self_btn.text(),
            )

        NavigationToolButton.paintEvent = _centered_tool_paintEvent

    def _customize_title_bar(self):
        """Enlarge the FluentWindow title bar icon and title font."""
        tb = self.titleBar
        # Bigger window icon (26×26 instead of 18×18)
        if hasattr(tb, 'iconLabel'):
            tb.iconLabel.setFixedSize(26, 26)
            icon = self.windowIcon()
            if not icon.isNull():
                tb.iconLabel.setPixmap(icon.pixmap(26, 26))
        # Bigger title font – visually close to the navigation hamburger icon
        if hasattr(tb, 'titleLabel'):
            tb.titleLabel.setStyleSheet(
                "font-size: 22px; font-weight: 600; font-family: 'Segoe UI';"
            )
            tb.titleLabel.adjustSize()

    def _setup_standard_ui(self):
        """Build the sidebar + stacked-page layout used on Linux and macOS."""
        central_widget = QWidget()
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        if hasattr(self, 'setCentralWidget'):
            self.setCentralWidget(central_widget)
        else:
            # Fallback for QWidget-based windows (like FramelessWindow)
            if not self.layout():
                layout = QVBoxLayout(self)
                layout.setContentsMargins(0, 0, 0, 0)
                layout.setSpacing(0)
                self.setLayout(layout)
            
            self.layout().addWidget(central_widget)
        
        # Sidebar
        self.sidebar = SidebarWidget(self)
        main_layout.addWidget(self.sidebar)
        
        # Stacked Content
        self.stack = QStackedWidget()
        main_layout.addWidget(self.stack)
        
        # Pages
        self.setup_pages()
        
        # High-level signal connections
        self.sidebar.nav_group.buttonClicked.connect(self.on_nav_clicked)
        self.sidebar.toggle_requested.connect(self.on_sidebar_toggle)
        self.dashboard.browse_btn.clicked.connect(self.select_directory)
        self.dashboard.pid_selected.connect(self.load_pid_data_direct)




    def setup_pages(self):
        # Dashboard
        self.dashboard = DashboardWidget()
        self.stack.addWidget(self.dashboard)

        
        # Methods
        self.methods_page = self.create_methods_page()
        self.stack.addWidget(self.methods_page)
        
        # Call Trees
        self.calltrees_page = self.create_calltrees_page()
        self.stack.addWidget(self.calltrees_page)

    def create_methods_page(self):
        """Create the analysis page with interactive graph."""
        self.analysis_page = AnalysisPage()
        return self.analysis_page

    def create_calltrees_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Card interface
        self.calltree_cards = CallTreeCardInterface(self)
        self.calltree_cards.calltree_selected.connect(self.on_calltree_selected_hierarchy)
        self.calltree_cards.method_selected.connect(self.on_method_selected_from_hierarchy)
        layout.addWidget(self.calltree_cards)
        
        return page

    def on_nav_clicked(self, btn):
        index = btn.property("index")
        if index >= 0:
            self.stack.setCurrentIndex(index)

    def on_sidebar_toggle(self, is_expanded):
        """Handle sidebar toggle request. Content adapts automatically via layout."""
        # The QHBoxLayout with stretch will automatically adapt
        # No additional action needed as the sidebar width change handles it
        pass

    def select_directory(self):
        try:
            dir_path = QFileDialog.getExistingDirectory(self, "Select Joular Output Directory")
            if dir_path:
                self.load_directory(dir_path)
        except Exception as e:
            ErrorHandler.show_error(self, "Error", "Failed to select directory", traceback.format_exc())

    def load_directory(self, dir_path: str):
        """Inspect *dir_path* and either load it as a PID folder or show its children."""
        try:
            dir_path = os.path.normpath(dir_path)
            self.dashboard.set_selected_path(dir_path)
            
            if self.is_pid_directory(dir_path):
                self.dir_history.add_directory(dir_path)
                self.recent_dirs_manager.update_recent_dirs(self.dashboard.recent_layout)
                self.load_pid_data_direct(dir_path)
                self.dashboard.set_results_visible(False)
                return
            
            pids = [d for d in os.listdir(dir_path) if os.path.isdir(os.path.join(dir_path, d))]
            pid_dirs = []
            for pid in pids:
                full_p = os.path.join(dir_path, pid)
                if self.is_pid_directory(full_p):
                    date_str = self.get_directory_date(full_p)
                    pid_dirs.append((pid, date_str, full_p))
            
            if pid_dirs:
                self.dir_history.add_directory(dir_path)
                self.recent_dirs_manager.update_recent_dirs(self.dashboard.recent_layout)
                self.dashboard.update_results(pid_dirs)
                self.dashboard.set_results_visible(True)
            else:
                 self.dashboard.set_results_visible(False)
                 ErrorHandler.show_error(self, "Invalid Directory", "No valid JoularJX output found.")
        except Exception as e:
            ErrorHandler.show_error(self, "Error", "Failed to load directory", traceback.format_exc())

    def get_directory_date(self, path: str) -> str:
        return get_directory_date(path)


    def load_pid_data_direct(self, pid_path: str):
        """Load JoularJX data from *pid_path* and update all pages."""
        try:
            pid_path = os.path.normpath(pid_path)
            pid = os.path.basename(pid_path)
            self.current_pid = pid
            self.current_path = pid_path
            self.reader = JoularReader(pid_path)
            
            if hasattr(self, 'sidebar'):
                self.sidebar.update_pid(pid)
                self.sidebar.enable_navigation()

            if hasattr(self, 'nav_analysis'):
                self.nav_analysis.setVisible(True)
                self.nav_calltrees.setVisible(True)
                self.navigationInterface.setCurrentItem('methods')
            
            date_str = format_pid_date_short(pid) or ""

            if hasattr(self, 'pid_widget'):
                pid_number = self.current_pid.split('-')[0] if '-' in self.current_pid else self.current_pid
                pid_text = f"PID: {pid_number}"
                full_tooltip = f"PID: {pid_number}\nDate: {date_str}\nPath: {pid_path}"
                self.pid_widget.update_data(pid_text, date_str, full_tooltip)
                self.pid_widget.setVisible(True)
            
            self.update_methods_display()
            self.update_calltrees_display()
            
            # Auto-navigate to Analysis page
            self.stack.setCurrentIndex(1)
            
            # Update sidebar selection
            if hasattr(self, 'sidebar'):
                self.sidebar.btn_analyses.setChecked(True)
                self.sidebar.btn_home.setChecked(False)
        except Exception as e:
            ErrorHandler.show_error(self, "Error", "Failed to load PID data", traceback.format_exc())


    def update_methods_display(self):
        """Update the analysis page with reader data."""
        if not self.reader:
            return
        self.analysis_page.set_reader(self.reader)

    def update_calltrees_display(self):
        """Refresh the call-tree page with data from the current reader."""
        if not self.reader: return
        self.calltree_cards.update_data(self.reader.app_call_trees, self.reader.all_call_trees)


    def on_calltree_selected_hierarchy(self, calltree):
        if calltree:
            CallTreeDetailsDialog(calltree, self.current_pid, self).exec()
    
    def on_method_selected_from_hierarchy(self, method):
        """Handle method selection from hierarchy widget."""
        if method:
            ConsumptionGraphDialog(method, self).exec()
                     
    def is_pid_directory(self, directory: str) -> bool:
        """Return True if *directory* has the expected JoularJX output structure."""
        try:
            app_dir = os.path.join(directory, "app")
            all_dir = os.path.join(directory, "all")
            if os.path.exists(app_dir) and os.path.exists(all_dir):
                methods_dir = os.path.join(app_dir, "total", "methods")
                calltrees_dir = os.path.join(app_dir, "total", "calltrees")
                return os.path.exists(methods_dir) and os.path.exists(calltrees_dir)
            return False
        except Exception:
            return False

def main():
    try:
        from ui.window_factory import apply_platform_style

        # Suppress verbose AT-SPI accessibility bridge warnings on Linux
        QLoggingCategory.setFilterRules("qt.accessibility.atspi=false")

        app = QApplication(sys.argv)
        apply_platform_style(app)  # Apply platform-specific styles
        app.setWindowIcon(QIcon(PathUtils.get_resource_path('ui/img/logo.png')))
        window = MainWindow()
        window.show()
        sys.exit(app.exec())
    except Exception as e:
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()