from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel)
from PyQt6.QtCore import Qt
import pyqtgraph as pg
import numpy as np
from utils.style_utils import get_metric_label_style

class ConsumptionGraphDialog(QDialog):
    def __init__(self, method, parent=None):
        super().__init__(parent)
        self.method = method
        self.setup_ui()
        
    def setup_ui(self):
        """Setup the UI components."""
        self.setWindowTitle(f"Consumption Evolution - {self.method.name}")
        self.setMinimumSize(800, 500)
        
        # Create layout
        layout = QVBoxLayout(self)
        
        # Create plot widget
        plot_widget = pg.PlotWidget()
        plot_widget.setBackground('w')  # White background
        plot_widget.showGrid(x=True, y=True)
        
        # Set labels
        plot_widget.setLabel('left', 'Consumption (Joules)')
        plot_widget.setLabel('bottom', 'Timestamp')
        plot_widget.setTitle(f"Energy Consumption Evolution for {self.method.name}", 
                           color='k', size='20pt')
        
        # Get data
        timestamps = np.array([point.timestamp for point in self.method.consumption_evolution])
        consumptions = np.array([point.consumption for point in self.method.consumption_evolution])
        
        # Create the plot
        pen = pg.mkPen(color=(66, 135, 245), width=2)
        scatter_pen = pg.mkPen(color=(66, 135, 245), width=2)
        scatter_brush = pg.mkBrush(color=(66, 135, 245))
        
        # Add line plot
        plot_widget.plot(timestamps, consumptions, pen=pen)
        
        # Add scatter plot
        scatter = pg.ScatterPlotItem(
            x=timestamps,
            y=consumptions,
            pen=scatter_pen,
            brush=scatter_brush,
            size=8
        )
        plot_widget.addItem(scatter)
        
        # Add statistics
        stats_layout = QHBoxLayout()
        
        # Total consumption
        total_consumption = QLabel(f"Total Consumption: {self.method.consumption:.4f} J")
        total_consumption.setStyleSheet(get_metric_label_style('dialog_value'))
        stats_layout.addWidget(total_consumption)
        
        # Percentage
        percentage = QLabel(f"Percentage: {self.method.percentage:.2f}%")
        percentage.setStyleSheet(get_metric_label_style('dialog_value'))
        stats_layout.addWidget(percentage)
        
        # Average consumption
        avg_consumption = np.mean(consumptions)
        average = QLabel(f"Average Consumption: {avg_consumption:.4f} J")
        average.setStyleSheet(get_metric_label_style('dialog_value'))
        stats_layout.addWidget(average)
        
        # Add widgets to layout
        layout.addWidget(plot_widget)
        layout.addLayout(stats_layout) 