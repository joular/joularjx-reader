from PyQt6.QtWidgets import QWidget, QVBoxLayout, QSizePolicy
import pyqtgraph as pg
import numpy as np
from utils.style_constants import GRAPH_STYLE, TOTAL_COLOR


class InteractiveGraphWidget(QWidget):
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        
        self.total_data = None
        self.method_data = {}
        self.visible_methods = set()
        
    def setup_ui(self):
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(5)
        
        self.graphics_widget = pg.GraphicsLayoutWidget()
        self.graphics_widget.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.graphics_widget.setBackground(GRAPH_STYLE['background'])
        
        self.graphics_widget.ci.layout.setContentsMargins(0, 0, 0, 0)
        self.graphics_widget.ci.layout.setSpacing(0)
        
        layout.addWidget(self.graphics_widget)
        
        self.main_plot = self.graphics_widget.addPlot(row=0, col=0)
        self.main_plot.setLabel('left', 'Consumption (J)', **{'font-size': GRAPH_STYLE['font_size'], 'color': GRAPH_STYLE['axis_color']})
        self.main_plot.setLabel('bottom', 'Timestamp', **{'font-size': GRAPH_STYLE['font_size'], 'color': GRAPH_STYLE['axis_color']})
        self.main_plot.showGrid(x=True, y=True, alpha=GRAPH_STYLE['grid_alpha'])
        self.main_plot.setTitle('Consumption Evolution', color=GRAPH_STYLE['title_color'], size=GRAPH_STYLE['title_size'])
        self.main_plot.getAxis('left').setPen(pg.mkPen(color=GRAPH_STYLE['axis_color'], width=GRAPH_STYLE['axis_width']))
        self.main_plot.getAxis('bottom').setPen(pg.mkPen(color=GRAPH_STYLE['axis_color'], width=GRAPH_STYLE['axis_width']))
        
        self.main_plot.enableAutoRange()
        self.main_plot.setMouseEnabled(x=True, y=True)
        
        self.vLine = pg.InfiniteLine(angle=90, movable=False, pen=pg.mkPen(GRAPH_STYLE['crosshair_color'], width=GRAPH_STYLE['axis_width'], style=pg.QtCore.Qt.PenStyle.DashLine))
        self.hLine = pg.InfiniteLine(angle=0, movable=False, pen=pg.mkPen(GRAPH_STYLE['crosshair_color'], width=GRAPH_STYLE['axis_width'], style=pg.QtCore.Qt.PenStyle.DashLine))
        self.main_plot.addItem(self.vLine, ignoreBounds=True)
        self.main_plot.addItem(self.hLine, ignoreBounds=True)
        
        self.value_label = pg.TextItem(
            anchor=(0, 1), 
            color=GRAPH_STYLE['title_color'],
            fill=pg.mkBrush(*GRAPH_STYLE['tooltip_background']),
            border=pg.mkPen(GRAPH_STYLE['tooltip_border'], width=GRAPH_STYLE['axis_width'])
        )
        self.main_plot.addItem(self.value_label)
        
        self.main_plot.scene().sigMouseMoved.connect(self.mouse_moved)
        
        self.plot_items = {}
        
    def set_total_data(self, timestamps, consumptions):
        self.total_data = (np.array(timestamps), np.array(consumptions))
        
    def add_method_data(self, method_name, timestamps, consumptions, color):
        self.method_data[method_name] = (
            np.array(timestamps), 
            np.array(consumptions), 
            color
        )
        
    def set_method_visibility(self, method_name, visible):
        if visible:
            if method_name not in self.visible_methods:
                self.visible_methods.add(method_name)
                self._add_method_to_plot(method_name)
        else:
            if method_name in self.visible_methods:
                self.visible_methods.remove(method_name)
                self._remove_method_from_plot(method_name)
   
    def set_total_visibility(self, visible):
        if visible:
            if 'total' not in self.visible_methods:
                self.visible_methods.add('total')
                self._add_total_to_plot()
        else:
            if 'total' in self.visible_methods:
                self.visible_methods.remove('total')
                self._remove_total_from_plot()
   
    def _add_total_to_plot(self):
        if self.total_data is None:
            return
            
        timestamps, consumptions = self.total_data
            
        if 'total' in self.plot_items:
            self.main_plot.removeItem(self.plot_items['total'])
        
        pen = pg.mkPen(color=TOTAL_COLOR, width=3)
        self.plot_items['total'] = self.main_plot.plot(
            self.total_data[0], 
            self.total_data[1], 
            pen=pen,
            name='Total'
        )
        
    def _remove_total_from_plot(self):
        if 'total' in self.plot_items:
            self.main_plot.removeItem(self.plot_items['total'])
            del self.plot_items['total']
    
    def _add_method_to_plot(self, method_name):
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
        if method_name in self.plot_items:
            self.main_plot.removeItem(self.plot_items[method_name])
            del self.plot_items[method_name]
    
    def mouse_moved(self, pos):
        if self.main_plot.sceneBoundingRect().contains(pos):
            mouse_point = self.main_plot.vb.mapSceneToView(pos)
            x = mouse_point.x()
            
            self.vLine.setPos(x)
            
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
        lines = []
        
        if 'total' in self.visible_methods and self.total_data is not None:
            value = self._get_value_at_x(self.total_data[0], self.total_data[1], x)
            if value is not None:
                lines.append(f"Total: {value:.4f} J")
        
        for method_name in self.visible_methods:
            if method_name == 'total':
                continue
            if method_name in self.method_data:
                timestamps, consumptions, _ = self.method_data[method_name]
                value = self._get_value_at_x(timestamps, consumptions, x)
                if value is not None:
                    lines.append(f"{method_name}: {value:.4f} J")
        
        return "\n".join(lines) if lines else None
    
    def _get_value_at_x(self, timestamps, values, x):
        if len(timestamps) == 0:
            return None
        
        idx = np.argmin(np.abs(timestamps - x))
        
        if abs(timestamps[idx] - x) < (timestamps[-1] - timestamps[0]) * 0.05:
            return values[idx]
        
        return None
    
    def clear_all(self):
        for item in list(self.plot_items.values()):
            self.main_plot.removeItem(item)
        self.plot_items.clear()
        
        self.total_data = None
        self.method_data.clear()
        self.visible_methods.clear()

    def update_bounds(self):
        min_x, max_x = float('inf'), float('-inf')
        min_y, max_y = float('inf'), float('-inf')
        has_data = False
        
        if self.total_data is not None:
            ts, cons = self.total_data
            if len(ts) > 0:
                min_x = min(min_x, np.min(ts))
                max_x = max(max_x, np.max(ts))
                min_y = min(min_y, np.min(cons))
                max_y = max(max_y, np.max(cons))
                has_data = True
                
        for ts, cons, _ in self.method_data.values():
            if len(ts) > 0:
                min_x = min(min_x, np.min(ts))
                max_x = max(max_x, np.max(ts))
                min_y = min(min_y, np.min(cons))
                max_y = max(max_y, np.max(cons))
                has_data = True
                
        if not has_data:
            return
            
        x_margin = (max_x - min_x) * 0.05 if max_x != min_x else 1.0
        y_margin = (max_y - min_y) * 0.1 if max_y != min_y else 1.0
        
        self.main_plot.getViewBox().setLimits(
            xMin=min_x - x_margin,
            xMax=max_x + x_margin,
            yMin=0,
            yMax=max_y + y_margin,
            minXRange=x_margin * 0.1 if x_margin > 0 else 1.0,
            minYRange=y_margin * 0.1 if y_margin > 0 else 1.0
        )
        
        self.main_plot.setXRange(min_x - x_margin, max_x + x_margin, padding=0)
        self.main_plot.setYRange(0, max_y + y_margin, padding=0)
