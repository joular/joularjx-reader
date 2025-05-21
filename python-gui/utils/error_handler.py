from PyQt6.QtWidgets import QMessageBox

class ErrorHandler:
    @staticmethod
    def show_error(parent, title, message, details=None):
        """Displays an error dialog with an option to view details."""
        error_dialog = QMessageBox(parent)
        error_dialog.setIcon(QMessageBox.Icon.Critical)
        error_dialog.setWindowTitle(title)
        error_dialog.setText(message)
        
        if details:
            error_dialog.setDetailedText(details)
            error_dialog.setStandardButtons(QMessageBox.StandardButton.Ok)
        else:
            error_dialog.setStandardButtons(QMessageBox.StandardButton.Ok)
            
        error_dialog.exec() 