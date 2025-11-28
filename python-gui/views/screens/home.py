import os
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QPushButton, QHBoxLayout,
    QFileDialog, QLineEdit, QSpacerItem, QSizePolicy, QDialog
)
from PyQt6.QtGui import QPixmap, QFont, QCursor, QIcon
from PyQt6.QtCore import Qt
from utils.folder_validator import extract_pids_from_root
from controllers.session_controller import SessionController

class HomeScreen(QWidget):
    def __init__(self, session: SessionController, parent=None):
        super().__init__(parent)
        self.session = session

        # Appliquer le style QSS
        qss_path = os.path.join("styles", "home.qss")
        if os.path.exists(qss_path):
            with open(qss_path, "r") as f:
                self.setStyleSheet(f.read())

        self.setObjectName("HomeScreen")
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        self.setAutoFillBackground(True)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(60, 40, 60, 40)
        layout.setSpacing(25)

        # --- Logo + Title ---
        logo = QLabel()
        logo.setObjectName("logo")
        pixmap = QPixmap("./assets/icon/Logo.png")
        logo.setPixmap(pixmap.scaled(80, 80, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
        logo.setAlignment(Qt.AlignmentFlag.AlignLeft)
        layout.addWidget(logo)

        title = QLabel("JoularJX GUI")
        title.setObjectName("title")
        title.setFont(QFont("Segoe UI", 24, QFont.Weight.Bold))
        title.setAlignment(Qt.AlignmentFlag.AlignLeft)
        layout.addWidget(title)

        # --- Description ---
        desc = QLabel(
            "JoularJX is a Java-based agent for power monitoring at the source code level with support for modern Java versions and multi-OS to monitor power consumption of hardware and software."
        )
        desc.setObjectName("description")
        desc.setWordWrap(True)
        desc.setAlignment(Qt.AlignmentFlag.AlignLeft)
        layout.addWidget(desc)

        # --- Links ---
        links_container = QWidget()
        links_layout = QHBoxLayout(links_container)
        links_layout.setContentsMargins(0, 0, 0, 0)
        links_layout.setSpacing(6)

        link_items = [
            ("Documentation", "https://example.com/doc"),
            ("GitHub Repository", "https://github.com/example"),
            ("Official Website", "https://joularjx.org")
        ]

        for i, (text, url) in enumerate(link_items):
            link = QLabel(f"<a href='{url}'>{text}</a>")
            link.setObjectName("link")
            link.setOpenExternalLinks(True)
            link.setAlignment(Qt.AlignmentFlag.AlignLeft)
            link.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
            links_layout.addWidget(link)

            if i < len(link_items) - 1:
                separator = QLabel("|")
                separator.setStyleSheet("color: #999999; font-size: 13px;")
                separator.setAlignment(Qt.AlignmentFlag.AlignLeft)
                links_layout.addWidget(separator)

        links_container.setSizePolicy(QSizePolicy.Policy.Maximum, QSizePolicy.Policy.Preferred)
        layout.addWidget(links_container, alignment=Qt.AlignmentFlag.AlignLeft)

        # --- Folder selection prompt ---
        folder_label = QLabel("Let's start by selecting the 'joularjx-result' folder.")
        folder_label.setObjectName("folder_prompt")
        folder_label.setAlignment(Qt.AlignmentFlag.AlignLeft)
        layout.addWidget(folder_label)

        # --- Folder path + button ---
        folder_row = QHBoxLayout()
        folder_row.setSpacing(10)

        self.folder_path = QLineEdit("C:/joularjx/joularjx-result")
        self.folder_path.setObjectName("folder_path")
        folder_row.addWidget(self.folder_path)

        select_button = QPushButton("Select folder")
        select_button.setObjectName("select_button")
        select_button.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        select_button.clicked.connect(self.select_folder)
        folder_row.addWidget(select_button)

        layout.addLayout(folder_row)

        # --- Start analysis button ---
        start_button = QPushButton("Start analysis")
        start_button.setObjectName("start_button")
        start_button.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        start_button.setFixedHeight(40)
        start_button.clicked.connect(self.start_analysis)
        layout.addWidget(start_button, alignment=Qt.AlignmentFlag.AlignCenter)

        # --- Spacer ---
        layout.addSpacerItem(QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding))

        # --- Footer ---
        footer = QLabel(
            "Version 0.9.0 beta\n"
            "This program is licensed under the GNU GPL 3 license (only GPL-3.0). Copyright (c) 2021-2023. "
            "Axel Nourdine, Université du Petit au Pays de l'Adour. All rights reserved.\n"
            "This program is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License version 3, as published by the Free Software Foundation.\n"
            "<a href='https://www.gnu.org/licenses/gpl-3.0.html'>https://www.gnu.org/licenses/gpl-3.0.html</a>"
        )
        footer.setObjectName("footer")
        footer.setOpenExternalLinks(True)
        footer.setWordWrap(True)
        footer.setAlignment(Qt.AlignmentFlag.AlignLeft)
        layout.addWidget(footer)

    def select_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Select joularjx-result folder")
        if folder:
            self.folder_path.setText(folder)

    def show_custom_error_dialog(self, title: str, message: str):
        dialog = QDialog(self)
        dialog.setWindowTitle(title)
        dialog.setFixedSize(400, 160)
        dialog.setStyleSheet("""
            QDialog {
                background-color: #ffffff;
                font-family: "Segoe UI", sans-serif;
                font-size: 13px;
                color: #333333;
            }
            QLabel#error_icon {
                min-width: 32px;
                max-width: 32px;
            }
            QLabel#error_text {
                padding: 0px;
            }
            QPushButton#ok_button {
                background-color: #007acc;
                color: white;
                padding: 6px 12px;
                border-radius: 4px;
                font-size: 13px;
                min-width: 80px;
            }
            QPushButton#ok_button:hover {
                background-color: #005f99;
            }
        """)

        layout = QVBoxLayout(dialog)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        # Icon + message
        row = QHBoxLayout()
        icon_label = QLabel()
        icon_label.setObjectName("error_icon")
        icon_label.setPixmap(QIcon.fromTheme("dialog-error").pixmap(32, 32))
        row.addWidget(icon_label)

        text_label = QLabel(message)
        text_label.setObjectName("error_text")
        text_label.setWordWrap(True)
        text_label.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        row.addWidget(text_label)

        layout.addLayout(row)

        # OK button
        ok_button = QPushButton("OK")
        ok_button.setObjectName("ok_button")
        ok_button.clicked.connect(dialog.accept)
        layout.addWidget(ok_button, alignment=Qt.AlignmentFlag.AlignRight)

        dialog.exec()

    def start_analysis(self):
        folder = self.folder_path.text().strip()
        pids = extract_pids_from_root(folder)
        if not pids:
            self.show_custom_error_dialog("Invalid Folder", "The selected folder is invalid. Please ensure that your folder contains PIDs in its root directory.")
        else:
            self.session.set_folder(folder, pids)
            # Tu peux ici déclencher une navigation ou un signal si nécessaire
