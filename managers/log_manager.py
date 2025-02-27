import logging
import tkinter as tk
from collections import deque
from tkinter import filedialog

app_logger = logging.getLogger("PHOMODLogger")

class LogManager:
    """
    Manages log buffering and integration with a Tkinter Text widget.
    Provides methods to attach a TkTextHandler for real-time logging,
    flush buffered logs, and save log contents to a file.
    """
    def __init__(self, max_buffer=100, text_widget=None):
        self.log_buffer = deque(maxlen=max_buffer)
        self.logger = logging.getLogger("PHOMODLogger")
        self.text_widget = text_widget  # Optional reference to the Text widget

    def set_text_widget(self, text_widget):
        """Stores a reference to the Text widget for log output."""
        self.text_widget = text_widget

    def add_to_buffer(self, log_entry):
        """Adds a log entry to the internal buffer."""
        self.log_buffer.append(log_entry)

    def flush_buffer(self):
        """Flushes all buffered log entries into the stored Text widget."""
        if not self.text_widget:
            app_logger.warning("No log widget set; cannot flush buffered logs.")
            return
        self._update_widget(lambda widget: widget.delete("1.0", tk.END))
        while self.log_buffer:
            entry = self.log_buffer.popleft()
            # Insert the entry with a UI-friendly tag (e.g., "info")
            self._update_widget(lambda widget: widget.insert(tk.END, entry + "\n", "info"))
        self._update_widget(lambda widget: widget.see(tk.END))

    def attach_text_handler(self, text_widget=None):
        """
        Attaches a TkTextHandler to the logger for real-time logging.
        If a text_widget is provided, it will be used.
        This handler uses a custom, UI-friendly formatter.
        """
        if text_widget:
            self.text_widget = text_widget

        if not self.text_widget:
            app_logger.warning("No log widget provided to attach TkTextHandler.")
            return

        # Attach a TkTextHandler only if one isn’t already attached
        if not any(isinstance(h, TkTextHandler) for h in self.logger.handlers):
            handler = TkTextHandler(self.text_widget)
            # Use a simplified formatter for the UI display
            ui_formatter = logging.Formatter('%(levelname)-8s: %(message)s', datefmt='%H:%M:%S')
            handler.setFormatter(ui_formatter)
            self.logger.addHandler(handler)
            app_logger.info("TkTextHandler attached to logger.")

    def save_logs_to_file(self):
        """
        Saves the contents of the Text widget to a file chosen by the user.
        """
        if not self.text_widget:
            app_logger.warning("No log widget available; cannot save logs.")
            return
        log_content = self.text_widget.get("1.0", tk.END).strip()
        if not log_content:
            return
        file_path = filedialog.asksaveasfilename(
            defaultextension=".log",
            filetypes=[("Log Files", "*.log"), ("Text Files", "*.txt"), ("All Files", "*.*")],
            title="Save Log File"
        )
        if file_path:
            try:
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(log_content)
                app_logger.info(f"Logs saved to file: {file_path}")
            except Exception as e:
                app_logger.error(f"Error saving logs to file: {e}")

    def _update_widget(self, action):
        """Helper method to safely update the Text widget’s state."""
        try:
            if self.text_widget:
                self.text_widget.configure(state="normal")
                action(self.text_widget)
                self.text_widget.configure(state="disabled")
        except tk.TclError as e:
            app_logger.error(f"Error updating log widget: {e}")

class TkTextHandler(logging.Handler):
    """
    A logging handler that writes log messages to a Tkinter Text widget.
    It schedules UI updates using the widget's after() method to ensure thread safety.
    """
    def __init__(self, text_widget):
        super().__init__()
        self.text_widget = text_widget

    def emit(self, record):
        try:
            log_entry = self.format(record) + "\n"
        except Exception:
            self.handleError(record)
            return
        level = record.levelname.lower()
        # Schedule appending the log entry on the main thread.
        self.text_widget.after(0, self.append_log, log_entry, level)

    def append_log(self, log_entry, level):
        try:
            self.text_widget.configure(state="normal")
            self.text_widget.insert(tk.END, log_entry, level)
            self.text_widget.configure(state="disabled")
            self.text_widget.see(tk.END)
        except tk.TclError as e:
            app_logger.error(f"Error appending log: {e}")
