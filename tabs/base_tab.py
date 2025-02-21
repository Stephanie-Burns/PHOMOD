
from tkinter import ttk


class BaseTab(ttk.Frame):
    def __init__(self, parent, controller, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.controller = controller

    def bind_help_message(self, widget, help_text=None):
        if help_text is not None:
            widget.bind("<Enter>", lambda event: self.controller.update_status_bar_text(help_text))
        widget.bind("<Leave>", lambda event: self.controller.update_status_bar_text("Ready"))
