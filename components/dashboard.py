from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                            QPushButton, QFrame, QScrollArea, QLineEdit, QTableWidget, 
                            QTableWidgetItem, QHeaderView, QAbstractItemView, QSizePolicy)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QIcon
from utils.path_utils import PathUtils
from utils.style_utils import get_title_style, get_description_style, get_separator_style, get_help_text_style, get_icon_style

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
        
        text_layout.addWidget(self.title_label)        
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
        
        title = QLabel("New Analysis")
        title.setObjectName("title_hero")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        desc = QLabel("Select a JoularJX result folder to start analysis")
        desc.setObjectName("description")
        desc.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        info_layout.addWidget(icon_label)
        info_layout.addWidget(title)
        info_layout.addWidget(desc)
        
        # Links Row
        links_layout = QHBoxLayout()
        links_layout.setSpacing(20)
        links_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        links_data = [
            ("Documentation", "https://github.com/joular/joularjx"),
            ("GitHub Repository", "https://github.com/joular/joularjx"), 
            ("Official Website", "https://www.joular.com")
        ]
        
        for text, url in links_data:
            link = QLabel(f'<a href="{url}" style="color: #6C757D; text-decoration: none;">{text}</a>')
            link.setProperty("class", "dashboard-link")
            link.setCursor(Qt.CursorShape.PointingHandCursor)
            link.setOpenExternalLinks(True)
            link.setTextFormat(Qt.TextFormat.RichText)
            
            links_layout.addWidget(link)
            if text != "Official Website":
                sep = QLabel("|")
                sep.setStyleSheet(get_separator_style())
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
        folder_icon.setObjectName("icon_large")
        select_title = QLabel("Result Folder")
        select_title.setObjectName("section_title")
        select_header.addWidget(folder_icon)
        select_header.addWidget(select_title)
        select_header.addStretch()
        
        select_help = QLabel("Select the folder containing JoularJX measurements")
        select_help.setObjectName("help_text")
        
        self.path_display = QLabel("/path/results")
        self.path_display.setObjectName("select_path_label")
        self.path_display.setMinimumHeight(40)
        
        # THE BUTTON (Prominent and Centered)
        btn_container = QHBoxLayout()
        btn_container.addStretch()
        self.browse_btn = QPushButton("   Browse folders")
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
        title_label = QLabel("Available Results")
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
        self.search_bar.setPlaceholderText("Search PID...")
        self.search_bar.textChanged.connect(self.filter_results)
        
        # Results Table
        self.results_table = QTableWidget()
        self.results_table.setColumnCount(2)
        self.results_table.setHorizontalHeaderLabels(["PID", "date"])
        self.results_table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.results_table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.results_table.setShowGrid(False)
        self.results_table.verticalHeader().setVisible(False)
        self.results_table.setAlternatingRowColors(True)
        self.results_table.setVerticalScrollMode(QAbstractItemView.ScrollMode.ScrollPerPixel)
        self.results_table.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.results_table.setMinimumHeight(400)
        self.results_table.cellClicked.connect(self.on_row_clicked)
        self.results_table.setObjectName("pid_results_table")
        
        header = self.results_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        
        results_layout.addLayout(title_row)
        results_layout.addWidget(self.search_bar)
        results_layout.addWidget(self.results_table)
        
        self.content_layout.addWidget(self.results_widget)

    def setup_recent_section(self):
        self.recent_widget = QWidget()
        recent_layout_v = QVBoxLayout(self.recent_widget)
        recent_layout_v.setContentsMargins(0, 40, 0, 0)
        recent_layout_v.setSpacing(15)
        
        recent_header = QLabel("Recent Folders")
        recent_header.setObjectName("recent_section_title")
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
        self.count_badge.setText(f"{len(pids_info)} results")
        
        for row, info in enumerate(pids_info):
            self.add_result_row(row, info)
        
        # Adjust table height based on content or keep fixed

    def add_result_row(self, row, info):
        pid, date, full_path = info
        self.results_table.insertRow(row)
        
        pid_item = QTableWidgetItem(pid)
        # Store full path in UserRole for easy access
        pid_item.setData(Qt.ItemDataRole.UserRole, full_path)
        self.results_table.setItem(row, 0, pid_item)
        
        date_item = QTableWidgetItem(date)
        date_item.setData(Qt.ItemDataRole.UserRole, full_path)
        self.results_table.setItem(row, 1, date_item)

    def on_row_clicked(self, row, column):
        """Handle row click to select PID."""
        item = self.results_table.item(row, 0)
        if item:
            full_path = item.data(Qt.ItemDataRole.UserRole)
            if full_path:
                self.pid_selected.emit(full_path)

    def filter_results(self, text):
        for row in range(self.results_table.rowCount()):
            pid = self.results_table.item(row, 0).text()
            self.results_table.setRowHidden(row, text.lower() not in pid.lower())

    def update_pid_label(self, pid):
        pass
    
    def set_selected_path(self, path):
        self.path_display.setText(path)
