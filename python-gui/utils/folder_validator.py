import os
import re

def is_valid_pid_folder(folder_path: str) -> bool:
    required_subdirs = ["all", "app"]
    for subdir in required_subdirs:
        if not os.path.isdir(os.path.join(folder_path, subdir)):
            return False
    return True

def extract_pids_from_root(root_path: str) -> list[dict]:
    pid_pattern = re.compile(r"^\d+-\d+$")
    pids = []

    for entry in os.listdir(root_path):
        full_path = os.path.join(root_path, entry)
        if os.path.isdir(full_path) and pid_pattern.match(entry):
            if is_valid_pid_folder(full_path):
                pids.append({
                    "pid": entry,
                    "path": full_path
                })
    return pids
