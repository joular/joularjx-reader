import sys
import os
import traceback
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                            QHBoxLayout, QStackedWidget, QLineEdit, QRadioButton, 
                            QLabel, QMessageBox, QFileDialog)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QIcon, QFont

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


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("JoularJX GUI")
        self.resize(1280, 800)
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
        """Load external QSS stylesheet."""
        style_path = PathUtils.get_resource_path('ui/style.qss')
        if os.path.exists(style_path):
            try:
                with open(style_path, "r", encoding="utf-8") as f:
                    self.setStyleSheet(f.read())
            except Exception as e:
                print(f"Failed to load styles: {e}")

    def setup_ui(self):
        # Central layout
        central_widget = QWidget()
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        self.setCentralWidget(central_widget)
        
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
        
        title = QLabel("Call Trees Analysis")
        title.setObjectName("page_title")
        layout.addWidget(title)
        
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
        """Get date from folder name timestamp (preferred) or modification time."""
        try:
            import time
            from datetime import datetime
            
            folder_name = os.path.basename(path)
            parts = folder_name.split('-')
            
            if len(parts) > 1:
                try:
                    timestamp_str = parts[1]
                    timestamp = float(timestamp_str)
                    
                    if timestamp > 1000000000000:
                        timestamp = timestamp / 1000.0
                        
                    return datetime.fromtimestamp(timestamp).strftime("%d/%m/%Y %H:%M:%S")
                except (ValueError, IndexError):
                    pass # Fallback to mtime
            
            # Fallback to modification time
            mtime = os.path.getmtime(path)
            return datetime.fromtimestamp(mtime).strftime("%d/%m/%Y %H:%M:%S")
        except:
            return "Unknown"


    def load_pid_data_direct(self, pid_path: str):
        try:
            pid_path = os.path.normpath(pid_path)
            pid = os.path.basename(pid_path)
            self.current_pid = pid
            self.current_path = pid_path
            self.reader = JoularReader(pid_path)
            
            self.sidebar.update_pid(pid)
            
            self.update_methods_display()
            self.update_calltrees_display()
            self.sidebar.enable_navigation()
            
            self.update_calltrees_display()
            self.sidebar.enable_navigation()
            
            # Auto-navigate to Analysis page
            self.stack.setCurrentIndex(1)
            # Update sidebar selection
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
        app = QApplication(sys.argv)
        app.setWindowIcon(QIcon(PathUtils.get_resource_path('ui/img/logo.png')))
        app.setWindowIcon(QIcon(PathUtils.get_resource_path('ui/img/logo.png')))
        window = MainWindow()
        window.show()
        sys.exit(app.exec())
    except Exception as e:
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()