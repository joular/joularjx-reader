def get_progress_color(percentage):
    """Get color based on percentage value."""
    try:
        if percentage >= 70:
            return "#dc3545"  # Rouge pour haute consommation
        elif percentage >= 40:
            return "#fd7e14"  # Orange pour consommation moyenne-haute
        elif percentage >= 20:
            return "#28a745"  # Vert pour consommation moyenne
        else:
            return "#17a2b8"  # Bleu clair pour faible consommation
    except Exception:
        # Return a default color in case of error
        return "#6c757d"  # Gray as fallback

def get_table_style():
    """Get the common table style."""
    return """
        QTableWidget {
            selection-background-color: #e3f2fd;
            selection-color: black;
        }
        QTableWidget::item:selected {
            background-color: #e3f2fd;
            border-top: 2px solid #2196f3;
            border-bottom: 2px solid #2196f3;
        }
    """

def get_header_style():
    """Get the common header style."""
    return """
        QHeaderView::section {
            background-color: white;
            padding: 5px;
            border: none;
            border-bottom: 2px solid #f0f0f0;
            font-weight: bold;
        }
    """

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