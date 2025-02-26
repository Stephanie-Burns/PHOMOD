
import logging
import tkinter as tk
from tkinter import ttk

from managers import HelpTextManager

app_logger = logging.getLogger('PHOMODLogger')


class StatusBar(ttk.Label):
    """
    A dedicated status bar widget that encapsulates its StringVar and the HelpTextManager.
    This class handles delayed updates and help text bindings.
    """
    def __init__(self, parent, initial_text="Ready", delay=300, **kwargs):
        self.status_var = tk.StringVar(value=initial_text)

        super().__init__(parent, textvariable=self.status_var, relief=tk.SUNKEN, anchor="w", **kwargs)
        self.help_manager = HelpTextManager(self.status_var, self, delay=delay)
        app_logger.info("StatusBar created with initial text: '{}'".format(initial_text))

    def update_text(self, message):
        """
        Immediately updates the status text.
        Use this if you need to force an immediate change (bypassing any scheduled delay).
        """
        if message != self.status_var.get():
            self.status_var.set(message)

            app_logger.info(f"📢 Status immediately updated: {message}")

    def schedule_text_update(self, message):
        """
        Schedules an update to the status text using the help manager.
        This is typically called via help text events.
        """
        self.help_manager.schedule_update(message)
