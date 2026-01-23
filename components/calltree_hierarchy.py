from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QTreeWidget, QTreeWidgetItem, QLineEdit, QFrame, 
                             QProgressBar, QScrollArea, QRadioButton, QButtonGroup)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont, QColor
import pyqtgraph as pg
from utils.style_utils import (get_metric_label_style, get_legend_box_style, get_legend_text_style,
                              get_node_card_style, get_chevron_style, get_node_label_style,
                              get_metric_card_container_style)


class TreeNode:
    """Represents a node in the merged call tree hierarchy."""
    def __init__(self, name):
        self.name = name
        self.consumption = 0.0
        self.children = {}
        self.call_count = 0
        
    def add_path(self, path_parts, consumption):
        """Add a call path to the tree, aggregating consumption."""
        self.consumption += consumption
        self.call_count += 1
        
        if path_parts:
            child_name = path_parts[0]
            if child_name not in self.children:
                self.children[child_name] = TreeNode(child_name)
            self.children[child_name].add_path(path_parts[1:], consumption)
    
    def get_percentage(self, total_consumption):
        """Calculate percentage of total consumption."""
        if total_consumption > 0:
            return (self.consumption / total_consumption) * 100
        return 0.0




class CallTreeCardInterface(QWidget):
    """Hierarchical card-based interface for call trees."""
    
    # Signals (disabled - no popups on click)
    calltree_selected = pyqtSignal(object)
    method_selected = pyqtSignal(object)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.app_call_trees = {}
        self.all_call_trees = {}
        self.all_items = []
        self.item_chevrons = {}  # Map tree items to their chevron labels
        self.expansion_state = {} # Map item ID to expanded state
        self.setup_ui()
        
    def setup_ui(self):
        """Setup the UI components."""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(15)
        
        # Statistics cards at top
        self.stats_widget = self.create_statistics_section()
        main_layout.addWidget(self.stats_widget)
        
        # Scrollable area for the rest
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setObjectName("transparent_scroll")
        
        scroll_content = QWidget()
        layout = QVBoxLayout(scroll_content)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(15)
        
        # Search bar
        search_filter_layout = QHBoxLayout()
        
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search method...")
        self.search_input.textChanged.connect(self.filter_tree)
        self.search_input.setObjectName("search_input")
        search_filter_layout.addWidget(self.search_input)
        
        # Radio buttons for filtering (mimicking Analysis Page)
        self.filter_group = QButtonGroup(self)
        
        self.app_radio = QRadioButton("Application Only")
        self.app_radio.setChecked(True)
        self.app_radio.toggled.connect(self.refresh_display)
        self.app_radio.setObjectName("filter_radio")
        self.filter_group.addButton(self.app_radio)
        
        self.all_radio = QRadioButton("All CallTrees")
        self.all_radio.toggled.connect(self.refresh_display)
        self.all_radio.setObjectName("filter_radio")
        self.filter_group.addButton(self.all_radio)
        
        search_filter_layout.addSpacing(20)
        search_filter_layout.addWidget(self.app_radio)
        search_filter_layout.addWidget(self.all_radio)
        
        layout.addLayout(search_filter_layout)
        
        # Intensity legend
        legend_widget = self.create_intensity_legend()
        layout.addWidget(legend_widget)
        
        # Hierarchical tree with custom cards
        self.tree = QTreeWidget()
        self.tree.setHeaderHidden(True)
        self.tree.setIndentation(0)
        self.tree.setRootIsDecorated(False)
        self.tree.setAnimated(True)
        self.tree.setObjectName("hierarchy_tree")
        # Connect expand/collapse signals to update chevrons
        self.tree.itemExpanded.connect(self.on_item_expanded)
        self.tree.itemCollapsed.connect(self.on_item_collapsed)
        # Disable click-to-view-details - only expand/collapse
        self.tree.itemClicked.connect(self.on_item_clicked)
        self.tree.setMinimumHeight(400)  # Ensure tree has minimum height
        layout.addWidget(self.tree, 1)  # Stretch factor of 1 to fill space
        
        scroll.setWidget(scroll_content)
        main_layout.addWidget(scroll, 1)  # Stretch factor to fill remaining space
        
    def create_statistics_section(self):
        """Create the statistics cards at the top."""
        container = QWidget()
        layout = QHBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(15)
        
        self.total_consumption_card = self.create_stat_card("Total Consumption", "0 J")
        layout.addWidget(self.total_consumption_card)
        
        self.method_count_card = self.create_stat_card("Method Count", "0")
        layout.addWidget(self.method_count_card)
        
        self.max_consumption_card = self.create_stat_card("Max Consumption", "0 J")
        layout.addWidget(self.max_consumption_card)
        
        return container
    
    def create_stat_card(self, title, value):
        """Create a single statistics card."""
        card = QFrame()
        card.setStyleSheet("""
            QFrame {
                background-color: white;
                border: 1px solid #e0e0e0;
                border-radius: 8px;
                padding: 12px 15px;
            }
        """)
        card.setMinimumHeight(70)
        
        card_layout = QVBoxLayout(card)
        card_layout.setSpacing(5)
        
        title_label = QLabel(title)
        title_label.setStyleSheet(get_metric_label_style('title'))
        card_layout.addWidget(title_label)
        
        value_label = QLabel(value)
        value_label.setStyleSheet(get_metric_label_style('value'))
        value_label.setObjectName("stat_value")
        card_layout.addWidget(value_label)
        
        return card
    
    
    def create_intensity_legend(self):
        """Create the intensity legend."""
        container = QWidget()
        layout = QHBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(15)
        
        title = QLabel("Consumption Intensity:")
        title.setStyleSheet(get_metric_label_style('dialog_title'))
        layout.addWidget(title)
        
        intensities = [
            ("< 20%", "#f5f5f5"),
            ("20-40%", "#BBDEFB"),
            ("40-60%", "#FFF9C4"),
            ("60-80%", "#FFD180"),
            ("> 80%", "#FFCDD2")
        ]
        
        for label, color in intensities:
            box = QLabel()
            box.setFixedSize(70, 24)
            box.setStyleSheet(get_legend_box_style(color))
            layout.addWidget(box)
            
            text = QLabel(label)
            text.setStyleSheet(get_legend_text_style())
            layout.addWidget(text)
        
        layout.addStretch()
        return container
    
    def get_consumption_color(self, percentage):
        """Get background color based on consumption percentage."""
        if percentage >= 80:
            return "#FFCDD2"  # Red
        elif percentage >= 60:
            return "#FFD180"  # Orange
        elif percentage >= 40:
            return "#FFF9C4"  # Yellow
        elif percentage >= 20:
            return "#BBDEFB"  # Blue
        else:
            return "#f5f5f5"  # Light gray
    
    def get_progress_bar_color(self, percentage):
        """Get progress bar color."""
        if percentage >= 80:
            return "#EF5350"
        elif percentage >= 60:
            return "#FF9800"
        elif percentage >= 40:
            return "#FFC107"
        elif percentage >= 20:
            return "#2196F3"
        else:
            return "#9E9E9E"
    
    def update_data(self, app_call_trees, all_call_trees):
        """Update the interface with new data."""
        self.app_call_trees = app_call_trees
        self.all_call_trees = all_call_trees
        
        self.populate_interface(app_call_trees, all_call_trees)


    def populate_interface(self, app_call_trees, all_call_trees):
        """Populate the interface with call tree data."""
        self.app_call_trees = app_call_trees
        self.all_call_trees = all_call_trees
        
        self.refresh_display()
        
    def refresh_display(self):
        """Refresh the tree display based on current filter settings."""
        self.tree.clear()
        self.all_items = [] # Clear all_items for new population
        self.item_chevrons.clear() # Clear item_chevrons for new population
        self.expansion_state.clear() # Clear saved state
        
        # Determine which data to show
        if self.app_radio.isChecked():
            source_trees = self.app_call_trees
        else:
            source_trees = self.all_call_trees
            
        if not source_trees:
            self.total_consumption_card.findChild(QLabel, "stat_value").setText("0.00 J")
            self.method_count_card.findChild(QLabel, "stat_value").setText("0")
            self.max_consumption_card.findChild(QLabel, "stat_value").setText("0.00 J")
            return

        total_consumption = sum(ct.consumption for ct in source_trees.values())
        
        # Update statistics cards
        self.total_consumption_card.findChild(QLabel, "stat_value").setText(f"{total_consumption:.2f} J")
        self.method_count_card.findChild(QLabel, "stat_value").setText(f"{len(source_trees)}")
        
        max_consumption = 0
        if source_trees:
           max_consumption = max(ct.consumption for ct in source_trees.values())
        self.max_consumption_card.findChild(QLabel, "stat_value").setText(f"{max_consumption:.2f} J")
        
        # Build hierarchy (merged tree)
        root_nodes = [] # List of TreeNode
        
        for calltree in source_trees.values():
            # Parse the calltree name (semicolon-separated) to build hierarchy
            method_names = calltree.name.split(';')
            
            if not method_names:
                continue
                
            root_name = method_names[0]
            # Create a new root node for each calltree entry (no merging)
            root_node = TreeNode(root_name)
            
            # Add this call path to the root node (skip root name in parts as it's the node itself)
            if len(method_names) > 1:
                root_node.add_path(method_names[1:], calltree.consumption)
            else:
                # Just the root node itself has consumption
                root_node.consumption += calltree.consumption
                root_node.call_count += 1
                
            root_nodes.append(root_node)

        # Render roots
        sorted_roots = sorted(root_nodes, key=lambda x: x.consumption, reverse=True)
        
        for node in sorted_roots:
            self.render_tree_node(None, node, total_consumption)

    
    def update_stat_card(self, card, value):
        """Update a statistics card value."""
        value_label = card.findChild(QLabel, "stat_value")
        if value_label:
            value_label.setText(value)
    
    def extract_method_name(self, full_name):
        """Extract the method name from full path."""
        if '.' in full_name:
            return full_name.split('.')[-1]
        return full_name
    
    
    def render_tree_node(self, parent_item, node, total_consumption, depth=0):
        """Render a TreeNode and its children recursively.
        
        Args:
            parent_item: Parent QTreeWidgetItem (None for root)
            node: TreeNode to render
            total_consumption: Total consumption for percentage calculation
            depth: Current depth in the tree (for visual hierarchy)
        """
        # Create tree item
        if parent_item is None:
            item = QTreeWidgetItem(self.tree)
        else:
            item = QTreeWidgetItem(parent_item)
        
        # Check if it has children
        has_children = len(node.children) > 0
        
        # Calculate percentage
        percentage = node.get_percentage(total_consumption)
        
        # Extra info for display
        extra_info = "" 
        
        # Determine visibility of metrics
        show_metrics = not has_children

        # Create the card widget
        card_widget, chevron_label = self.create_method_card(
            self.extract_method_name(node.name),
            node.consumption,
            percentage,
            extra_info,
            node.name,
            has_children,
            depth,
            show_metrics=show_metrics
        )
        
        # Store item data
        item.setData(0, Qt.ItemDataRole.UserRole, {
            "type": "tree_node",
            "node": node,
            "name": node.name
        })
        self.tree.setItemWidget(item, 0, card_widget)
        self.all_items.append(item)
        
        # Store chevron reference
        if chevron_label:
            self.item_chevrons[id(item)] = chevron_label
        
        # Recursively render children (sorted by consumption)
        if has_children:
            sorted_children = sorted(node.children.values(), 
                                    key=lambda x: x.consumption, 
                                    reverse=True)
            for child_node in sorted_children:
                self.render_tree_node(item, child_node, total_consumption, depth + 1)

    
    def create_method_card(self, name, consumption, percentage, extra_info, full_name, has_children=False, depth=0, show_metrics=True):
        """Create a card widget for a method or call tree.
        
        Args:
            depth: Depth in the tree hierarchy (for visual indicators)
            show_metrics: Whether to display consumption and percentage
        """
        # Container to hold chevron + card
        container = QWidget()
        container_layout = QHBoxLayout(container)
        container_layout.setContentsMargins(0, 0, 0, 0)
        container_layout.setSpacing(8)
        
        # Add left margin for hierarchy depth
        if depth > 0:
            spacer = QWidget()
            spacer.setFixedWidth(depth * 20)
            container_layout.addWidget(spacer)
        
        # Chevron arrow indicator (if has children) - OUTSIDE the card
        chevron_label = None
        if has_children:
            chevron_label = QLabel("▶")  # Right arrow (collapsed by default)
            chevron_label.setStyleSheet(get_chevron_style(False))
            chevron_label.setFixedWidth(15)
            chevron_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            container_layout.addWidget(chevron_label)
        else:
            # Add spacer if no chevron to maintain alignment
            spacer = QLabel("")
            spacer.setFixedWidth(15)
            container_layout.addWidget(spacer)
        
        # The actual card
        card = QFrame()
        
        # Use color only if showing metrics, else white/neutral
        bg_color = self.get_consumption_color(percentage) if show_metrics else "#ffffff"
        
        # Add left border for hierarchy visualization
        border_left = "5px solid #BDBDBD" if depth > 0 else "none"
        
        # Compact card styling
        card.setObjectName("node_card")
        card.setStyleSheet(f"""
            #node_card {{
                background-color: {bg_color};
                border: 1px solid #e0e0e0;
                border-left: {border_left};
                border-radius: 6px;
                padding: 8px 12px;
            }}
            #node_card:hover {{
                border: 1px solid #2196F3;
                border-left: {border_left};
            }}
        """)
        card.setMinimumHeight(40)
        card.setMaximumHeight(40)
        
        card_layout = QHBoxLayout(card)
        card_layout.setContentsMargins(4, 4, 4, 4)
        card_layout.setSpacing(10)
        
        # Method name
        name_label = QLabel(name)
        name_label.setStyleSheet(get_node_label_style('name'))
        name_label.setToolTip(full_name)
        name_label.setMinimumWidth(150)
        card_layout.addWidget(name_label)
        
        if show_metrics:
            # Consumption
            consumption_label = QLabel(f"⚡ {consumption:.2f} J")
            consumption_label.setStyleSheet(get_node_label_style('consumption'))
            consumption_label.setMinimumWidth(100)
            card_layout.addWidget(consumption_label)
            
            # Percentage
            percentage_label = QLabel(f"{percentage:.1f}%")
            percentage_label.setStyleSheet(get_node_label_style('percentage'))
            percentage_label.setMinimumWidth(50)
            card_layout.addWidget(percentage_label)
        
        # Extra info if present and not empty
        if extra_info:
            extra_label = QLabel(extra_info)
            extra_label.setStyleSheet(get_node_label_style('extra'))
            card_layout.addWidget(extra_label)
        
        card_layout.addStretch()
        
        container_layout.addWidget(card, 1)
        
        return container, chevron_label
    
    def on_item_clicked(self, item, column):
        """Handle item click - only for expand/collapse, no popups."""
        # Just toggle expansion, no dialog popups
        if item.childCount() > 0:
            should_expand = not item.isExpanded()
            item.setExpanded(should_expand)
            
            # If expanding, also expand all children recursively
            if should_expand:
                self._recursive_expand(item)
    
    def _recursive_expand(self, item):
        """Recursively expand all children of an item."""
        for i in range(item.childCount()):
            child = item.child(i)
            child.setExpanded(True)
            self._recursive_expand(child)

    def on_item_expanded(self, item):
        """Handle item expansion - update chevron to down arrow."""
        if id(item) in self.item_chevrons:
            self.item_chevrons[id(item)].setText("▼")
            self.item_chevrons[id(item)].setStyleSheet(get_chevron_style(True))
    
    def on_item_collapsed(self, item):
        """Handle item collapse - update chevron to right arrow."""
        if id(item) in self.item_chevrons:
            self.item_chevrons[id(item)].setText("▶")
            self.item_chevrons[id(item)].setStyleSheet(get_chevron_style(False))
    
    def filter_tree(self, text):
        """Filter tree items based on search text."""
        if not text:
            # Restore expansion state if available
            if self.expansion_state:
                for item in self.all_items:
                    item.setHidden(False)
                    if id(item) in self.expansion_state:
                        # Restore saved state
                        is_expanded = self.expansion_state[id(item)]
                        item.setExpanded(is_expanded)
                        # Ensure chevrons are updated
                        if is_expanded:
                            self.on_item_expanded(item)
                        else:
                            self.on_item_collapsed(item)
                
                self.expansion_state.clear()
            else:
                # Default behavior if no state saved
                for item in self.all_items:
                    item.setHidden(False)
            return

        # If starting a new search (and state not saved yet), save current state
        if not self.expansion_state:
            for item in self.all_items:
                self.expansion_state[id(item)] = item.isExpanded()
        
        text = text.lower()
        
        # First hide all
        for item in self.all_items:
            item.setHidden(True)
            
        # Then show matches and their parents/children
        for item in self.all_items:
            data = item.data(0, Qt.ItemDataRole.UserRole)
            if data and 'name' in data:
                name = data['name'].lower()
                if text in name:
                    # Show this item
                    item.setHidden(False)
                    
                    # Show all parents
                    parent = item.parent()
                    while parent:
                        parent.setHidden(False)
                        parent.setExpanded(True)
                        parent = parent.parent()

    def _show_subtree(self, item):
        """Recursively show item and its children."""
        item.setHidden(False)
        for i in range(item.childCount()):
            self._show_subtree(item.child(i))

    def filter_items(self, text):
        """Alias for compatibility."""
        self.filter_tree(text)
