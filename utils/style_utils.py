

def get_progress_color(percentage):
    """Get color based on percentage value."""
    from .style_constants import COLOR_DANGER, COLOR_WARNING, COLOR_SUCCESS, COLOR_INFO, COLOR_TEXT_SECONDARY
    try:
        if percentage >= 70:
            return COLOR_DANGER  # Red
        elif percentage >= 40:
            return COLOR_WARNING  # Orange
        elif percentage >= 20:
            return COLOR_SUCCESS  # Green
        else:
            return COLOR_INFO  # Blue
    except Exception:
        return COLOR_TEXT_SECONDARY  # Gray as fallback





def get_progress_bar_style(bar_color):
    """Get the common progress bar style."""
    return f"""
        QProgressBar {{
            border: none;
            background-color: #e9ecef;
            border-radius: 3px;
            text-align: center;
            margin: 2px;
            min-height: 10px;
            max-height: 10px;
            padding: 0px;
        }}
        QProgressBar::chunk {{
            background-color: {bar_color};
            border-radius: 3px;
            min-height: 10px;
            max-height: 10px;
            padding: 0px;
        }}
    """

def get_cell_widget_style(bg_color):
    from .style_constants import COLOR_BORDER_CELL_BOTTOM, COLOR_BORDER_CELL_RIGHT
    return f"""
        background-color: {bg_color};
        border-bottom: 1px solid {COLOR_BORDER_CELL_BOTTOM};
        border-right: 1px solid {COLOR_BORDER_CELL_RIGHT};
    """

def get_color_indicator_style(r, g, b, border_color=None, size=20):
    from .style_constants import BORDER_RADIUS_SMALL, COLOR_BORDER_GRAY
    if border_color is None:
        border_color = COLOR_BORDER_GRAY
    return f"""
        background-color: rgb({r}, {g}, {b});
        border: 1px solid {border_color};
        border-radius: {BORDER_RADIUS_SMALL};
    """

def get_total_color_indicator_style():
    from .style_constants import BORDER_RADIUS_SMALL, COLOR_TOTAL_INDICATOR, COLOR_TOTAL_BORDER
    return f"""
        background-color: {COLOR_TOTAL_INDICATOR};
        border: 2px solid {COLOR_TOTAL_BORDER};
        border-radius: {BORDER_RADIUS_SMALL};
    """

def get_label_style(font_size, color, weight="normal", family=None):
    from .style_constants import FONT_FAMILY_PRIMARY
    if family is None:
        family = FONT_FAMILY_PRIMARY
    
    weight_class = ""
    if weight == "bold":
        weight_class = "font-weight: bold;"
    elif isinstance(weight, int):
        weight_class = f"font-weight: {weight};"
    
    return f"""
        font-size: {font_size};
        color: {color};
        {weight_class}
        font-family: "{family}";
        background-color: transparent;
        border: none;
    """

def get_title_style(level="h1"):
    from .style_constants import (
        FONT_SIZE_MEGA, FONT_SIZE_H1, FONT_SIZE_H2, FONT_SIZE_ICON_MEDIUM,
        COLOR_TEXT_PRIMARY, COLOR_TEXT_DARK, FONT_SIZE_HERO, FONT_SIZE_XXLARGE,
        COLOR_TEXT_MEDIUM
    )
    
    styles = {
        'hero': {'size': FONT_SIZE_HERO, 'color': COLOR_TEXT_DARK, 'weight': 800},
        'h1': {'size': FONT_SIZE_H1, 'color': COLOR_TEXT_PRIMARY, 'weight': 'bold'},
        'h2': {'size': FONT_SIZE_H2, 'color': COLOR_TEXT_PRIMARY, 'weight': 'bold'},
        'h3': {'size': FONT_SIZE_ICON_MEDIUM, 'color': COLOR_TEXT_PRIMARY, 'weight': 'bold'},
        'section': {'size': FONT_SIZE_XXLARGE, 'color': COLOR_TEXT_MEDIUM, 'weight': 700},
    }
    
    style = styles.get(level, styles['h1'])
    return get_label_style(style['size'], style['color'], style['weight'])

def get_icon_style(size):
    return f"font-size: {size};"

def get_separator_style():
    from .style_constants import COLOR_BORDER_SEPARATOR
    return f"color: {COLOR_BORDER_SEPARATOR};"

def get_description_style():
    from .style_constants import FONT_SIZE_XXLARGE, COLOR_TEXT_LIGHT
    return get_label_style(FONT_SIZE_XXLARGE, COLOR_TEXT_LIGHT)

def get_help_text_style():
    from .style_constants import FONT_SIZE_XLARGE, COLOR_TEXT_LIGHT
    return get_label_style(FONT_SIZE_XLARGE, COLOR_TEXT_LIGHT)

def get_metric_label_style(label_type):
    from .style_constants import (
        FONT_SIZE_NORMAL, FONT_SIZE_METRIC_VALUE, FONT_SIZE_H2,
        COLOR_TEXT_GRAY, COLOR_TEXT_METRIC, FONT_SIZE_LARGE
    )
    
    if label_type == 'title':
        return get_label_style(FONT_SIZE_NORMAL, COLOR_TEXT_GRAY, 500)
    elif label_type == 'value':
        return get_label_style(FONT_SIZE_METRIC_VALUE, COLOR_TEXT_METRIC, 'bold')
    elif label_type == 'dialog_title':
        return f"""
            font-size: {FONT_SIZE_LARGE};
            color: {COLOR_TEXT_GRAY};
            font-weight: 500;
        """
    elif label_type == 'dialog_value':
        return f"""
            font-size: {FONT_SIZE_H2};
            font-weight: bold;
            color: {COLOR_TEXT_METRIC};
        """
    return ""

