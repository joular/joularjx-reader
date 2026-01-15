from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                            QPushButton, QFrame, QScrollArea, QLineEdit, QTableWidget, 
                            QTableWidgetItem, QHeaderView, QAbstractItemView)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QIcon
from utils.path_utils import PathUtils

class DashboardWidget(QWidget):
    """ Enhanced Dashboard matching Figma mockup with conditional results. """
    
    # Signal to request loading a specific PID path
    pid_selected = pyqtSignal(str)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("dashboard")
        self.setup_ui()

    def setup_ui(self):
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(50, 40, 50, 40)
        self.main_layout.setSpacing(20)
        
        # Header Section
        self.setup_header()
        
        # Scroll area
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setObjectName("dashboard_scroll")
        
        self.content_container = QWidget()
        self.content_container.setObjectName("content_container")
        self.content_layout = QVBoxLayout(self.content_container)
        self.content_layout.setContentsMargins(0, 0, 0, 0)
        self.content_layout.setSpacing(30)
        scroll.setWidget(self.content_container)
        self.main_layout.addWidget(scroll)
        
        # Action Card (New Analyse)
        self.setup_action_card()
        
        # Available Results Section (Hidden by default)
        self.setup_results_section()
        
        # Recent Section (Fallback/Initial)
        self.setup_recent_section()


    def setup_header(self):
        # Header Container
        self.header_widget = QWidget()
        header_layout = QHBoxLayout(self.header_widget)
        header_layout.setContentsMargins(0, 0, 0, 0)
        header_layout.setSpacing(10)
        
        # Left Text
        text_layout = QVBoxLayout()
        text_layout.setSpacing(5)
        
        self.title_label = QLabel("JoularJX Dashboard")
        self.title_label.setObjectName("dashboard_title")
        
        self.subtitle_label = QLabel("Prêt pour une nouvelle analyse")
        self.subtitle_label.setObjectName("dashboard_subtitle")
        
        text_layout.addWidget(self.title_label)
        text_layout.addWidget(self.subtitle_label)
        
        header_layout.addLayout(text_layout)
        header_layout.addStretch()
        
        self.main_layout.addWidget(self.header_widget)




    def setup_action_card(self):
        # Centering Layout
        outer_container = QVBoxLayout()
        outer_container.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        card_center_h = QHBoxLayout()
        card_center_h.addStretch()
        
        self.action_card = QFrame()
        self.action_card.setObjectName("action_card")
        self.action_card.setFixedWidth(720)
        
        card_layout = QVBoxLayout(self.action_card)
        card_layout.setContentsMargins(40, 40, 40, 40)
        card_layout.setSpacing(30)
        card_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Icon & Title Area
        info_layout = QVBoxLayout()
        info_layout.setSpacing(10)
        info_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        icon_label = QLabel()
        icon_label.setPixmap(QIcon(PathUtils.get_resource_path('ui/img/logo.png')).pixmap(90, 90))
        icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        title = QLabel("Nouvelle Analyse")
        title.setStyleSheet("font-size: 30px; font-weight: 800; color: #1A1D21;")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        desc = QLabel("Sélectionnez un dossier de résultats JoularJX pour commencer l'analyse")
        desc.setStyleSheet("font-size: 15px; color: #64748B;")
        desc.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        info_layout.addWidget(icon_label)
        info_layout.addWidget(title)
        info_layout.addWidget(desc)
        
        # Links Row
        links_layout = QHBoxLayout()
        links_layout.setSpacing(20)
        links_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        for text in ["Documentation", "GitHub Repository", "Official Website"]:
            link = QLabel(text)
            link.setProperty("class", "dashboard-link")
            link.setCursor(Qt.CursorShape.PointingHandCursor)
            links_layout.addWidget(link)
            if text != "Official Website":
                sep = QLabel("|")
                sep.setStyleSheet("color: #E2E8F0;")
                links_layout.addWidget(sep)
        
        # Selection Frame (The box matching Figma)
        self.select_frame = QFrame()
        self.select_frame.setObjectName("select_folder_frame")
        select_layout = QVBoxLayout(self.select_frame)
        select_layout.setContentsMargins(25, 25, 25, 25)
        select_layout.setSpacing(15)
        
        # Folder Header
        select_header = QHBoxLayout()
        folder_icon = QLabel("📁")
        folder_icon.setStyleSheet("font-size: 18px;")
        select_title = QLabel("Dossier de résultats")
        select_title.setStyleSheet("font-weight: 700; font-size: 15px; color: #1E293B;")
        select_header.addWidget(folder_icon)
        select_header.addWidget(select_title)
        select_header.addStretch()
        
        select_help = QLabel("Sélectionnez le dossier contenant les mesures JoularJX")
        select_help.setStyleSheet("font-size: 14px; color: #64748B;")
        
        self.path_display = QLabel("/path/results")
        self.path_display.setObjectName("select_path_label")
        self.path_display.setMinimumHeight(40)
        
        # THE BUTTON (Prominent and Centered)
        btn_container = QHBoxLayout()
        btn_container.addStretch()
        self.browse_btn = QPushButton("   Parcourir les dossiers")
        self.browse_btn.setObjectName("browse_btn")
        self.browse_btn.setFixedWidth(280)
        self.browse_btn.setFixedHeight(50)
        self.browse_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_container.addWidget(self.browse_btn)
        btn_container.addStretch()
        
        select_layout.addLayout(select_header)
        select_layout.addWidget(select_help)
        select_layout.addWidget(self.path_display)
        select_layout.addLayout(btn_container)
        
        # Assemble Card
        card_layout.addLayout(info_layout)
        card_layout.addLayout(links_layout)
        card_layout.addWidget(self.select_frame)
        
        card_center_h.addWidget(self.action_card)
        card_center_h.addStretch()
        
        outer_container.addLayout(card_center_h)
        self.content_layout.addLayout(outer_container)

    def setup_results_section(self):
        self.results_widget = QWidget()
        self.results_widget.setVisible(False)
        results_layout = QVBoxLayout(self.results_widget)
        results_layout.setContentsMargins(0, 40, 0, 0)
        results_layout.setSpacing(20)
        
        # Title Row
        title_row = QHBoxLayout()
        title_label = QLabel("Résultats disponibles")
        title_label.setObjectName("results_title")
        
        self.count_badge = QLabel("0 résultats")
        self.count_badge.setObjectName("results_count_badge")
        
        title_row.addWidget(title_label)
        title_row.addSpacing(15)
        title_row.addWidget(self.count_badge)
        title_row.addStretch()
        
        # Search Bar
        self.search_bar = QLineEdit()
        self.search_bar.setObjectName("pid_search_bar")
        self.search_bar.setPlaceholderText("Rechercher un PID...")
        self.search_bar.textChanged.connect(self.filter_results)
        
        # Results Table
        self.results_table = QTableWidget()
        self.results_table.setColumnCount(3)
        self.results_table.setHorizontalHeaderLabels(["PID", "date", "Actions"])
        self.results_table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.results_table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.results_table.setShowGrid(False)
        self.results_table.verticalHeader().setVisible(False)
        
        header = self.results_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Fixed)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.Fixed)
        self.results_table.setColumnWidth(1, 250)
        self.results_table.setColumnWidth(2, 200)
        self.results_table.setFixedHeight(400) # Initial height
        
        results_layout.addLayout(title_row)
        results_layout.addWidget(self.search_bar)
        results_layout.addWidget(self.results_table)
        
        self.content_layout.addWidget(self.results_widget)

    def setup_recent_section(self):
        self.recent_widget = QWidget()
        recent_layout_v = QVBoxLayout(self.recent_widget)
        recent_layout_v.setContentsMargins(0, 40, 0, 0)
        recent_layout_v.setSpacing(15)
        
        recent_header = QLabel("Dossiers Récents")
        recent_header.setStyleSheet("font-size: 18px; font-weight: bold; color: #212529;")
        recent_layout_v.addWidget(recent_header)
        
        self.recent_layout = QHBoxLayout()
        self.recent_layout.setAlignment(Qt.AlignmentFlag.AlignLeft)
        
        recent_container = QWidget()
        recent_container.setLayout(self.recent_layout)
        
        self.recent_scroll = QScrollArea()
        self.recent_scroll.setWidgetResizable(True)
        self.recent_scroll.setFixedHeight(180)
        self.recent_scroll.setFrameShape(QFrame.Shape.NoFrame)
        self.recent_scroll.setWidget(recent_container)
        
        recent_layout_v.addWidget(self.recent_scroll)
        self.content_layout.addWidget(self.recent_widget)

    def set_results_visible(self, visible: bool):
        self.results_widget.setVisible(visible)
        self.recent_widget.setVisible(not visible)

    def update_results(self, pids_info):
        """ Populate the results table. pids_info: list of (pid, date, full_path) """
        self.results_table.setRowCount(0)
        self.all_results = pids_info
        self.count_badge.setText(f"{len(pids_info)} résultats")
        
        for row, info in enumerate(pids_info):
            self.add_result_row(row, info)
        
        # Adjust table height based on content or keep fixed
        self.results_table.setFixedHeight(min(400, len(pids_info) * 60 + 50))

    def add_result_row(self, row, info):
        pid, date, full_path = info
        self.results_table.insertRow(row)
        
        pid_item = QTableWidgetItem(pid)
        self.results_table.setItem(row, 0, pid_item)
        
        date_item = QTableWidgetItem(date)
        self.results_table.setItem(row, 1, date_item)
        
        # Action Button
        btn = QPushButton("Voir détails >")
        btn.setObjectName("view_details_btn")
        btn.setCursor(Qt.CursorShape.PointingHandCursor)
        btn.clicked.connect(lambda: self.pid_selected.emit(full_path))
        self.results_table.setCellWidget(row, 2, btn)

    def filter_results(self, text):
        for row in range(self.results_table.rowCount()):
            pid = self.results_table.item(row, 0).text()
            self.results_table.setRowHidden(row, text.lower() not in pid.lower())

    def update_pid_label(self, pid):
        self.subtitle_label.setText(f"PID : {pid}")
    
    def set_selected_path(self, path):
        self.path_display.setText(path)
