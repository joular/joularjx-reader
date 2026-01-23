from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                            QLineEdit, QRadioButton, QPushButton)
from PyQt6.QtCore import Qt, pyqtSignal
import numpy as np

from .interactive_graph import InteractiveGraphWidget
from .method_table import MethodTable
from .consumption_graph import ConsumptionGraphDialog
from utils.style_utils import METHOD_COLORS


class MetricsPanel(QWidget):
    """Panel displaying current consumption metrics"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        
    def setup_ui(self):
        """Setup the metrics UI"""
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 10, 0, 10)
        layout.setSpacing(20)
        
        # Create metric cards
        self.total_label = self._create_metric_card("Total Consumption", "0 J", "total")
        self.avg_label = self._create_metric_card("Average Consumption", "0 J", "avg")
        self.max_label = self._create_metric_card("Peak Maximum", "0 J", "max")
        self.min_label = self._create_metric_card("Minimum", "0 J", "min")
        
        layout.addWidget(self.total_label)
        layout.addWidget(self.avg_label)
        layout.addWidget(self.max_label)
        layout.addWidget(self.min_label)
        layout.addStretch()
        
        
    def _create_metric_card(self, title, value, card_type):
        """Create a styled metric card using QSS styles"""
        container = QWidget()
        container.setObjectName(f"metric_card_{card_type}")
        
        layout = QVBoxLayout(container)
        layout.setContentsMargins(15, 12, 15, 12)
        layout.setSpacing(8)
        
        title_label = QLabel(title)
        title_label.setObjectName("metric_title")
        
        value_label = QLabel(value)
        value_label.setObjectName("metric_value")
        
        layout.addWidget(title_label)
        layout.addWidget(value_label)
        
        container.value_label = value_label
        
        return container
        
    def update_metrics(self, total, avg, max_val, min_val):
        """Update all metric values."""
        self.total_label.value_label.setText(f"{total:.2f} J")
        self.avg_label.value_label.setText(f"{avg:.2f} J")
        self.max_label.value_label.setText(f"{max_val:.2f} J")
        self.min_label.value_label.setText(f"{min_val:.2f} J")


class AnalysisPage(QWidget):
    """Main analysis page with interactive graph and method selection."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        
        self.reader = None
        self.current_methods = []
        self.method_colors = {}
        self.total_checked = False
        
    def setup_ui(self):
        """Setup the UI components."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        # Title
        title = QLabel("Method Analysis")
        title.setObjectName("page_title")
        layout.addWidget(title)
        
        # Metrics panel
        self.metrics_panel = MetricsPanel()
        layout.addWidget(self.metrics_panel)
        
        # Interactive graph
        self.graph = InteractiveGraphWidget()
        layout.addWidget(self.graph, stretch=3)
        
        # Search and filters
        controls = QHBoxLayout()
        self.search_box = QLineEdit()
        self.search_box.setPlaceholderText("Search method...")
        self.search_box.textChanged.connect(self.on_search_changed)
        
        self.app_radio = QRadioButton("Application Only")
        self.app_radio.setChecked(True)
        self.all_radio = QRadioButton("All Methods")
        self.app_radio.toggled.connect(self.on_filter_changed)
        
        controls.addWidget(self.search_box)
        controls.addSpacing(20)
        controls.addWidget(self.app_radio)
        controls.addWidget(self.all_radio)
        layout.addLayout(controls)
        
        self.table = MethodTable()
        self.table.enable_checkbox_mode()
        self.table.method_toggled.connect(self.on_method_toggled)
        self.table.itemSelectionChanged.connect(self.on_method_selected)
        layout.addWidget(self.table, stretch=2)
        
    def set_reader(self, reader):
        """Set the data reader and load data."""
        self.reader = reader
        self.reload_data()
        
    def reload_data(self):
        """Reload data from reader."""
        if not self.reader:
            return
            
        data = self.reader.app_methods if self.app_radio.isChecked() else self.reader.all_methods
        methods = []
        for m_list in data.values():
            methods.extend(m_list)
        
        # Clear graph data first
        self.graph.clear_all()
        
        # Sort by percentage
        methods.sort(key=lambda x: x.percentage, reverse=True)
        self.current_methods = methods
        
        # Assign colors to methods
        self._assign_colors()
        
        # Load total evolution data
        self._load_total_evolution()
        
        # Update table
        self.table.update_methods(methods, self.method_colors)
        
        # Add method data to graph
        for method in methods:
            if method.consumption_evolution:
                timestamps = [p.timestamp for p in method.consumption_evolution]
                consumptions = [p.consumption for p in method.consumption_evolution]
                color = self.method_colors.get(method.name, (100, 100, 100))
                self.graph.add_method_data(method.name, timestamps, consumptions, color)
        
        # Manually trigger TOTAL checkbox to ensure display
        self.on_method_toggled("TOTAL", True)
        
        # Update graph bounds to fit data
        self.graph.update_bounds()
        
    def _assign_colors(self):
        """Assign distinct colors to methods."""
        self.method_colors.clear()
        
        # Assign colors from global theme
        for idx, method in enumerate(self.current_methods[:10]):
            self.method_colors[method.name] = METHOD_COLORS[idx % len(METHOD_COLORS)]
        
        # Remaining methods get grey shades until best method
        for method in self.current_methods[10:]:
            grey_val = 100 + (idx % 5) * 30
            self.method_colors[method.name] = (grey_val, grey_val, grey_val)
    
    def _load_total_evolution(self):
        """Load total evolution data from all methods."""
        if not self.reader:
            return
        
        # Get all evolution data
        data = self.reader.app_methods if self.app_radio.isChecked() else self.reader.all_methods
        
        # Aggregate all timestamps and consumptions
        all_points = {}  # {timestamp: total_consumption}
        
        for method_list in data.values():
            for method in method_list:
                for point in method.consumption_evolution:
                    if point.timestamp not in all_points:
                        all_points[point.timestamp] = 0
                    all_points[point.timestamp] += point.consumption
        
        if all_points:
            timestamps = sorted(all_points.keys())
            consumptions = [all_points[ts] for ts in timestamps]
            self.graph.set_total_data(timestamps, consumptions)
    
    def on_method_toggled(self, method_name, checked):
        """Handle method visibility toggle."""
        
        if method_name == "TOTAL":
            self.total_checked = checked
            self.graph.set_total_visibility(checked)
        else:
            self.graph.set_method_visibility(method_name, checked)
        
        # Update metrics
        self._update_metrics()
    
    def _update_metrics(self):
        """Update the metrics panel based on visible methods."""
        if not self.reader:
            return
        
        # Collect visible method data
        visible_consumptions = []
        
        if self.total_checked and self.graph.total_data is not None:
            # Use total data
            visible_consumptions = self.graph.total_data[1]
        else:
            for method in self.current_methods:
                if method.name in self.graph.visible_methods:
                    for point in method.consumption_evolution:
                        visible_consumptions.append(point.consumption)
        
        if len(visible_consumptions) > 0:
            total = sum(visible_consumptions)
            avg = np.mean(visible_consumptions)
            max_val = max(visible_consumptions)
            min_val = min(visible_consumptions)
            self.metrics_panel.update_metrics(total, avg, max_val, min_val)
        else:
            self.metrics_panel.update_metrics(0, 0, 0, 0)
    
    def on_search_changed(self, text):
        """Handle search text change."""
        self.table.filter_methods(text)
    
    def on_filter_changed(self):
        """Handle app/all filter change."""
        self.reload_data()
    
    def on_method_selected(self):
        """Handle method selection for details view."""
        method = self.table.get_selected_method()
        if method:
            ConsumptionGraphDialog(method, self).exec()
            self.table.clearSelection()
