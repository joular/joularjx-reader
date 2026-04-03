from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, QFrame, QWidget)
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

        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)

        # Plot widget
        plot_widget = pg.PlotWidget()
        plot_widget.setBackground('w')
        plot_widget.showGrid(x=True, y=True)
        plot_widget.setLabel('left', 'Consumption (Joules)')
        plot_widget.setLabel('bottom', 'Timestamp')
        plot_widget.setTitle(f"Energy Consumption Evolution for {self.method.name}",
                             color='k', size='16pt')

        # Data
        timestamps = np.array([point.timestamp for point in self.method.consumption_evolution])
        consumptions = np.array([point.consumption for point in self.method.consumption_evolution])

        pen = pg.mkPen(color=(66, 135, 245), width=2)
        plot_widget.plot(timestamps, consumptions, pen=pen)
        scatter = pg.ScatterPlotItem(
            x=timestamps, y=consumptions,
            pen=pg.mkPen(color=(66, 135, 245), width=2),
            brush=pg.mkBrush(color=(66, 135, 245)),
            size=8
        )
        plot_widget.addItem(scatter)
        layout.addWidget(plot_widget)

        # Stats bar
        stats_container = QWidget()
        stats_container.setObjectName("metrics_unified_container")
        stats_layout = QHBoxLayout(stats_container)
        stats_layout.setContentsMargins(15, 10, 15, 10)
        stats_layout.setSpacing(20)

        avg_consumption = float(np.mean(consumptions)) if len(consumptions) > 0 else 0.0

        def add_stat(title, value):
            wrapper = QWidget()
            wrapper.setObjectName("metric_wrapper")
            vl = QVBoxLayout(wrapper)
            vl.setContentsMargins(0, 0, 0, 0)
            vl.setSpacing(2)
            vl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            t = QLabel(title.upper())
            t.setObjectName("metric_title_unified")
            t.setAlignment(Qt.AlignmentFlag.AlignCenter)
            v = QLabel(value)
            v.setObjectName("metric_value_total")
            v.setProperty("class", "metric_value_unified")
            v.setAlignment(Qt.AlignmentFlag.AlignCenter)
            vl.addWidget(t)
            vl.addWidget(v)
            stats_layout.addWidget(wrapper, 1)

        def add_sep():
            sep = QFrame()
            sep.setFrameShape(QFrame.Shape.VLine)
            sep.setFrameShadow(QFrame.Shadow.Sunken)
            sep.setObjectName("metric_separator")
            stats_layout.addWidget(sep)

        add_stat("Total", f"{self.method.consumption:.4f} J")
        add_sep()
        add_stat("Average", f"{avg_consumption:.4f} J")
        add_sep()
        add_stat("Percentage", f"{self.method.percentage:.2f}%")

        layout.addWidget(stats_container)
