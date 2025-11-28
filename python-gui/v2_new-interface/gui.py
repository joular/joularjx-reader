import sys
import os
import traceback
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                            QHBoxLayout, QPushButton, QFileDialog, QTabWidget,
                            QCheckBox, QLabel, QScrollArea, QFrame, QLineEdit,
                            QStackedWidget, QDialog, QComboBox, QMessageBox,
                            QGraphicsOpacityEffect)
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QIcon, QTransform
from PyQt6 import uic

from reader import JoularReader
from directory_history import DirectoryHistory

from components import (
    MethodTable,
    CallTreeTable,
    ConsumptionGraphDialog,
    CallTreeDetailsDialog,
    RecentDirectories
)
from utils import ErrorHandler
from utils.path_utils import PathUtils

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        try:
            # Load the UI file
            uic.loadUi(PathUtils.get_resource_path('ui/main_window.ui'), self)
            
            # Set window icon
            self.setWindowIcon(QIcon(PathUtils.get_resource_path('ui/img/logo.png')))
            
            # Setup background image
            self.setup_background()
            
            # Setup tab icons
            self.setup_tab_icons()
            
            # Initialize directory history
            self.setup_directory_history()
            
            # Initialize components
            self.setup_components()
            
            # Connect signals
            self.connect_signals()
            
            # Initialize reader
            self.reader = None
            self.current_pid = None
            
            # Initialize recent directories manager
            self.recent_dirs_manager = RecentDirectories(self.dir_history, self)
            
            # Load recent directories
            self.recent_dirs_manager.update_recent_dirs(self.recent_layout)
        except Exception as e:
            ErrorHandler.show_error(
                None, 
                "Initialization Error", 
                "Failed to initialize the application",
                traceback.format_exc()
            )
            sys.exit(1)
            
    def setup_background(self):
        """Setup the background image for home tab."""
        self.background_label = QLabel(self.home_tab)
        self.background_label.setObjectName("background_label")
        pixmap = QIcon(PathUtils.get_resource_path('ui/img/joularjx.png')).pixmap(500, 500)
        self.background_label.setPixmap(pixmap)
        self.background_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        opacity_effect = QGraphicsOpacityEffect()
        opacity_effect.setOpacity(0.2)
        self.background_label.setGraphicsEffect(opacity_effect)
        
        self.background_label.setGeometry(150, 25, self.home_tab.width(), self.home_tab.height())
        self.background_label.lower()
        
    def setup_tab_icons(self):
        """Setup the tab icons."""
        transform = QTransform()
        transform.rotate(90)
        
        home_icon = QIcon(PathUtils.get_resource_path("ui/img/home.png"))
        method_icon = QIcon(PathUtils.get_resource_path("ui/img/method.png"))
        calltrees_icon = QIcon(PathUtils.get_resource_path("ui/img/calltrees.png"))
        
        home_pixmap = home_icon.pixmap(35, 35)
        method_pixmap = method_icon.pixmap(35, 35)
        calltrees_pixmap = calltrees_icon.pixmap(35, 35)
        
        rotated_home = QIcon(home_pixmap.transformed(transform))
        rotated_method = QIcon(method_pixmap.transformed(transform))
        rotated_calltrees = QIcon(calltrees_pixmap.transformed(transform))
        
        self.tab_widget.setTabIcon(0, rotated_home)
        self.tab_widget.setTabIcon(1, rotated_method)
        self.tab_widget.setTabIcon(2, rotated_calltrees)
        
    def setup_directory_history(self):
        """Setup the directory history."""
        if sys.platform == 'win32' and getattr(sys, 'frozen', False):
            app_data_path = os.path.join(os.getenv('APPDATA'), 'JoularJX-Reader')
            os.makedirs(app_data_path, exist_ok=True)
            history_file = os.path.join(app_data_path, 'directory_history.json')
        elif sys.platform == 'linux' and getattr(sys, 'frozen', False):
            # Linux specific path : /usr/share/JoularJX-reader
            app_data_path = "/var/cache/JoularJX-reader"
            history_file = os.path.join(app_data_path, 'directory_history.json')
        else:
            # Default path for non-frozen applications
            history_file = "directory_history.json"
        
        self.dir_history = DirectoryHistory(history_file)
        
    def setup_components(self):
        """Setup the GUI components."""
        from PyQt6.QtWidgets import QTableWidget
        # Méthodes
        orig_methods = self.findChild(QTableWidget, "methods_table")
        if orig_methods is not None and not isinstance(orig_methods, MethodTable):
            parent = orig_methods.parent()
            layout = parent.layout()
            idx = layout.indexOf(orig_methods)
            orig_methods.deleteLater()
            self.methods_table = MethodTable(self)
            layout.insertWidget(idx, self.methods_table)
        else:
            self.methods_table = self.findChild(MethodTable, "methods_table")
        # Calltrees
        orig_calltrees = self.findChild(QTableWidget, "calltrees_table")
        if orig_calltrees is not None and not isinstance(orig_calltrees, CallTreeTable):
            parent = orig_calltrees.parent()
            layout = parent.layout()
            idx = layout.indexOf(orig_calltrees)
            orig_calltrees.deleteLater()
            self.calltrees_table = CallTreeTable(self)
            layout.insertWidget(idx, self.calltrees_table)
        else:
            self.calltrees_table = self.findChild(CallTreeTable, "calltrees_table")
        # Recent layout du .ui
        self.recent_layout = self.findChild(QHBoxLayout, "recent_layout")
        
    def connect_signals(self):
        """Connect all signal handlers."""
        self.select_dir_btn.clicked.connect(self.select_directory)
        self.methods_all_radio.toggled.connect(self.update_methods_display)
        self.calltrees_all_radio.toggled.connect(self.update_calltrees_display)
        self.methods_search.textChanged.connect(self.methods_table.filter_methods)
        self.calltrees_search.textChanged.connect(self.calltrees_table.filter_calltrees)
        self.methods_table.itemSelectionChanged.connect(self.on_method_selected)
        self.calltrees_table.itemSelectionChanged.connect(self.on_calltree_selected)
        self.pid_list.itemSelectionChanged.connect(self.on_pid_selected)
        self.load_pid_btn.clicked.connect(self.load_pid_data)

            
    def load_directory(self, dir_path: str):
        """Load a directory and update the UI."""
        try:
            # Reset current PID and reader
            self.current_pid = None
            self.reader = None
            
            # Clear and hide current PID label
            self.current_pid_label.setText("Current PID: None")
            self.current_pid_label.setVisible(False)
            
            # Clear tables
            self.methods_table.setRowCount(0)
            self.calltrees_table.setRowCount(0)
            
            # Normalize the directory path
            dir_path = os.path.normpath(dir_path)
            
            # Update directory label
            self.dir_label.setText(dir_path)
            
            # Hide PID selection widget if it was visible
            self.pid_selection_widget.setVisible(False)
            
            # First check if the directory itself is a PID directory
            if self.is_pid_directory(dir_path):
                self.dir_history.add_directory(dir_path)
                self.recent_dirs_manager.update_recent_dirs(self.recent_layout)
                self.load_pid_data_direct(dir_path)
                return
            
            # If not a PID directory, scan for PIDs
            pids = [d for d in os.listdir(dir_path) if os.path.isdir(os.path.join(dir_path, d))]
            pid_dirs = [pid for pid in pids if self.is_pid_directory(os.path.join(dir_path, pid))]
            
            if pid_dirs:
                self.dir_history.add_directory(dir_path)
                self.recent_dirs_manager.update_recent_dirs(self.recent_layout)
                
                self.pid_list.clear()
                for pid in pid_dirs:
                    self.pid_list.addItem(pid)
                self.pid_selection_widget.setVisible(True)
            else:
                ErrorHandler.show_error(
                    self,
                    "Invalid Directory",
                    "The selected directory does not contain any valid JoularJX output folders.\n\n"
                    "Please select a directory that contains JoularJX output folders with the following structure:\n"
                    "- app/\n"
                    "  - total/\n"
                    "    - methods/\n"
                    "    - calltrees/\n"
                    "- all/\n"
                    "  - total/\n"
                    "    - methods/\n"
                    "    - calltrees/"
                )
        except Exception as e:
            ErrorHandler.show_error(
                self, 
                "Error Loading Directory", 
                f"Failed to load directory: {dir_path}",
                traceback.format_exc()
            )
            
    def on_pid_selected(self):
        """Handle PID selection from the list."""
        try:
            selected_items = self.pid_list.selectedItems()
            self.load_pid_btn.setEnabled(bool(selected_items))
        except Exception as e:
            ErrorHandler.show_error(
                self, 
                "Error Selecting PID", 
                "Failed to handle PID selection",
                traceback.format_exc()
            )
            
    def load_pid_data_direct(self, pid_path: str):
        """Load PID data directly without user selection."""
        try:
            pid = os.path.basename(pid_path)
            self.current_pid = pid
            
            self.reader = JoularReader(pid_path)
            
            self.pid_selection_widget.setVisible(False)
            
            self.current_pid_label.setText(f"Current PID: {pid}")
            self.current_pid_label.setVisible(True)
            
            self.update_methods_display()
            self.update_calltrees_display()
            
            self.tab_widget.setCurrentIndex(1)
        except Exception as e:
            ErrorHandler.show_error(
                self, 
                "Error Loading PID Data", 
                f"Failed to load data for PID: {pid_path}",
                traceback.format_exc()
            )
            
    def load_pid_data(self):
        """Load data for the selected PID."""
        try:
            selected_items = self.pid_list.selectedItems()
            if not selected_items:
                return
                
            pid = selected_items[0].text()
            self.current_pid = pid
            
            pid_path = os.path.join(self.dir_label.text(), pid)
            
            self.reader = JoularReader(pid_path)
            
            self.current_pid_label.setText(f"Current PID: {pid}")
            self.current_pid_label.setVisible(True)
            
            self.update_methods_display()
            self.update_calltrees_display()
            
            self.tab_widget.setCurrentIndex(1)
        except Exception as e:
            ErrorHandler.show_error(
                self, 
                "Error Loading PID Data", 
                "Failed to load data for selected PID",
                traceback.format_exc()
            )
            
    def on_method_selected(self):
        """Handle method selection."""
        try:
            method = self.methods_table.get_selected_method()
            if method:
                dialog = ConsumptionGraphDialog(method, self)
                dialog.exec()
                self.methods_table.clearSelection()
                self.methods_table.setCurrentItem(None)
                self.methods_table.viewport().update()
        except Exception as e:
            ErrorHandler.show_error(
                self, 
                "Error Selecting Method", 
                "Failed to handle method selection",
                traceback.format_exc()
            )
            
    def on_calltree_selected(self):
        """Handle calltree selection."""
        try:
            calltree = self.calltrees_table.get_selected_calltree()
            if calltree:
                dialog = CallTreeDetailsDialog(calltree, self.current_pid, self)
                dialog.exec()
                self.calltrees_table.clearSelection()
                self.calltrees_table.setCurrentItem(None)
                self.calltrees_table.viewport().update()
        except Exception as e:
            ErrorHandler.show_error(
                self, 
                "Error Selecting Call Tree", 
                "Failed to handle call tree selection",
                traceback.format_exc()
            )
            
    def update_methods_display(self):
        """Update the methods display."""
        try:
            if not self.reader:
                return
                
            methods_dict = self.reader.all_methods if self.methods_all_radio.isChecked() else self.reader.app_methods
            
            methods = []
            for method_name, methods_list in methods_dict.items():
                methods.extend(methods_list)
                
            self.methods_table.update_methods(methods)
        except Exception as e:
            ErrorHandler.show_error(
                self, 
                "Error Updating Methods Display", 
                "Failed to update methods display",
                traceback.format_exc()
            )
            
    def update_calltrees_display(self):
        """Update the calltrees display."""
        try:
            if not self.reader:
                return
                
            calltrees_dict = self.reader.all_call_trees if self.calltrees_all_radio.isChecked() else self.reader.app_call_trees
            
            calltrees = list(calltrees_dict.values())
            self.calltrees_table.update_calltrees(calltrees)
        except Exception as e:
            ErrorHandler.show_error(
                self, 
                "Error Updating Call Trees Display", 
                "Failed to update call trees display",
                traceback.format_exc()
            )
            
    def select_directory(self):
        """Open directory selection dialog and handle selection."""
        try:
            dir_path = QFileDialog.getExistingDirectory(self, "Select Joular Output Directory")
            if dir_path:
                self.load_directory(dir_path)
        except Exception as e:
            ErrorHandler.show_error(
                self, 
                "Error Selecting Directory", 
                "Failed to select directory",
                traceback.format_exc()
            )
            
    def is_pid_directory(self, directory: str) -> bool:
        """Check if the directory is a PID directory by looking for specific files/structure."""
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
        window = MainWindow()
        window.show()
        sys.exit(app.exec())
    except Exception as e:
        ErrorHandler.show_error(
            None, 
            "Application Error", 
            "Failed to start the application",
            traceback.format_exc()
        )
        sys.exit(1)

if __name__ == "__main__":
    main()