def get_node_card_style(bg_color, is_expanded=False):
    from .style_constants import (
        COLOR_BORDER_LIGHT, COLOR_BORDER_PRIMARY, BORDER_RADIUS_MEDIUM,
        COLOR_PRIMARY_LIGHT
    )
    
    border_color = COLOR_PRIMARY_LIGHT if is_expanded else COLOR_BORDER_LIGHT
    
    return f"""
        background-color: {bg_color};
        border: 1px solid {border_color};
        border-radius: {BORDER_RADIUS_MEDIUM};
        padding: 12px;
    """

def get_chevron_style(is_expanded):
    from .style_constants import COLOR_TEXT_SECONDARY, FONT_SIZE_MEDIUM
    
    return f"""
        color: {COLOR_TEXT_SECONDARY};
        font-size: {FONT_SIZE_MEDIUM};
        font-weight: bold;
    """

def get_node_label_style(label_type):
    from .style_constants import (
        FONT_SIZE_XLARGE, FONT_SIZE_MEDIUM, FONT_SIZE_LARGE,
        COLOR_TEXT_PRIMARY, COLOR_TEXT_SECONDARY, COLOR_TEXT_LIGHT
    )
    
    styles = {
        'name': {'size': FONT_SIZE_XLARGE, 'color': COLOR_TEXT_PRIMARY, 'weight': 600},
        'consumption': {'size': FONT_SIZE_MEDIUM, 'color': COLOR_TEXT_SECONDARY, 'weight': 'bold'},
        'percentage': {'size': FONT_SIZE_MEDIUM, 'color': COLOR_TEXT_LIGHT, 'weight': 500},
        'extra': {'size': FONT_SIZE_LARGE, 'color': COLOR_TEXT_LIGHT, 'weight': 'normal'},
    }
    
    style = styles.get(label_type, styles['name'])
    return get_label_style(style['size'], style['color'], style['weight'])

def get_legend_box_style(color):
    from .style_constants import BORDER_RADIUS_SMALL, COLOR_BORDER_LIGHT_GRAY
    return f"background-color: {color}; border: 1px solid {COLOR_BORDER_LIGHT_GRAY}; border-radius: {BORDER_RADIUS_SMALL};"

def get_legend_text_style():
    from .style_constants import FONT_SIZE_MEDIUM, COLOR_TEXT_GRAY
    return get_label_style(FONT_SIZE_MEDIUM, COLOR_TEXT_GRAY)

def get_metric_card_container_style(bg_color, border_color):
    from .style_constants import BORDER_RADIUS_LARGE
    return f"""
        background-color: {bg_color};
        border: 2px solid {border_color};
        border-radius: {BORDER_RADIUS_LARGE};
        padding: 12px;
    """

def get_theme_button_style(is_dark_mode):
    if is_dark_mode:
        return """
            QPushButton {
                background-color: #424242;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 8px 16px;
                font-size: 13px;
            }
            QPushButton:hover {
                background-color: #616161;
            }
        """
    else:
        return """
            QPushButton {
                background-color: #F5F5F5;
                color: #424242;
                border: 1px solid #E0E0E0;
                border-radius: 6px;
                padding: 8px 16px;
                font-size: 13px;
            }
            QPushButton:hover {
                background-color: #EEEEEE;
            }
        """
def get_method_box_style(is_last_child):
    from .style_constants import COLOR_ACCENT_GREEN, COLOR_ACCENT_PURPLE, COLOR_BG_WHITE, COLOR_ACCENT_BLACK
    bg_color = COLOR_ACCENT_GREEN if is_last_child else COLOR_ACCENT_PURPLE
    text_color = COLOR_ACCENT_BLACK if is_last_child else COLOR_BG_WHITE
    
    return f"""
        background-color: {bg_color};
        color: {text_color};
        border-radius: 15px;
        padding: 10px 20px;
        font-size: 14px;
    """

def get_close_button_style():
    from .style_constants import COLOR_PRIMARY
    return f"""
        background-color: {COLOR_PRIMARY};
        color: white;
        border: none;
        padding: 8px 16px;
        border-radius: 4px;
        font-weight: bold;
    """

def get_base_dialog_style():
    from .style_constants import COLOR_BG_WHITE
    return f"background-color: {COLOR_BG_WHITE};"

def get_method_entry_style():
    from .style_constants import COLOR_ACCENT_GREEN
    return f"""
        background-color: {COLOR_ACCENT_GREEN};
        border-radius: 4px;
    """

def get_result_text_style(size=14, bold=False):
    from .style_constants import COLOR_ACCENT_BLACK
    weight = "bold" if bold else "normal"
    return f"color: {COLOR_ACCENT_BLACK}; font-size: {size}px; font-weight: {weight};"

def get_progress_wrapper_style(bg_color):
    return f"background-color: {bg_color}; min-height: 10px; max-height: 10px;"