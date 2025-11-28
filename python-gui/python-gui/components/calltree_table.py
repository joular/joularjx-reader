from PyQt6.QtWidgets import (QTableWidget, QTableWidgetItem, QHeaderView, 
                            QProgressBar, QWidget, QHBoxLayout, QAbstractItemView)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
import pyqtgraph as pg
from utils.style_utils import get_progress_color, get_table_style, get_header_style, get_progress_bar_style

class CallTreeTable(QTableWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_table()
        self.current_calltrees = []
        
    def setup_table(self):
        """Configure the table's basic settings."""
        # Set column count and headers
        self.setColumnCount(4)
        self.setHorizontalHeaderLabels(["Call Tree", "Consumption", "Percentage", "Progress"])
        
        # Configure headers
        header = self.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Fixed)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.Fixed)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.Stretch)
        
        # Set specific widths for numeric columns
        self.setColumnWidth(1, 120)
        self.setColumnWidth(2, 100)
        
        # Configure headers style
        header.setDefaultAlignment(Qt.AlignmentFlag.AlignLeft)
        header.setStyleSheet(get_header_style())
        
        # Set table style
        self.setStyleSheet(get_table_style())
        
        # Set minimum column widths
        self.horizontalHeader().setMinimumSectionSize(100)
        
        # Masquer la colonne d'index à gauche
        self.verticalHeader().setVisible(False)
        # Masquer l'en-tête de colonne
        self.horizontalHeader().setVisible(False)
        # Sélectionner toute la ligne au clic
        self.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        
    def update_calltrees(self, calltrees):
        """Update the table with new calltrees data."""
        self.setRowCount(0)
        self.current_calltrees = calltrees
        
        # Sort calltrees by percentage in descending order
        calltrees.sort(key=lambda x: x.percentage, reverse=True)
        
        # Display sorted calltrees
        for row, calltree in enumerate(calltrees):
            self.insertRow(row)
            
            # Set alternating row colors
            bg_color = "#f8f9fa" if row % 2 == 0 else "#ffffff"
            
            # Name column
            name = calltree.name
            if len(name) > 40:
                name = name[:37] + "[..]"
            name_item = QTableWidgetItem(f"⚡ {name}")
            name_item.setFlags(name_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            name_item.setTextAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
            name_item.setBackground(pg.mkColor(bg_color))
            name_item.setFont(QFont("Arial", 12))
            name_item.setToolTip(calltree.name)
            self.setItem(row, 0, name_item)
            
            # Consumption column
            consumption_text = f"{calltree.consumption:.4f} J"
            consumption_item = QTableWidgetItem(consumption_text)
            consumption_item.setFlags(consumption_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            consumption_item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            consumption_item.setBackground(pg.mkColor(bg_color))
            consumption_item.setFont(QFont("Arial", 12))
            self.setItem(row, 1, consumption_item)
            
            # Percentage column
            percentage_text = f"{calltree.percentage:.2f}%"
            percentage_item = QTableWidgetItem(percentage_text)
            percentage_item.setFlags(percentage_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            percentage_item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            percentage_item.setBackground(pg.mkColor(bg_color))
            percentage_item.setFont(QFont("Arial", 12))
            self.setItem(row, 2, percentage_item)
            
            # Progress bar column
            progress_bar = QProgressBar()
            percentage_value = int(calltree.percentage)
            progress_bar.setValue(percentage_value)
            progress_bar.setMaximum(100)
            progress_bar.setFixedHeight(10)
            
            bar_color = get_progress_color(percentage_value)
            progress_bar.setStyleSheet(get_progress_bar_style(bar_color))
            progress_bar.setTextVisible(False)
            
            progress_widget = QWidget()
            progress_layout = QHBoxLayout(progress_widget)
            progress_layout.setContentsMargins(0, 0, 0, 0)
            progress_layout.setSpacing(0)
            progress_layout.addWidget(progress_bar)
            progress_widget.setStyleSheet(f"background-color: {bg_color}; min-height: 10px; max-height: 10px;")
            
            self.setCellWidget(row, 3, progress_widget)
            
    def filter_calltrees(self, text):
        """Filter calltrees based on search text."""
        for row in range(self.rowCount()):
            calltree_name = self.item(row, 0).text()
            self.setRowHidden(row, text.lower() not in calltree_name.lower())
            
    def get_selected_calltree(self):
        """Get the currently selected calltree."""
        selected_items = self.selectedItems()
        if selected_items and self.current_calltrees:
            row = selected_items[0].row()
            return self.current_calltrees[row]
        return None 