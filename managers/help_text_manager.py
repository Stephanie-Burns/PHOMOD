
import logging
import tkinter as tk

app_logger = logging.getLogger('PHOMODLogger')

class HelpTextManager:
    """Centralized help text manager that binds tooltips to widgets and updates a status bar with a delay."""
    def __init__(self, status_var: tk.StringVar, scheduler_widget: tk.Widget, delay: int = 150):
        """
        :param status_var: The StringVar used by the status bar.
        :param scheduler_widget: A Tk widget (here, the StatusBar) used for scheduling updates via its after() method.
        :param delay: Delay in milliseconds before updating the status to avoid rapid flickering.
        """
        self.status_var = status_var
        self.scheduler_widget = scheduler_widget
        self.delay = delay
        self._after_id = None
        self.current_status = status_var.get()
        app_logger.debug(f"HelpTextManager initialized with delay {delay}ms.")

    def bind_help(self, widget, help_text: str):
        """
        Binds help text to a widget. On <Enter> it schedules an update, and on <Leave> it reverts to "Ready".
        """
        if help_text:
            widget.bind("<Enter>", lambda event: self.schedule_update(help_text))
            widget.bind("<Leave>", lambda event: self.schedule_update("Ready"))
            app_logger.info(f"🔗 Help text bound: '{help_text}' to {widget.__class__.__name__}")

    def schedule_update(self, message: str):
        """
        Schedules an update to the status bar after a short delay, cancelling any previous pending update.
        """
        if self._after_id:
            self.scheduler_widget.after_cancel(self._after_id)
            self._after_id = None
            app_logger.debug("⏹️ Previous status update canceled.")

        if message != self.current_status:
            self._after_id = self.scheduler_widget.after(self.delay, lambda: self._do_update(message))
            app_logger.debug(f"⏱️ Scheduled status update: '{message}' in {self.delay}ms.")

    def _do_update(self, message: str):
        """Executes the update to the status bar and logs the change."""
        if message != self.current_status:
            self.status_var.set(message)
            app_logger.info(f"📢 Status updated: {message}")
            self.current_status = message
        self._after_id = None
