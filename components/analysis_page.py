from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                            QLineEdit, QRadioButton, QPushButton, QFrame)
from PyQt6.QtCore import Qt, pyqtSignal
import numpy as np

from .interactive_graph import InteractiveGraphWidget
from .method_table import MethodTable
from .consumption_graph import ConsumptionGraphDialog

# Method color palette (previously in style_utils)
METHOD_COLORS = [
    (255, 99, 71),      # Tomato
    (60, 179, 113),     # MediumSeaGreen
    (255, 165, 0),      # Orange
    (106, 90, 205),     # SlateBlue
    (255, 20, 147),     # DeepPink
    (0, 191, 255),      # DeepSkyBlue
    (255, 215, 0),      # Gold
    (138, 43, 226),     # BlueViolet
    (50, 205, 50),      # LimeGreen
    (255, 105, 180),    # HotPink
]



class MetricsPanel(QWidget):
    """Panel displaying current consumption metrics"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        
    def setup_ui(self):
        """Setup the metrics UI"""
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 5, 0, 5)
        layout.setSpacing(0)
        
        self.container = QWidget()
        self.container.setObjectName("metrics_unified_container")
        
        self.container_layout = QHBoxLayout(self.container)
        self.container_layout.setContentsMargins(15, 8, 15, 8)
        self.container_layout.setSpacing(20)
        
        self.total_label = self._add_metric("Total", "0 J", "total")
        self._add_separator()
        self.avg_label = self._add_metric("Average", "0 J", "avg")
        self._add_separator()
        self.max_label = self._add_metric("Max", "0 J", "max")
        self._add_separator()
        self.min_label = self._add_metric("Min", "0 J", "min")
        
        layout.addWidget(self.container)
        
    def _add_metric(self, title, value, object_name_suffix):
        """Add a metric items to the container"""
        wrapper = QWidget()
        wrapper.setObjectName("metric_wrapper")
        v_layout = QVBoxLayout(wrapper)
        v_layout.setContentsMargins(0, 0, 0, 0)
        v_layout.setSpacing(2)
        v_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        title_label = QLabel(title.upper())
        title_label.setObjectName("metric_title_unified")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        value_label = QLabel(value)
        value_label.setObjectName(f"metric_value_{object_name_suffix}") 
        value_label.setProperty("class", "metric_value_unified") 
        value_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        v_layout.addWidget(title_label)
        v_layout.addWidget(value_label)
        
        self.container_layout.addWidget(wrapper, 1)
        return value_label

    def _add_separator(self):
        """Add a vertical separator line"""
        line = QFrame()
        line.setFrameShape(QFrame.Shape.VLine)
        line.setFrameShadow(QFrame.Shadow.Sunken)
        line.setObjectName("metric_separator")
        self.container_layout.addWidget(line)

    def update_metrics(self, total, avg, max_val, min_val):
        """Update all metric values."""
        self.total_label.setText(f"{total:.2f} J")
        self.avg_label.setText(f"{avg:.2f} J")
        self.max_label.setText(f"{max_val:.2f} J")
        self.min_label.setText(f"{min_val:.2f} J")


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
        header_layout = QHBoxLayout()
        header_layout.setContentsMargins(0, 0, 0, 0)
        
        # Title
        title = QLabel("Method Analysis")
        title.setObjectName("page_title")
        header_layout.addWidget(title)
        
        header_layout.addSpacing(40)
        
        # Metrics panel
        self.metrics_panel = MetricsPanel()
        header_layout.addWidget(self.metrics_panel, stretch=1)
        layout.addLayout(header_layout)
        
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
