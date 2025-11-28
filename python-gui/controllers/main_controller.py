# controllers/main_controller.py
class MainController:
    def __init__(self, view, model):
        self.view = view
        self.model = model

        # Connect semantic signals to controller actions
        self.view.navigation.view_home.connect(lambda: self.switch_screen("Home"))
        self.view.navigation.view_all_pids.connect(lambda: self.switch_screen("All PIDs"))
        self.view.navigation.view_pid_selected.connect(lambda: self.switch_screen("PID Selected"))

        # Optionally handle toggle_requested for logging or model update
        self.view.navigation.toggle_requested.connect(self.on_toggle)

        # set initial screen from model
        self.switch_screen(self.model.get_screen())

    def switch_screen(self, name: str):
        self.model.set_screen(name)
        # find index of name in menu_list
        menu_list = [m["name"] for m in self.view.navigation.controller.menu_list]
        try:
            idx = menu_list.index(name)
        except ValueError:
            idx = 0
        self.view.stack.setCurrentIndex(idx)

    def on_toggle(self):
        # placeholder if you want to persist this state
        pass
