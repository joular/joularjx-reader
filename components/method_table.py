from PyQt6.QtWidgets import (QTableWidget, QTableWidgetItem, QHeaderView, 
                            QProgressBar, QWidget, QHBoxLayout, QAbstractItemView)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont
import pyqtgraph as pg
import numpy as np

from ui.widgets import CheckBox, TableWidget
from utils.style_utils import (get_progress_color, 
                               get_progress_bar_style, get_cell_widget_style,
                               get_color_indicator_style, get_total_color_indicator_style,
                               get_progress_wrapper_style)
from utils.style_constants import (
    COLOR_BG_SELECTION, COLOR_BG_LIGHT, COLOR_BG_WHITE, 
    COLOR_TOTAL_BG, COLOR_BORDER_CELL_BOTTOM, COLOR_BORDER_CELL_RIGHT
)
from utils.ui_constants import (
    TABLE_CHECKBOX_WIDTH, TABLE_COLOR_WIDTH, TABLE_METHOD_WIDTH,
    TABLE_CONSUMPTION_WIDTH, TABLE_AVERAGE_WIDTH, TABLE_PERCENTAGE_WIDTH
)

class MethodTable(TableWidget):
    # Signal emitted when a method's visibility is toggled
    method_toggled = pyqtSignal(str, bool)  # (method_name, is_visible)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_methods = []
        self.checkbox_mode = False 
        self.method_colors = {}
        self.setup_table()
        
    def setup_table(self):
        """Configure the table's basic settings."""
        # Set column count and headers
        self.setColumnCount(5)
        self.setHorizontalHeaderLabels(["Method", "Consumption", "Average", "Percentage", "Progress"])
        
        # Configure headers
        self._configure_headers()
        
        # Set minimum column widths
        self.horizontalHeader().setMinimumSectionSize(60)
        
        self.verticalHeader().setVisible(False)

        self.setWordWrap(False)
        self.setShowGrid(False)
        self.setFrameShape(QTableWidget.Shape.NoFrame)

        self.verticalHeader().setDefaultSectionSize(32)
        self.verticalHeader().setMinimumSectionSize(28)

        self.horizontalHeader().setVisible(True)

        self.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.setAlternatingRowColors(True)
        self.itemSelectionChanged.connect(self._update_row_selection_styles)
        self.cellClicked.connect(self._on_cell_clicked)
    
    def _update_row_selection_styles(self):
        """Update cell widget styles to match row selection state."""
        if not self.checkbox_mode:
            return
            
        for row in range(self.rowCount()):
            # Checkbox widget (Column 0)
            checkbox_widget = self.cellWidget(row, 0)
            if checkbox_widget:
                checkbox_widget.setStyleSheet(f"""
                    background-color: transparent;
                    border: none;
                """)
                
            # Color widget (Column 1)
            color_widget = self.cellWidget(row, 1)
            if color_widget:
                color_widget.setStyleSheet(f"""
                    background-color: transparent;
                    border-bottom: 1px solid {COLOR_BORDER_CELL_BOTTOM};
                    border-right: 1px solid {COLOR_BORDER_CELL_RIGHT};
                """)
                
    def _on_cell_clicked(self, row, col):
        """Handle clicks on the table cells."""
        
        if self.checkbox_mode and col == 0 and row >= 0:
            widget = self.cellWidget(row, 0)
            if widget:
                checkboxes = widget.findChildren(CheckBox)
                if checkboxes:
                    checkbox = checkboxes[0]
                    checkbox.click()
    
    def _configure_headers(self):
        """Configure header resize modes."""
        header = self.horizontalHeader()
        if self.checkbox_mode:
            header.setSectionResizeMode(0, QHeaderView.ResizeMode.Fixed)  # Checkbox
            header.setSectionResizeMode(1, QHeaderView.ResizeMode.Fixed)  # Color
            header.setSectionResizeMode(2, QHeaderView.ResizeMode.Interactive)  # Method
            header.setSectionResizeMode(3, QHeaderView.ResizeMode.Interactive)  # Consumption
            header.setSectionResizeMode(4, QHeaderView.ResizeMode.Interactive)  # Average
            header.setSectionResizeMode(5, QHeaderView.ResizeMode.Stretch)      # Percentage
            
            self.setColumnWidth(0, 20)   # Checkbox (Graph)
            self.setColumnWidth(1, 16)   # Color
            self.setColumnWidth(2, 250)  # Method
            self.setColumnWidth(3, 140)  # Consumption
            self.setColumnWidth(4, 140)  # Average
            self.setColumnWidth(5, 105)  # Percentage
        else:
            header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
            header.setSectionResizeMode(1, QHeaderView.ResizeMode.Fixed)
            header.setSectionResizeMode(2, QHeaderView.ResizeMode.Fixed)
            header.setSectionResizeMode(3, QHeaderView.ResizeMode.Fixed)
            header.setSectionResizeMode(4, QHeaderView.ResizeMode.Stretch)
            
            self.setColumnWidth(1, 120)
            self.setColumnWidth(2, 120)
            self.setColumnWidth(3, 100)
        
        header.setDefaultAlignment(Qt.AlignmentFlag.AlignLeft)
    
    def enable_checkbox_mode(self):
        """Enable checkbox mode for method visibility toggling."""
        self.checkbox_mode = True
        self.setColumnCount(6)
        self.setHorizontalHeaderLabels(["Graph", "Color", "Method", "Consumption", "Average", "Percentage"])
        self._configure_headers()
        
    def update_methods(self, methods, colors=None):
        """Update the table with new methods data."""
        self.setRowCount(0)
        self.current_methods = methods
        if colors:
            self.method_colors = colors
        
        # Sort methods by percentage in descending order
        methods.sort(key=lambda x: x.percentage, reverse=True)
        
        row_offset = 0
        
        # Add "TOTAL" row if in checkbox mode
        if self.checkbox_mode:
            self.insertRow(0)
            row_offset = 1
            
            # Checkbox for TOTAL
            checkbox_widget = QWidget()
            checkbox_layout = QHBoxLayout(checkbox_widget)
            checkbox_layout.setContentsMargins(0, 0, 0, 0)
            checkbox_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
            
            total_checkbox = CheckBox()
            total_checkbox.setText("")
            total_checkbox.setProperty("method_name", "TOTAL")
            total_checkbox.blockSignals(True)
            total_checkbox.setChecked(True)
            total_checkbox.blockSignals(False)
            total_checkbox.toggled.connect(
                lambda state: self.method_toggled.emit("TOTAL", state)
            )
            checkbox_layout.addWidget(total_checkbox)
            checkbox_widget.setStyleSheet("background-color: transparent;")
            
            # Add item for background color
            total_bg_item = QTableWidgetItem()
            total_bg_item.setFlags(Qt.ItemFlag.ItemIsSelectable | Qt.ItemFlag.ItemIsEnabled)
            self.setItem(0, 0, total_bg_item)

            self.setCellWidget(0, 0, checkbox_widget)
            
            # Color indicator for TOTAL (blue)
            color_widget = QWidget()
            color_widget.setStyleSheet("background-color: transparent;")
            color_layout = QHBoxLayout(color_widget)
            color_layout.setContentsMargins(2, 5, 2, 5)
            
            color_label = QWidget()
            color_label.setFixedSize(20, 20)
            color_label.setStyleSheet(get_total_color_indicator_style())
            color_layout.addWidget(color_label)
            
            total_color_bg_item = QTableWidgetItem()
            total_color_bg_item.setFlags(Qt.ItemFlag.ItemIsSelectable | Qt.ItemFlag.ItemIsEnabled)
            self.setItem(0, 1, total_color_bg_item)
            
            self.setCellWidget(0, 1, color_widget)
            
            # Name
            name_item = QTableWidgetItem("TOTAL (Global)")
            name_item.setFlags(name_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            name_item.setTextAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
            name_item.setFont(QFont("Arial", 12, QFont.Weight.Bold))
            self.setItem(0, 2, name_item)
            
            # Consumption
            consumption_item = QTableWidgetItem("-")
            consumption_item.setFlags(consumption_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            consumption_item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            consumption_item.setFont(QFont("Arial", 12))
            self.setItem(0, 3, consumption_item)

           
            total_avg = 0.0
            timeline_consumptions = {}
            for m in methods:
                 for p in m.consumption_evolution:
                     if p.timestamp not in timeline_consumptions:
                         timeline_consumptions[p.timestamp] = 0.0
                     timeline_consumptions[p.timestamp] += p.consumption
            
            if timeline_consumptions:
                total_values = list(timeline_consumptions.values())
                total_avg = np.mean(total_values)
            
            avg_item = QTableWidgetItem(f"{total_avg:.4f} J")
            avg_item.setFlags(avg_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            avg_item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            avg_item.setFont(QFont("Arial", 12, QFont.Weight.Bold))
            self.setItem(0, 4, avg_item)
            
            # Percentage
            percentage_item = QTableWidgetItem("100%")
            percentage_item.setFlags(percentage_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            percentage_item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            percentage_item.setFont(QFont("Arial", 12, QFont.Weight.Bold))
            self.setItem(0, 5, percentage_item)
        
        # Display sorted methods
        for idx, method in enumerate(methods):
            row = idx + row_offset
            self.insertRow(row)
            col_offset = 0
            
            # Checkbox column (if in checkbox mode)
            if self.checkbox_mode:
                checkbox_widget = QWidget()
                checkbox_layout = QHBoxLayout(checkbox_widget)
                checkbox_layout.setContentsMargins(0, 0, 0, 0)
                checkbox_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
                
                checkbox = CheckBox()
                checkbox.setText("")
                checkbox.setProperty("method_name", method.name)
                checkbox.toggled.connect(
                    lambda state, name=method.name: self.method_toggled.emit(name, state)
                )
                checkbox_layout.addWidget(checkbox)
                
                # Add item for background color
                checkbox_item = QTableWidgetItem()
                checkbox_item.setFlags(Qt.ItemFlag.ItemIsSelectable | Qt.ItemFlag.ItemIsEnabled)
                self.setItem(row, col_offset, checkbox_item)
                
                checkbox_widget.setStyleSheet("background-color: transparent;")
                self.setCellWidget(row, col_offset, checkbox_widget)
                col_offset += 1
                
                # Color indicator column
                color_widget = QWidget()
                color_widget.setStyleSheet("background-color: transparent;")
                color_layout = QHBoxLayout(color_widget)
                color_layout.setContentsMargins(2, 5, 2, 5)
                
                if method.name in self.method_colors:
                    r, g, b = self.method_colors[method.name]
                    color_label = QWidget()
                    color_label.setFixedSize(20, 20)
                    color_label.setStyleSheet(get_color_indicator_style(r, g, b))
                    color_layout.addWidget(color_label)
                
                # Add item for background color
                color_item = QTableWidgetItem()
                color_item.setFlags(Qt.ItemFlag.ItemIsSelectable | Qt.ItemFlag.ItemIsEnabled)
                self.setItem(row, col_offset, color_item)
                
                self.setCellWidget(row, col_offset, color_widget)
                col_offset += 1
            
            # Name column
            name = method.name
            if len(name) > 50:
                name = name[:47] + "[..]"
            name_item = QTableWidgetItem(f"⚡ {name}" if not self.checkbox_mode else name)
            name_item.setFlags(name_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            name_item.setTextAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
            name_item.setFont(QFont("Arial", 12))
            name_item.setToolTip(method.name)
            self.setItem(row, col_offset, name_item)
            col_offset += 1
            
            # Consumption column
            consumption_text = f"{method.consumption:.4f} J"
            consumption_item = QTableWidgetItem(consumption_text)
            consumption_item.setFlags(consumption_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            consumption_item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            consumption_item.setFont(QFont("Arial", 12))
            self.setItem(row, col_offset, consumption_item)
            col_offset += 1

            # Average column
            avg_val = np.mean([p.consumption for p in method.consumption_evolution]) if method.consumption_evolution else 0.0
            avg_text = f"{avg_val:.4f} J"
            avg_item = QTableWidgetItem(avg_text)
            avg_item.setFlags(avg_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            avg_item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            avg_item.setFont(QFont("Arial", 12))
            self.setItem(row, col_offset, avg_item)
            col_offset += 1
            
            # Percentage column
            if self.checkbox_mode:
                percentage_text = f"{method.percentage:.2f}%"
                percentage_item = QTableWidgetItem(percentage_text)
                percentage_item.setFlags(percentage_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
                percentage_item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
                percentage_item.setFont(QFont("Arial", 12))
                self.setItem(row, col_offset, percentage_item)
            else:
                # Original percentage item
                percentage_text = f"{method.percentage:.2f}%"
                percentage_item = QTableWidgetItem(percentage_text)
                percentage_item.setFlags(percentage_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
                percentage_item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
                percentage_item.setFont(QFont("Arial", 12))
                self.setItem(row, col_offset, percentage_item)
                col_offset += 1
                
                # Progress bar column
                progress_bar = QProgressBar()
                percentage_value = int(method.percentage)
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
                progress_widget.setStyleSheet(get_progress_wrapper_style("transparent"))
                
                self.setCellWidget(row, col_offset, progress_widget)
            
    def filter_methods(self, text):
        """Filter methods based on search text."""
        name_col = 2 if self.checkbox_mode else 0
        start_row = 1 if self.checkbox_mode else 0
        
        for row in range(start_row, self.rowCount()):
            item = self.item(row, name_col)
            if item:
                # Remove lightning symbol if present
                name_text = item.text().replace("⚡ ", "")
                self.setRowHidden(row, text.lower() not in name_text.lower())
            
    def get_selected_method(self):
        """Get the currently selected method."""
        selected_items = self.selectedItems()
        if selected_items and self.current_methods:
            row = selected_items[0].row()
            
            if self.checkbox_mode:
                if row == 0:
                    return None
                row -= 1
            
            if 0 <= row < len(self.current_methods):
                return self.current_methods[row]
        return None 