# models/app_model.py
class AppModel:
    """Simple model stockant l'écran courant."""
    def __init__(self):
        self.current_screen = "Home"

    def set_screen(self, screen_name: str):
        self.current_screen = screen_name

    def get_screen(self) -> str:
        return self.current_screen