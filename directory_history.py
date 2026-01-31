import json
import os
from pathlib import Path
from typing import List, Optional
from datetime import datetime, timedelta

class DirectoryHistoryError(Exception):
    """Base exception class for DirectoryHistory errors."""
    pass

class DirectoryHistoryLoadError(DirectoryHistoryError):
    """Raised when there's an error loading the directory history."""
    pass

class DirectoryHistorySaveError(DirectoryHistoryError):
    """Raised when there's an error saving the directory history."""
    pass

class InvalidDirectoryError(DirectoryHistoryError):
    """Raised when an invalid directory is provided."""
    pass

class DirectoryHistory:
    def __init__(self, history_file: str = "directory_history.json"):
        self.history_file = history_file
        self.max_entries = 6
        self._directories = []  # In-memory cache
        self._last_load = None  # Last load timestamp
        self._cache_duration = timedelta(minutes=5)  # Cache duration
        self.try_delete= True
        self._load_history()


    def _load_history(self) -> None:
        """Load directory history from JSON file with error handling."""
        if self._last_load and datetime.now() - self._last_load < self._cache_duration:
            return

        try:
            if os.path.exists(self.history_file):
                with open(self.history_file, 'r') as f:
                    loaded_data = json.load(f)
                    self._directories = [
                        {
                            "path": str(Path(entry["path"]).resolve()),
                            "date": entry["date"]
                        }
                        for entry in loaded_data
                        if self._is_valid_directory(entry["path"])
                    ]
            else:
                self._directories = []
        except json.JSONDecodeError as e:
            raise DirectoryHistoryLoadError(f"Invalid JSON format in history file: {e}")
        except IOError as e:
            raise DirectoryHistoryLoadError(f"Failed to read history file: {e}")
        except Exception as e:
            if self.try_delete:
                self.try_delete = False
                with open(self.history_file, 'w') as f:
                    f.write('[]')
                self._load_history()
            else:
                raise DirectoryHistoryLoadError(f"Unexpected error while loading history: {e}")
             


        self._last_load = datetime.now()

    def _save_history(self) -> bool:
        """Save directory history to JSON file."""
        try:
            os.makedirs(os.path.dirname(self.history_file) or '.', exist_ok=True)

            with open(self.history_file, 'w') as f:
                json.dump(self._directories, f)
            return True
        except IOError as e:
            raise DirectoryHistorySaveError(f"Failed to write to history file: {e}")
        except OSError as e:
            raise DirectoryHistorySaveError(f"Failed to create directory for history file: {e}")
        except Exception as e:
            raise DirectoryHistorySaveError(f"Unexpected error while saving history: {e}")

    def _is_valid_directory(self, directory: str) -> bool:
        """
        Check if a directory path is valid.
        
        Args:
            directory (str): Directory path to validate
            
        Returns:
            bool: True if directory is valid, False otherwise
        """
        try:
            path = Path(directory)
            return path.exists() and path.is_dir()
        except Exception:
            return False

    def add_directory(self, directory: str) -> bool:
        """Add a directory to history, maintaining max entries limit."""
        try:
            abs_path = str(Path(directory).resolve())

            if not self._is_valid_directory(abs_path):
                raise InvalidDirectoryError(f"Invalid directory path: {directory}")

            existing_entry = next((entry for entry in self._directories if entry["path"] == abs_path), None)
            if existing_entry:
                self._directories.remove(existing_entry)

            self._directories.insert(0, {"path": abs_path, "date": datetime.now().strftime("%d %b %Y")})

            self._directories = self._directories[:self.max_entries]

            return self._save_history()
        except InvalidDirectoryError:
            raise
        except Exception as e:
            raise DirectoryHistorySaveError(f"Error adding directory: {e}")

    def get_directories(self) -> List[dict]:
        """Get list of directories in history."""
        try:
            self._load_history()
            return self._directories.copy()
        except DirectoryHistoryLoadError:
            raise
        except Exception as e:
            raise DirectoryHistoryLoadError(f"Unexpected error getting directories: {e}")

    def clear_history(self) -> bool:
        """
        Clear the directory history.
        
        Returns:
            bool: True if history was cleared successfully, False otherwise
            
        Raises:
            DirectoryHistorySaveError: If there's an error saving the cleared history
        """
        try:
            self._directories = []
            return self._save_history()
        except DirectoryHistorySaveError:
            raise
        except Exception as e:
            raise DirectoryHistorySaveError(f"Unexpected error clearing history: {e}")

    def remove_directory(self, directory: str) -> bool:
        """
        Remove a directory from history.
        
        Args:
            directory (str): Directory path to remove
            
        Returns:
            bool: True if directory was removed successfully, False otherwise
            
        Raises:
            DirectoryHistorySaveError: If there's an error saving the history after removal
        """
        try:
            abs_path = str(Path(directory).resolve())
            
            # Remove if exists
            existing_entry = next((entry for entry in self._directories if entry["path"] == abs_path), None)
            if existing_entry:
                self._directories.remove(existing_entry)
                return self._save_history()
            return False
            
        except DirectoryHistorySaveError:
            raise
        except Exception as e:
            raise DirectoryHistorySaveError(f"Error removing directory: {e}")