# main.py
import sys
import os
from PyQt6.QtWidgets import QApplication
from models.app_model import AppModel
from views.main_window import MainWindow
from controllers.main_controller import MainController

def load_style(app):
    # prefer style.qss, fallback to style.css
    for fname in ("style.qss", "style.css"):
        if os.path.exists(fname):
            with open(fname, "r", encoding="utf-8") as f:
                app.setStyleSheet(f.read())
            return

def main():
    app = QApplication(sys.argv)
    load_style(app)

    window = MainWindow()
    model = AppModel()
    controller = MainController(window, model)

    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
