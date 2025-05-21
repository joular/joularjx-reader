from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                            QScrollArea, QFrame, QWidget, QPushButton, QProgressBar)
from PyQt6.QtCore import Qt, QObject, QSize
from PyQt6.QtGui import QFont

class BoxEventFilter(QObject):
    def __init__(self, parent, box, method):
        super().__init__(parent)
        self.box = box
        self.method = method
        
    def eventFilter(self, obj, event):
        if obj is self.box and event.type() == event.Type.MouseButtonPress:
            parent = self.parent()
            while parent is not None and not hasattr(parent, "show_method_evolution"):
                parent = parent.parent()
            if parent is not None and hasattr(parent, "show_method_evolution"):
                parent.show_method_evolution(self.method)
            else:
                window = self.box.window()
                if hasattr(window, "show_method_evolution"):
                    window.show_method_evolution(self.method)
        return super().eventFilter(obj, event)

class CallTreeDetailsDialog(QDialog):
    def __init__(self, calltree, current_pid, parent=None):
        super().__init__(parent)
        self.calltree = calltree
        self.current_pid = current_pid
        self.setup_ui()
        
    def setup_ui(self):
        """Setup the UI components."""
        self.setWindowTitle(f"Call Tree Details - {self.calltree.name}")
        self.setMinimumSize(800, 600)
        self.setStyleSheet("background-color: #FFFFFF;")
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)
        
        # Add PID name and title section
        pid_label = QLabel(f"PID: {self.current_pid}")
        pid_label.setStyleSheet("""
            font-size: 14px;
            color: #6c757d;
        """)
        
        title_label = QLabel("Calltree's branch (from the parent to the last child)")
        title_label.setStyleSheet("""
            font-size: 22px;
            font-weight: bold;
            color: #212529;
        """)
        
        header_layout = QVBoxLayout()
        header_layout.addWidget(pid_label)
        header_layout.addWidget(title_label)
        layout.addLayout(header_layout)
        
        # Create a scroll area for the hierarchy visualization
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setFrameShape(QFrame.Shape.NoFrame)
        scroll_area.setStyleSheet("background-color: #FFFFFF;")
        
        scroll_content = QWidget()
        scroll_content.setStyleSheet("background-color: #FFFFFF;")
        scroll_layout = QVBoxLayout(scroll_content)
        scroll_layout.setSpacing(5)
        scroll_layout.setContentsMargins(0, 0, 0, 0)
        scroll_layout.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        
        # Parse method names from the calltree
        method_names = self.calltree.name.split(';')
        method_count = len(method_names)
        
        # Create the hierarchical visualization
        for i, method_name in enumerate(method_names):
            # Determine if this is the last child
            is_last_child = (i == method_count - 1)
            
            # Find the corresponding Method object
            corresponding_method = None
            for method in self.calltree.methods:
                if method.name == method_name:
                    corresponding_method = method
                    break
            
            # Create the method box with proper styling
            method_box = QLabel(method_name)
            method_box.setAlignment(Qt.AlignmentFlag.AlignCenter)
            method_box.setMinimumWidth(500)
            method_box.setMinimumHeight(40)
            
            # Style based on position in hierarchy
            if is_last_child:
                # Green for last child method
                method_box.setStyleSheet("""
                    background-color: #86EFC5;
                    color: black;
                    border-radius: 15px;
                    padding: 10px 20px;
                    font-size: 14px;
                """)
            else:
                # Blue for all other methods
                method_box.setStyleSheet("""
                    background-color: #5D5FEF;
                    color: white;
                    border-radius: 15px;
                    padding: 10px 20px;
                    font-size: 14px;
                """)
            
            # Add the method box to the layout
            scroll_layout.addWidget(method_box, 0, Qt.AlignmentFlag.AlignHCenter)
            
            # Add minimal spacing between methods
            if not is_last_child:
                spacer = QWidget()
                spacer.setFixedHeight(10)
                scroll_layout.addWidget(spacer, 0, Qt.AlignmentFlag.AlignHCenter)
            
            # Make label clickable if there's a corresponding method
            if corresponding_method:
                method_box.setCursor(Qt.CursorShape.PointingHandCursor)
                event_filter = BoxEventFilter(self, method_box, corresponding_method)
                method_box.installEventFilter(event_filter)
                method_box.event_filter = event_filter
        
        # Add spacer at the bottom
        scroll_layout.addStretch()
        
        # Set the scroll content
        scroll_area.setWidget(scroll_content)
        layout.addWidget(scroll_area)
        
        # Method Power Consumption Section
        consumption_frame = QFrame()
        consumption_frame.setFrameShape(QFrame.Shape.NoFrame)
        consumption_frame.setStyleSheet("""
            border-radius: 4px;
            background-color: #FFFFFF;
        """)
        
        consumption_layout = QVBoxLayout(consumption_frame)
        
        consumption_title = QLabel("Method Power consumption")
        consumption_title.setStyleSheet("""
            font-size: 16px;
            font-weight: bold;
            color: #212529;
            padding: 10px;
        """)
        consumption_layout.addWidget(consumption_title)
        
        # Show consumption data for the entire calltree
        consumption_value = self.calltree.consumption
        percentage_value = self.calltree.percentage
        
        # Method entry container
        method_entry = QWidget()
        method_entry.setStyleSheet("""
            background-color: #86EFC5;
            border-radius: 4px;
        """)
        entry_layout = QHBoxLayout(method_entry)
        entry_layout.setContentsMargins(10, 5, 10, 5)
        
        # Lightning bolt icon
        icon_label = QLabel("⚡")
        icon_label.setStyleSheet("color: #000000; font-size: 16px;")
        entry_layout.addWidget(icon_label)
        
        # Full calltree name
        full_name = self.calltree.name
        display_name = full_name
        if len(full_name) > 40:
            display_name = full_name[:37] + "[..]"
        
        name_label = QLabel(display_name)
        name_label.setStyleSheet("color: #000000; font-size: 14px;")
        name_label.setWordWrap(True)
        name_label.setToolTip(full_name)
        entry_layout.addWidget(name_label)
        
        # Progress bar in a widget with layout for proper stretching
        progress_widget = QWidget()
        progress_layout = QHBoxLayout(progress_widget)
        progress_layout.setContentsMargins(0, 0, 0, 0)
        progress_layout.setSpacing(0)
        progress_bar = QProgressBar()
        progress_bar.setValue(int(percentage_value))
        progress_bar.setMaximum(100)
        progress_bar.setFixedHeight(10)
        progress_bar.setStyleSheet("""
            QProgressBar {
                border: none;
                background-color: #ffffff;
                border-radius: 4px;
                text-align: center;
                margin: 0px;
                min-height: 10px;
                max-height: 10px;
            }
            QProgressBar::chunk {
                background-color: #5d9cec;
                border-radius: 4px;
                min-height: 10px;
                max-height: 10px;
            }
        """)
        progress_bar.setTextVisible(False)
        progress_layout.addWidget(progress_bar)
        # Label for consumption value
        cons_label = QLabel(f"{consumption_value:.3f} J ({percentage_value:.2f}%)")
        cons_label.setStyleSheet("color: #000000; font-size: 14px;")
        cons_label.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        progress_layout.addWidget(cons_label)
        entry_layout.addWidget(progress_widget, 1)
        
        consumption_layout.addWidget(method_entry)
        
        layout.addWidget(consumption_frame)
        
        # Close button
        close_button = QPushButton("Close")
        close_button.setStyleSheet("""
            background-color: #0d6efd;
            color: white;
            border: none;
            padding: 8px 16px;
            border-radius: 4px;
            font-weight: bold;
        """)
        close_button.clicked.connect(self.accept)
        close_button.setFixedWidth(120)
        
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        button_layout.addWidget(close_button)
        button_layout.addStretch()
        layout.addLayout(button_layout) 