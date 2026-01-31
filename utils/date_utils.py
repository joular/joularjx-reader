import os
from datetime import datetime
from typing import Optional


def format_timestamp_from_folder(folder_name: str) -> Optional[str]:
    try:
        parts = folder_name.split('-')
        if len(parts) > 1:
            timestamp_str = parts[1]
            timestamp = float(timestamp_str)
            
            if timestamp > 1000000000000:
                timestamp = timestamp / 1000.0
                
            return datetime.fromtimestamp(timestamp).strftime("%d/%m/%Y %H:%M:%S")
    except (ValueError, IndexError):
        pass
    
    return None


def get_directory_date(path: str) -> str:
    try:
        folder_name = os.path.basename(path)
        
        date_str = format_timestamp_from_folder(folder_name)
        if date_str:
            return date_str
        
        mtime = os.path.getmtime(path)
        return datetime.fromtimestamp(mtime).strftime("%d/%m/%Y %H:%M:%S")
    except Exception:
        return "Unknown"


def format_pid_date_short(pid_full: str) -> Optional[str]:
    try:
        parts = pid_full.split('-')
        if len(parts) > 1:
            timestamp = float(parts[1])
            if timestamp > 1000000000000:
                timestamp = timestamp / 1000.0
            
            dt = datetime.fromtimestamp(timestamp)
            return dt.strftime("%d/%m/%Y %H:%M")
    except Exception:
        pass
    
    return None
