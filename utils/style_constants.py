# Primary / brand colors
COLOR_PRIMARY = "#0D6EFD"
COLOR_PRIMARY_HOVER = "#0B5ED7"
COLOR_PRIMARY_LIGHT = "#E7F1FF"

# Text colors (from darkest to lightest)
COLOR_TEXT_PRIMARY = "#212529"
COLOR_TEXT_SECONDARY = "#6C757D"
COLOR_TEXT_TERTIARY = "#ADB5BD"
COLOR_TEXT_DARK = "#1A1D21"
COLOR_TEXT_MEDIUM = "#1E293B"
COLOR_TEXT_LIGHT = "#64748B"
COLOR_TEXT_GRAY = "#757575"
COLOR_TEXT_LIGHT_GRAY = "#9E9E9E"
COLOR_TEXT_DARK_GRAY = "#424242"
COLOR_TEXT_MID_GRAY = "#495057"
COLOR_TEXT_SELECTION = "#1565C0"
COLOR_TEXT_METRIC = "#212121"
COLOR_TEXT_METRIC_TITLE = "#616161"

# Background colors
COLOR_BG_WHITE = "#FFFFFF"
COLOR_BG_LIGHT = "#F8F9FA"
COLOR_BG_LIGHTER = "#FAFAFA"
COLOR_BG_GRAY = "#F1F3F5"
COLOR_BG_SELECTION = "#E3F2FD"
COLOR_BG_HOVER = "#F5F5F5"
COLOR_BG_ALTERNATE = "#F9F9F9"

# Border / separator colors
COLOR_BORDER_LIGHT = "#DEE2E6"
COLOR_BORDER_LIGHTER = "#E9ECEF"
COLOR_BORDER_DARK = "#E0E0E0"
COLOR_BORDER_DARKER = "#c0c0c0"
COLOR_BORDER_SEPARATOR = "#E2E8F0"
COLOR_BORDER_CELL_BOTTOM = "#e0e0e0"
COLOR_BORDER_CELL_RIGHT = "#f0f0f0"
COLOR_BORDER_TABLE = "#F0F0F0"
COLOR_BORDER_GRAY = "#ccc"
COLOR_BORDER_LIGHT_GRAY = "#ddd"
COLOR_BORDER_HEADER = "#EEEEEE"
COLOR_BORDER_PRIMARY = "#2196F3"

# Status / semantic colors
COLOR_SUCCESS = "#28a745"
COLOR_WARNING = "#fd7e14"
COLOR_DANGER = "#dc3545"
COLOR_INFO = "#17a2b8"

# "Total" row highlight (used in method tables)
COLOR_TOTAL_BG = "#e3f2fd"
COLOR_TOTAL_INDICATOR = "rgb(0, 0, 0)"
COLOR_TOTAL_BORDER = "#000000"

# Accent colors (used in call-tree node badges, etc.)
COLOR_ACCENT_GREEN = "#86EFC5"
COLOR_ACCENT_PURPLE = "#5D5FEF"
COLOR_ACCENT_BLACK = "#000000"

# Font families
FONT_FAMILY_PRIMARY = "Segoe UI, sans-serif"
FONT_FAMILY_MONO = "Consolas, monospace"
FONT_FAMILY_ARIAL = "Arial"

# Font sizes (CSS strings, smallest → largest)
FONT_SIZE_TINY = "9px"
FONT_SIZE_SMALL = "10px"
FONT_SIZE_NORMAL = "11px"
FONT_SIZE_MEDIUM = "12px"
FONT_SIZE_LARGE = "13px"
FONT_SIZE_XLARGE = "14px"
FONT_SIZE_XXLARGE = "15px"
FONT_SIZE_TITLE = "16px"
FONT_SIZE_ICON_MEDIUM = "18px"
FONT_SIZE_ICON_LARGE = "20px"
FONT_SIZE_METRIC_VALUE = "22px"
FONT_SIZE_H2 = "24px"
FONT_SIZE_H1 = "28px"
FONT_SIZE_HERO = "30px"
FONT_SIZE_MEGA = "32px"

# Spacing tokens (CSS strings)
SPACING_TINY = "2px"
SPACING_SMALL = "5px"
SPACING_MEDIUM = "10px"
SPACING_LARGE = "15px"
SPACING_XLARGE = "20px"
SPACING_XXLARGE = "25px"

# Border radius tokens
BORDER_RADIUS_SMALL = "3px"
BORDER_RADIUS_MEDIUM = "6px"
BORDER_RADIUS_LARGE = "8px"
BORDER_RADIUS_XLARGE = "10px"
BORDER_RADIUS_XXLARGE = "12px"
BORDER_RADIUS_PILL = "18px"

# Padding tokens
PADDING_SMALL = "8px"
PADDING_MEDIUM = "10px"
PADDING_LARGE = "12px"
PADDING_XLARGE = "15px"

# pyqtgraph plot configuration
GRAPH_STYLE = {
    'background': '#fafafa',
    'grid_alpha': 0.2,
    'axis_color': '#666',
    'axis_width': 1,
    'curve_width': 2,
    'crosshair_color': '#666',
    'crosshair_style': 'dash',
    'tooltip_background': (255, 255, 255, 230),
    'tooltip_border': '#ccc',
    'font_size': '11pt',
    'title_size': '16pt',
    'title_color': '#1a1a1a',
}

# Color used for the aggregated "Total" curve in the analysis graph
TOTAL_COLOR = (0, 0, 0)

# Ordered palette for the first 10 methods in the analysis graph
METHOD_COLORS = [
    (220, 53, 69),
    (0, 123, 255),
    (40, 167, 69),
    (253, 126, 20),
    (111, 66, 193),
    (32, 201, 151),
    (232, 62, 140),
    (52, 58, 64),
    (255, 193, 7),
    (23, 162, 184),
]

