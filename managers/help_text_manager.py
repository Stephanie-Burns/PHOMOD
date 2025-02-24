
import logging
import tkinter as tk

app_logger = logging.getLogger('FOMODLogger')


class HelpTextManager:
    """Centralized help text manager that binds tooltips to widgets and updates a status bar."""

    def __init__(self, status_var: tk.StringVar):
        """
        Initializes the help text manager.

        :param status_var: The StringVar used for the status bar.
        """
        self.status_var = status_var

    def bind_help(self, widget, help_text: str):
        """
        Binds a help message to a widget. When hovered, it updates the status bar.

        :param widget: The Tkinter widget to bind the help text to.
        :param help_text: The help text to display when hovering over the widget.
        """
        if help_text:
            widget.bind("<Enter>", lambda event: self.update_status(help_text))
            widget.bind("<Leave>", lambda event: self.update_status("Ready"))
            app_logger.info(f"🔗 Help text bound: '{help_text}' to {widget.__class__.__name__}")

    def update_status(self, message):
        """Updates the status bar text."""
        self.status_var.set(message)
        app_logger.info(f"📢 Status updated: {message}")
