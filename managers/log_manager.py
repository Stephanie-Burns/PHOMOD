import logging
from collections import deque
import tkinter as tk
from tkinter import filedialog

app_logger = logging.getLogger("PHOMODLogger")

class LogManager:
    """
    Manages log buffering and integration with the UI.
    Provides methods to attach a TextHandler to a Tkinter Text widget,
    flush buffered logs, and perform common log operations.
    """
    def __init__(self, max_buffer=100, text_widget=None):
        self.log_buffer = deque(maxlen=max_buffer)
        self.logger = logging.getLogger("PHOMODLogger")
        self.text_widget = text_widget  # Optional reference to the log widget

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
            self._update_widget(lambda widget: widget.insert(tk.END, entry + "\n", "info"))
        self._update_widget(lambda widget: widget.see(tk.END))

    def attach_text_handler(self, text_widget=None):
        """Attaches a TextHandler to the logger for real-time logging."""
        if text_widget:
            self.text_widget = text_widget

        if not self.text_widget:
            app_logger.warning("No log widget provided to attach TextHandler.")
            return

        # Attach a TextHandler only if one isn’t already attached
        if not any(isinstance(h, TextHandler) for h in self.logger.handlers):
            handler = TextHandler(self.text_widget)
            formatter = logging.Formatter(
                '%(asctime)s - %(levelname)-8s | %(message)s', datefmt='%H:%M:%S'
            )
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
            app_logger.info("📥 TextHandler attached to logger.")

    def save_logs_to_file(self):
        """Saves the contents of the stored Text widget to a file selected by the user."""
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
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(log_content)

    def _update_widget(self, action):
        """Helper method to update the Text widget’s state safely."""
        try:
            if self.text_widget:
                self.text_widget.configure(state="normal")
                action(self.text_widget)
                self.text_widget.configure(state="disabled")
        except tk.TclError as e:
            app_logger.error(f"Error updating log widget: {e}")

class TextHandler(logging.Handler):
    """
    A logging handler that writes log messages to a Tkinter Text widget
    with syntax highlighting.
    """
    def __init__(self, text_widget):
        super().__init__()
        self.text_widget = text_widget

    def emit(self, record):
        log_entry = self.format(record) + "\n"
        level = record.levelname.lower()
        self.text_widget.after(0, self.append_log, log_entry, level)

    def append_log(self, log_entry, level):
        try:
            self.text_widget.configure(state="normal")
            self.text_widget.insert(tk.END, log_entry, level)
            self.text_widget.configure(state="disabled")
            self.text_widget.see(tk.END)
        except tk.TclError as e:
            app_logger.error(f"Error appending log: {e}")
