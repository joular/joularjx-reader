import os
from datetime import datetime
from typing import Optional


def format_timestamp_from_folder(folder_name: str) -> Optional[str]:
    """Extract and format a human-readable date from a JoularJX folder name.

    JoularJX names output folders as ``<pid>-<timestamp>``.  The timestamp
    may be in seconds or milliseconds; values above 1 × 10¹² are treated as
    milliseconds and divided by 1000 before conversion.

    Returns the formatted date string or ``None`` if parsing fails.
    """
    try:
        parts = folder_name.split('-')
        if len(parts) > 1:
            timestamp_str = parts[1]
            timestamp = float(timestamp_str)
            
            # Convert milliseconds → seconds when the value is too large
            if timestamp > 1000000000000:
                timestamp = timestamp / 1000.0
                
            return datetime.fromtimestamp(timestamp).strftime("%d/%m/%Y %H:%M:%S")
    except (ValueError, IndexError):
        pass
    
    return None


def get_directory_date(path: str) -> str:
    """Return a formatted date for a JoularJX output directory.

    First tries to parse the timestamp embedded in the folder name via
    :func:`format_timestamp_from_folder`; falls back to the filesystem
    modification time if that fails.
    """
    try:
        folder_name = os.path.basename(path)
        
        # Prefer the timestamp encoded in the folder name
        date_str = format_timestamp_from_folder(folder_name)
        if date_str:
            return date_str
        
        # Fallback: use the filesystem modification time
        mtime = os.path.getmtime(path)
        return datetime.fromtimestamp(mtime).strftime("%d/%m/%Y %H:%M:%S")
    except Exception:
        return "Unknown"


def format_pid_date_short(pid_full: str) -> Optional[str]:
    """Return a short date string (``dd/mm/yyyy HH:MM``) from a PID folder name.

    Used to populate the compact date label shown alongside the PID in the
    sidebar / navigation panel.  Returns ``None`` when parsing fails.
    """
    try:
        parts = pid_full.split('-')
        if len(parts) > 1:
            timestamp = float(parts[1])
            # Convert milliseconds → seconds when the value is too large
            if timestamp > 1000000000000:
                timestamp = timestamp / 1000.0
            
            dt = datetime.fromtimestamp(timestamp)
            return dt.strftime("%d/%m/%Y %H:%M")
    except Exception:
        pass
    
    return None

