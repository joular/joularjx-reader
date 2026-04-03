from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                            QPushButton, QFrame, QScrollArea, QLineEdit, QTableWidget, 
                            QTableWidgetItem, QHeaderView, QAbstractItemView, QSizePolicy,
                            QGraphicsDropShadowEffect)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QIcon, QColor, QFont
import sys
from utils.path_utils import PathUtils
from utils.style_utils import get_title_style, get_description_style, get_separator_style, get_help_text_style, get_icon_style
from utils.os_config import OSConfig

TableBaseClass = OSConfig.get_table_widget_class()


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
        self.main_layout.setContentsMargins(30, 20, 30, 20)
        self.main_layout.setSpacing(15)
        
        # Header Section
        self.setup_header()
        
        # Scroll area
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll.setObjectName("dashboard_scroll")
        
        self.content_container = QWidget()
        self.content_container.setObjectName("content_container")
        self.content_layout = QHBoxLayout(self.content_container)
        self.content_layout.setContentsMargins(0, 0, 0, 0)
        self.content_layout.setSpacing(20)
        scroll.setWidget(self.content_container)
        self.main_layout.addWidget(scroll)
        
        # Left Column
        self.left_column = QWidget()
        self.left_layout = QVBoxLayout(self.left_column)
        self.left_layout.setContentsMargins(0, 0, 0, 0)
        self.setup_action_card()
        self.content_layout.addWidget(self.left_column, stretch=40)
        self.left_column.setMinimumWidth(380)
        
        # Right Column
        self.right_column = QWidget()
        self.right_layout = QVBoxLayout(self.right_column)
        self.right_layout.setContentsMargins(0, 0, 0, 0)
        self.right_layout.setSpacing(15)
        
        # Available Results Section (Hidden by default)
        self.setup_results_section()
        
        # Recent Section (Fallback/Initial)
        self.setup_recent_section()
        
        self.content_layout.addWidget(self.right_column, stretch=60)


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
        # Action Card Container
        self.action_card = QFrame()
        self.action_card.setObjectName("action_card")
        self.action_card.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        
        card_layout = QVBoxLayout(self.action_card)
        card_layout.setContentsMargins(20, 20, 20, 20)
        card_layout.setSpacing(10)
        card_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Icon & Title Area
        info_layout = QVBoxLayout()
        info_layout.setSpacing(5)
        info_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        icon_label = QLabel()
        icon_label.setPixmap(QIcon(PathUtils.get_resource_path('ui/img/joularjx.png')).pixmap(120, 120)) # Increased to 120x120
        icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        title = QLabel("New Analysis")
        title.setObjectName("title_hero")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        desc = QLabel("Select a JoularJX result folder to start analysis")
        desc.setObjectName("description")
        desc.setAlignment(Qt.AlignmentFlag.AlignCenter)
        desc.setWordWrap(False)
        
        info_layout.addWidget(icon_label)
        info_layout.addWidget(title)
        info_layout.addWidget(desc)
        
        # Links Row
        links_layout = QHBoxLayout()
        links_layout.setSpacing(10)
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
        
        self.select_frame = QFrame()
        self.select_frame.setObjectName("select_folder_frame")
        select_layout = QVBoxLayout(self.select_frame)
        select_layout.setContentsMargins(10, 10, 10, 10)
        select_layout.setSpacing(10)
        
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
        self.path_display.setMinimumHeight(30)
        
        # THE BUTTON (Prominent and Centered)
        btn_container = QHBoxLayout()
        btn_container.addStretch()
        self.browse_btn = QPushButton("   Browse folders")
        self.browse_btn.setObjectName("browse_btn")
        self.browse_btn.setFixedWidth(260)
        self.browse_btn.setFixedHeight(40)
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
        
        self.left_layout.addWidget(self.action_card)
        
    def setup_results_section(self):
        self.results_widget = QWidget()
        self.results_widget.setVisible(False)
        self.results_widget.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        results_layout = QVBoxLayout(self.results_widget)
        results_layout.setContentsMargins(0, 0, 0, 0)
        results_layout.setSpacing(12)
        
        # Title Row
        title_row = QHBoxLayout()
        title_label = QLabel("Available Results")
        title_label.setObjectName("results_title")
        
        self.count_badge = QLabel("0")
        self.count_badge.setObjectName("results_count_badge")
        
        title_row.addWidget(title_label)
        title_row.addSpacing(10)
        title_row.addWidget(self.count_badge)
        title_row.addStretch()
        
        results_layout.addLayout(title_row)
        
        # Subtitle
        subtitle = QLabel("Select an analysis to view detailed results")
        subtitle.setObjectName("results_subtitle")
        results_layout.addWidget(subtitle)
        
        # Search Bar with icon
        search_container = QHBoxLayout()
        search_container.setSpacing(0)
        self.search_bar = QLineEdit()
        self.search_bar.setObjectName("pid_search_bar")
        self.search_bar.setPlaceholderText("🔍  Search by PID...")
        self.search_bar.textChanged.connect(self.filter_results)
        search_container.addWidget(self.search_bar)
        results_layout.addLayout(search_container)
        
        # Scrollable cards area
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll.setObjectName("results_scroll")
        
        self.results_cards_container = QWidget()
        self.results_cards_container.setObjectName("results_cards_container")
        self.results_cards_layout = QVBoxLayout(self.results_cards_container)
        self.results_cards_layout.setContentsMargins(0, 0, 4, 0)
        self.results_cards_layout.setSpacing(8)
        self.results_cards_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        
        scroll.setWidget(self.results_cards_container)
        results_layout.addWidget(scroll)
        
        self.right_layout.addWidget(self.results_widget)
        
    def setup_recent_section(self):
        self.recent_widget = QWidget()
        self.recent_widget.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        recent_layout_v = QVBoxLayout(self.recent_widget)
        recent_layout_v.setContentsMargins(0, 0, 0, 0)
        recent_layout_v.setSpacing(12)
        
        # Header row with title and subtitle
        recent_header = QLabel("Recent Folders")
        recent_header.setObjectName("recent_section_title")
        recent_layout_v.addWidget(recent_header)
        
        recent_subtitle = QLabel("Pick up where you left off")
        recent_subtitle.setObjectName("recent_section_subtitle")
        recent_layout_v.addWidget(recent_subtitle)
        
        self.recent_container = QWidget()
        self.recent_layout = QVBoxLayout(self.recent_container)
        self.recent_layout.setContentsMargins(0, 0, 0, 0)
        self.recent_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.recent_layout.setSpacing(8)

        recent_layout_v.addWidget(self.recent_container)
        recent_layout_v.addStretch()
        
        self.right_layout.addWidget(self.recent_widget)

    def set_results_visible(self, visible: bool):
        self.results_widget.setVisible(visible)
        self.recent_widget.setVisible(not visible)

    def update_results(self, pids_info):
        """ Populate the results with styled cards. pids_info: list of (pid, date, full_path) """
        # Clear existing cards
        while self.results_cards_layout.count():
            item = self.results_cards_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        
        self.all_results = pids_info
        self.count_badge.setText(f"{len(pids_info)} result{'s' if len(pids_info) != 1 else ''}")
        
        for info in pids_info:
            card = self._create_result_card(info)
            self.results_cards_layout.addWidget(card)
    
    def _create_result_card(self, info):
        """Create a styled card for a PID result."""
        pid, date, full_path = info
        
        card = QFrame()
        card.setObjectName("pid_result_card")
        card.setCursor(Qt.CursorShape.PointingHandCursor)
        card.setProperty("full_path", full_path)
        
        card_layout = QHBoxLayout(card)
        card_layout.setContentsMargins(14, 12, 14, 12)
        card_layout.setSpacing(12)
        
        # PID icon/badge
        pid_icon = QLabel("⚡")
        pid_icon.setObjectName("pid_card_icon")
        pid_icon.setFixedSize(36, 36)
        pid_icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
        card_layout.addWidget(pid_icon)
        
        # Info column
        info_layout = QVBoxLayout()
        info_layout.setSpacing(2)
        info_layout.setContentsMargins(0, 0, 0, 0)
        
        # Extract just the PID number for a cleaner display
        pid_display = pid.split('-')[0] if '-' in pid else pid
        pid_label = QLabel(f"PID {pid_display}")
        pid_label.setObjectName("pid_card_title")
        
        date_label = QLabel(date)
        date_label.setObjectName("pid_card_date")
        
        info_layout.addWidget(pid_label)
        info_layout.addWidget(date_label)
        card_layout.addLayout(info_layout, stretch=1)
        
        # Arrow indicator
        arrow = QLabel("›")
        arrow.setObjectName("pid_card_arrow")
        arrow.setAlignment(Qt.AlignmentFlag.AlignCenter)
        card_layout.addWidget(arrow)
        
        # Make the card clickable via mouse press event
        card.mousePressEvent = lambda event, path=full_path: self.pid_selected.emit(path)
        
        return card

    def filter_results(self, text):
        for i in range(self.results_cards_layout.count()):
            widget = self.results_cards_layout.itemAt(i).widget()
            if widget:
                # Search in the PID title label
                labels = widget.findChildren(QLabel)
                pid_text = ""
                for label in labels:
                    if label.objectName() == "pid_card_title":
                        pid_text = label.text()
                        break
                widget.setVisible(text.lower() in pid_text.lower())

    def update_pid_label(self, pid):
        pass
    
    def set_selected_path(self, path):
        metrics = self.path_display.fontMetrics()
        elided_path = metrics.elidedText(path, Qt.TextElideMode.ElideMiddle, 300) 
        self.path_display.setText(elided_path)
        self.path_display.setToolTip(path)
