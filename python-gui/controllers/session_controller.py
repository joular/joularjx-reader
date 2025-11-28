class SessionController:
    def __init__(self):
        self.folder_path = None
        self.pids = []

    def set_folder(self, folder_path: str, pids: list[dict]):
        self.folder_path = folder_path
        self.pids = pids

    def get_pids(self):
        return self.pids

    def get_folder(self):
        return self.folder_path
