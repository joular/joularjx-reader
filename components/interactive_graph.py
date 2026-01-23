from PyQt6.QtWidgets import QWidget, QVBoxLayout
import pyqtgraph as pg
import numpy as np
from utils.style_utils import GRAPH_STYLE, TOTAL_COLOR


class InteractiveGraphWidget(QWidget):
    """Interactive graph widget with main plot, range selector, and hover tooltip."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        
        # Data storage
        self.total_data = None  # (timestamps, consumptions)
        self.method_data = {}  # {method_name: (timestamps, consumptions, color)}
        self.visible_methods = set()  # Set of visible method names
        
    def setup_ui(self):
        """Setup the UI components."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(5)
        
        # Create graphics layout widget
        self.graphics_widget = pg.GraphicsLayoutWidget()
        self.graphics_widget.setBackground(GRAPH_STYLE['background'])
        layout.addWidget(self.graphics_widget)
        
        # Main plot (single plot, no range selector)
        self.main_plot = self.graphics_widget.addPlot(row=0, col=0)
        self.main_plot.setLabel('left', 'Consumption (J)', **{'font-size': GRAPH_STYLE['font_size'], 'color': GRAPH_STYLE['axis_color']})
        self.main_plot.setLabel('bottom', 'Timestamp', **{'font-size': GRAPH_STYLE['font_size'], 'color': GRAPH_STYLE['axis_color']})
        self.main_plot.showGrid(x=True, y=True, alpha=GRAPH_STYLE['grid_alpha'])
        self.main_plot.setTitle('Consumption Evolution', color=GRAPH_STYLE['title_color'], size=GRAPH_STYLE['title_size'])
        self.main_plot.getAxis('left').setPen(pg.mkPen(color=GRAPH_STYLE['axis_color'], width=GRAPH_STYLE['axis_width']))
        self.main_plot.getAxis('bottom').setPen(pg.mkPen(color=GRAPH_STYLE['axis_color'], width=GRAPH_STYLE['axis_width']))
        
        # Enable native navigation (pan and zoom)
        self.main_plot.enableAutoRange()
        self.main_plot.setMouseEnabled(x=True, y=True)
        
        # Crosshair for hover tooltip
        self.vLine = pg.InfiniteLine(angle=90, movable=False, pen=pg.mkPen(GRAPH_STYLE['crosshair_color'], width=GRAPH_STYLE['axis_width'], style=pg.QtCore.Qt.PenStyle.DashLine))
        self.hLine = pg.InfiniteLine(angle=0, movable=False, pen=pg.mkPen(GRAPH_STYLE['crosshair_color'], width=GRAPH_STYLE['axis_width'], style=pg.QtCore.Qt.PenStyle.DashLine))
        self.main_plot.addItem(self.vLine, ignoreBounds=True)
        self.main_plot.addItem(self.hLine, ignoreBounds=True)
        
        # Text item for values with better styling
        self.value_label = pg.TextItem(
            anchor=(0, 1), 
            color=GRAPH_STYLE['title_color'],
            fill=pg.mkBrush(*GRAPH_STYLE['tooltip_background']),
            border=pg.mkPen(GRAPH_STYLE['tooltip_border'], width=GRAPH_STYLE['axis_width'])
        )
        self.main_plot.addItem(self.value_label)
        
        # Connect mouse movement
        self.main_plot.scene().sigMouseMoved.connect(self.mouse_moved)
        
        # Storage for plot items
        self.plot_items = {}  # {method_name or 'total': PlotDataItem}
        
    def set_total_data(self, timestamps, consumptions):
        """Set the total consumption data."""
        self.total_data = (np.array(timestamps), np.array(consumptions))
        
    def add_method_data(self, method_name, timestamps, consumptions, color):
        """Add method data for potential display."""
        self.method_data[method_name] = (
            np.array(timestamps), 
            np.array(consumptions), 
            color
        )
        
    def set_method_visibility(self, method_name, visible):
        """Toggle method visibility on the main plot."""
        if visible:
            if method_name not in self.visible_methods:
                self.visible_methods.add(method_name)
                self._add_method_to_plot(method_name)
        else:
            if method_name in self.visible_methods:
                self.visible_methods.remove(method_name)
                self._remove_method_from_plot(method_name)
   
    def set_total_visibility(self, visible):
        """Toggle total curve visibility."""
        if visible:
            if 'total' not in self.visible_methods:
                self.visible_methods.add('total')
                self._add_total_to_plot()
        else:
            if 'total' in self.visible_methods:
                self.visible_methods.remove('total')
                self._remove_total_from_plot()
   
    def _add_total_to_plot(self):
        """Add total curve to main plot."""
        if self.total_data is None:
            return
            
        timestamps, consumptions = self.total_data
            
        if 'total' in self.plot_items:
            self.main_plot.removeItem(self.plot_items['total'])
        
        pen = pg.mkPen(color=(66, 135, 245), width=3)
        self.plot_items['total'] = self.main_plot.plot(
            self.total_data[0], 
            self.total_data[1], 
            pen=pen,
            name='Total'
        )
        
    def _remove_total_from_plot(self):
        """Remove total curve from main plot."""
        if 'total' in self.plot_items:
            self.main_plot.removeItem(self.plot_items['total'])
            del self.plot_items['total']
    
    def _add_method_to_plot(self, method_name):
        """Add a method curve to the main plot."""
        if method_name not in self.method_data:
            return
            
        timestamps, consumptions, color = self.method_data[method_name]
        
        if method_name in self.plot_items:
            self.main_plot.removeItem(self.plot_items[method_name])
        
        pen = pg.mkPen(color=color, width=GRAPH_STYLE['curve_width'])
        self.plot_items[method_name] = self.main_plot.plot(
            timestamps, 
            consumptions, 
            pen=pen,
            name=method_name
        )
        
    def _remove_method_from_plot(self, method_name):
        """Remove a method curve from the main plot."""
        if method_name in self.plot_items:
            self.main_plot.removeItem(self.plot_items[method_name])
            del self.plot_items[method_name]
    
    
    def mouse_moved(self, pos):
        """Handle mouse movement for crosshair and tooltip."""
        if self.main_plot.sceneBoundingRect().contains(pos):
            mouse_point = self.main_plot.vb.mapSceneToView(pos)
            x = mouse_point.x()
            
            # Update crosshair position
            self.vLine.setPos(x)
            
            # Find closest data point and display values
            tooltip_text = self._get_tooltip_text(x)
            if tooltip_text:
                self.value_label.setPos(x, mouse_point.y())
                self.value_label.setText(tooltip_text)
                self.value_label.setVisible(True)
            else:
                self.value_label.setVisible(False)
        else:
            self.value_label.setVisible(False)
    
    def _get_tooltip_text(self, x):
        """Generate tooltip text showing values at x for all visible curves."""
        lines = []
        
        # Check total
        if 'total' in self.visible_methods and self.total_data is not None:
            value = self._get_value_at_x(self.total_data[0], self.total_data[1], x)
            if value is not None:
                lines.append(f"Total: {value:.4f} J")
        
        # Check visible methods
        for method_name in self.visible_methods:
            if method_name == 'total':
                continue
            if method_name in self.method_data:
                timestamps, consumptions, _ = self.method_data[method_name]
                value = self._get_value_at_x(timestamps, consumptions, x)
                if value is not None:
                    # Truncate long method names
                    display_name = method_name[:30] + "..." if len(method_name) > 30 else method_name
                    lines.append(f"{display_name}: {value:.4f} J")
        
        return "\n".join(lines) if lines else None
    
    def _get_value_at_x(self, timestamps, values, x):
        """Get the value at a given x (timestamp) using nearest neighbor."""
        if len(timestamps) == 0:
            return None
        
        # Find closest timestamp
        idx = np.argmin(np.abs(timestamps - x))
        
        # Check if it's reasonably close
        if abs(timestamps[idx] - x) < (timestamps[-1] - timestamps[0]) * 0.05:
            return values[idx]
        
        return None
    
    def clear_all(self):
        """Clear all data and plots."""
        # Clear main plot items
        for item in list(self.plot_items.values()):
            self.main_plot.removeItem(item)
        self.plot_items.clear()
        
        # Clear data
        self.total_data = None
        self.method_data.clear()
        self.visible_methods.clear()

    def update_bounds(self):
        """Update graph bounds based on loaded data."""
        min_x, max_x = float('inf'), float('-inf')
        min_y, max_y = float('inf'), float('-inf')
        has_data = False
        
        # Check total data
        if self.total_data is not None:
            ts, cons = self.total_data
            if len(ts) > 0:
                min_x = min(min_x, np.min(ts))
                max_x = max(max_x, np.max(ts))
                min_y = min(min_y, np.min(cons))
                max_y = max(max_y, np.max(cons))
                has_data = True
                
        # Check method data
        for ts, cons, _ in self.method_data.values():
            if len(ts) > 0:
                min_x = min(min_x, np.min(ts))
                max_x = max(max_x, np.max(ts))
                min_y = min(min_y, np.min(cons))
                max_y = max(max_y, np.max(cons))
                has_data = True
                
        if not has_data:
            return
            
        # seamless margin
        x_margin = (max_x - min_x) * 0.05 if max_x != min_x else 1.0
        y_margin = (max_y - min_y) * 0.1 if max_y != min_y else 1.0
        
        # Set limits (hard bounds for pan/zoom)
        self.main_plot.getViewBox().setLimits(
            xMin=min_x - x_margin,
            xMax=max_x + x_margin,
            yMin=0, # Consumption can't be negative, but let's stick to 0 or min_y - margin
            yMax=max_y + y_margin,
            minXRange=x_margin * 0.1 if x_margin > 0 else 1.0,
            minYRange=y_margin * 0.1 if y_margin > 0 else 1.0
        )
        
        # Set initial range
        self.main_plot.setXRange(min_x - x_margin, max_x + x_margin, padding=0)
        self.main_plot.setYRange(0, max_y + y_margin, padding=0)
