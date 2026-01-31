import sys
import os
import traceback
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                            QHBoxLayout, QStackedWidget, QLineEdit, QRadioButton, 
                            QLabel, QMessageBox, QFileDialog, QPushButton)
from PyQt6.QtCore import Qt, QSize, pyqtSignal
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
    def __init__(self):
        super().__init__()
        self.setWindowTitle("JoularJX GUI")
        
        if OSConfig.is_windows() or OSConfig.is_macos():
            self.resize(875, 650)
        else:
            self.resize(1015, 650)
            
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

        self.pid_widget = PidDisplayWidget()
        self.pid_widget.setVisible(False)
        
        panel = getattr(self.navigationInterface, 'panel', None)
        if panel:
            bottom_layout = getattr(panel, 'bottomLayout', None)
            if bottom_layout:
                 bottom_layout.insertWidget(0, self.pid_widget)
            else:
                 if panel.layout():
                     panel.layout().addWidget(self.pid_widget)

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

    def _setup_standard_ui(self):
        # Central layout
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

    def select_directory(self):
        try:
            dir_path = QFileDialog.getExistingDirectory(self, "Select Joular Output Directory")
            if dir_path:
                self.load_directory(dir_path)
        except Exception as e:
            ErrorHandler.show_error(self, "Error", "Failed to select directory", traceback.format_exc())

    def load_directory(self, dir_path: str):
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
                pid_text = f"PID: {self.current_pid}"
                full_tooltip = f"PID: {self.current_pid}\nDate: {date_str}\nPath: {pid_path}"
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