import os
import traceback
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QMessageBox
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QIcon
from utils import ErrorHandler
from datetime import datetime
from utils.path_utils import PathUtils

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
            card.setStyleSheet("""
                QWidget#recent_card {
                    background-color: #ffffff;
                    border: 1px solid #dee2e6;
                    border-radius: 8px;
                    padding: 10px;
                    min-width: 150px;
                    max-width: 200px;
                    position: relative;
                }
                QWidget#recent_card:hover {
                    border-color: #0d6efd;
                    background-color: #f8f9fa;
                }
            """)

            # Create main layout
            layout = QVBoxLayout(card)
            layout.setSpacing(5)
            layout.setContentsMargins(10, 2, 10, 10)  # Reduced top margin from 5 to 2

            # Create delete button
            delete_btn = QPushButton()
            delete_btn.setFixedSize(18, 18)
            delete_btn.setIcon(QIcon(PathUtils.get_resource_path("ui/img/close_white.svg")))
            delete_btn.setIconSize(QSize(12, 12))
            delete_btn.setStyleSheet("""
                QPushButton {
                    background-color: #dc3545;
                    border: none;
                    border-radius: 9px;
                    padding: 0px;
                    margin: 0px;
                }
                QPushButton:hover {
                    background-color: #bb2d3b;
                }
            """)
            delete_btn.setLayoutDirection(Qt.LayoutDirection.LeftToRight)
            delete_btn.clicked.connect(lambda: self.confirm_remove_recent_directory(directory["path"]))

            # Create a container for the delete button
            delete_container = QWidget()
            delete_container.setStyleSheet("background: transparent;")
            delete_layout = QHBoxLayout(delete_container)
            delete_layout.setContentsMargins(0, 0, 0, 0)
            delete_layout.addStretch()
            delete_layout.addWidget(delete_btn)

            # Add delete button container to main layout
            layout.addWidget(delete_container)

            # Check if it's a PID directory
            is_pid = self.is_pid_directory(directory["path"])
            icon_container = QWidget()
            icon_layout = QHBoxLayout(icon_container)
            # Icon and type label
            if is_pid:
                icon_layout.setContentsMargins(0, 0, 0, 0)
                icon_layout.setSpacing(5)

                # PID icon (using a different icon for PID)
                icon_label = QLabel("⚡")
                icon_label.setStyleSheet("font-size: 24px; color: #0d6efd;")
                icon_layout.addWidget(icon_label)

                # PID badge
                pid_badge = QLabel("PID")
                pid_badge.setStyleSheet("""
                    background-color: #0d6efd;
                    color: white;
                    padding: 2px 6px;
                    border-radius: 4px;
                    font-size: 10px;
                    font-weight: bold;
                """)
                icon_layout.addWidget(pid_badge)
                icon_layout.addStretch()

                layout.addWidget(icon_container)
            else:
                # Count the number of PIDs in the directory if it's NOT a PID directory
                pid_count = len([d for d in os.listdir(directory["path"]) if os.path.isdir(os.path.join(directory["path"], d))])

                # Adjust icon and count alignment
                icon_layout.setContentsMargins(0, 0, 0, 0)
                icon_layout.setSpacing(5)

                # Center the folder icon
                icon_label = QLabel("📁")
                icon_label.setStyleSheet("font-size: 26px; color: #0d6efd;")
                icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

                # PID count label
                pid_count_label = QLabel(f"{pid_count} PID(s)")
                pid_count_label.setStyleSheet("""
                    font-size: 12px;
                    color: #198754;
                    margin-left: 5px;
                """)
                pid_count_label.setAlignment(Qt.AlignmentFlag.AlignVCenter)

                # Add icon and count to the layout
                icon_layout.addWidget(icon_label)
                icon_layout.addWidget(pid_count_label)
                icon_layout.addStretch()
                layout.addWidget(icon_container)

            # Directory name (use basename)
            dir_name = os.path.basename(directory["path"])
            name_label = QLabel(dir_name)
            name_label.setStyleSheet("""
                font-size: 14px;
                font-weight: bold;
                color: #212529;
            """)
            name_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            name_label.setWordWrap(True)
            layout.addWidget(name_label)

            # Retrieve the import date from the directory dictionary
            import_date = directory["date"]

            # Add import date label
            date_label = QLabel(import_date)
            date_label.setStyleSheet("""
                font-size: 12px;
                color: #6c757d;
            """)
            date_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            layout.addWidget(date_label)

            # Add click event
            card.mousePressEvent = lambda e: self.handle_directory_click(directory["path"])

            return card
        except Exception as e:
            ErrorHandler.show_error(
                self.parent,
                "Error Creating Directory Card",
                f"Failed to create card for directory: {directory['path']}",
                traceback.format_exc()
            )
            # Return a simple widget as fallback
            fallback = QWidget()
            fallback.setMinimumHeight(100)
            return fallback

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
            if self.parent and self.parent.dir_label.text() == directory:
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