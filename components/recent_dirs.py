import os
import traceback
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QMessageBox
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QIcon
from utils import ErrorHandler
from datetime import datetime
from utils.path_utils import PathUtils
from utils.style_utils import get_icon_style

class RecentDirectories:
    def __init__(self, dir_history, parent=None):
        self.dir_history = dir_history
        self.parent = parent

    def update_recent_dirs(self, recent_layout):
        """Update the recent directories display."""
        try:
            # Clear the layout
            while recent_layout.count():
                item = recent_layout.takeAt(0)
                if item.widget():
                    item.widget().deleteLater()
            # Add cards
            for directory in self.dir_history.get_directories():
                card = self.create_recent_dir_card(directory)
                recent_layout.addWidget(card)
            recent_layout.addStretch()
        except Exception as e:
            ErrorHandler.show_error(
                self.parent,
                "Error Updating Recent Directories",
                "Failed to update recent directories display",
                traceback.format_exc()
            )

    def create_recent_dir_card(self, directory: dict) -> QWidget:
        """Create a card widget for a recent directory."""
        try:
            card = QWidget()
            card.setObjectName("recent_card")
            card.setCursor(Qt.CursorShape.PointingHandCursor)

            layout = QVBoxLayout(card)
            layout.setSpacing(5)
            layout.setContentsMargins(10, 5, 10, 10)

            # Top row with delete button
            top_layout = QHBoxLayout()
            top_layout.setContentsMargins(0, 0, 0, 0)
            top_layout.addStretch()
            
            delete_btn = QPushButton()
            delete_btn.setObjectName("delete_btn")
            delete_btn.setFixedSize(18, 18)
            delete_btn.setIcon(QIcon(PathUtils.get_resource_path("ui/img/close_white.svg")))
            delete_btn.setIconSize(QSize(10, 10))
            delete_btn.setCursor(Qt.CursorShape.PointingHandCursor)
            delete_btn.clicked.connect(lambda: self.confirm_remove_recent_directory(directory["path"]))
            top_layout.addWidget(delete_btn)
            layout.addLayout(top_layout)

            # Icon / Badge Row
            icon_layout = QHBoxLayout()
            is_pid = self.is_pid_directory(directory["path"])
            
            if is_pid:
                badge = QLabel("PID")
                badge.setObjectName("recent_pid_badge")
                icon_layout.addWidget(badge)
            else:
                folder_icon = QLabel("📁")
                folder_icon.setStyleSheet(get_icon_style("20px"))
                icon_layout.addWidget(folder_icon)
            
            icon_layout.addStretch()
            layout.addLayout(icon_layout)

            # Directory name (use basename)
            dir_name = os.path.basename(directory["path"])
            name_label = QLabel(dir_name)
            name_label.setObjectName("recent_name")
            name_label.setWordWrap(True)
            layout.addWidget(name_label)

            # Date
            date_label = QLabel(directory["date"])
            date_label.setObjectName("recent_date")
            layout.addWidget(date_label)

            # Click Event
            card.mousePressEvent = lambda e: self.handle_directory_click(directory["path"])
            return card
        except Exception as e:
            ErrorHandler.show_error(self.parent, "Error", f"Failed to create card: {directory['path']}", traceback.format_exc())
            return QWidget()


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

    def confirm_remove_recent_directory(self, directory: str):
        """Confirm removal of a directory from recent directories."""
        try:
            dir_name = os.path.basename(directory)
            reply = QMessageBox.question(
                self.parent,
                "Confirm removal",
                f"Do you really want to remove '{dir_name}' from recents?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            if reply == QMessageBox.StandardButton.Yes:
                self.remove_recent_directory(directory)
        except Exception as e:
            ErrorHandler.show_error(
                self.parent,
                "Error Confirming Directory Removal",
                f"Failed to confirm removal of directory: {directory}",
                traceback.format_exc()
            )

    def remove_recent_directory(self, directory: str):
        """Remove a directory from recent directories."""
        try:
            self.dir_history.remove_directory(directory)
            if self.parent:
                self.update_recent_dirs(self.parent.recent_layout)
        except Exception as e:
            ErrorHandler.show_error(
                self.parent,
                "Error Removing Directory",
                f"Failed to remove directory from recent: {directory}",
                traceback.format_exc()
            )

    def handle_directory_click(self, directory: str):
        """Handle click on a recent directory card."""
        try:
            # Check if the directory is already loaded
            if self.parent and hasattr(self.parent, 'current_path') and self.parent.current_path == directory:
                QMessageBox.information(
                    self.parent,
                    "Directory Already Loaded",
                    f"The directory '{directory}' is already loaded.",
                    QMessageBox.StandardButton.Ok
                )
                return

            # Ask user if they want to load the directory
            reply = QMessageBox.question(
                self.parent,
                'Load Directory',
                f'Do you want to load the directory:\n{directory}?',
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No
            )

            if reply == QMessageBox.StandardButton.Yes:
                self.dir_history.add_directory(directory)
                if self.parent:
                    self.parent.load_directory(directory)
        except Exception as e:
            ErrorHandler.show_error(
                self.parent,
                "Error Loading Directory",
                f"Failed to load directory: {directory}",
                traceback.format_exc()
            )