
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
    def __init__(self, max_buffer=100):
        self.log_buffer = deque(maxlen=max_buffer)
        # You might want to expose the underlying logger too
        self.logger = logging.getLogger("PHOMODLogger")

    def add_to_buffer(self, log_entry):
        """Adds a log entry to the internal buffer."""
        self.log_buffer.append(log_entry)

    def flush_buffer_to_widget(self, text_widget):
        """Flushes all buffered log entries into the provided Text widget."""
        text_widget.configure(state="normal")
        while self.log_buffer:
            entry = self.log_buffer.popleft()
            text_widget.insert(tk.END, entry + "\n", "info")
        text_widget.configure(state="disabled")
        text_widget.see(tk.END)

    def attach_text_handler(self, text_widget):
        """Attaches a TextHandler to the logger for real-time logging to the given widget."""
        # Check if a TextHandler is already attached
        if not any(isinstance(h, TextHandler) for h in self.logger.handlers):
            handler = TextHandler(text_widget)
            formatter = logging.Formatter('%(asctime)s - %(levelname)-8s | %(message)s', datefmt='%H:%M:%S')
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
            app_logger.info("📥 TextHandler attached to logger.")

    def save_logs_to_file(self, text_widget):
        """Saves the contents of the Text widget to a file selected by the user."""
        log_content = text_widget.get("1.0", tk.END).strip()
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
        self.text_widget.configure(state="normal")
        self.text_widget.insert(tk.END, log_entry, level)
        self.text_widget.configure(state="disabled")
        self.text_widget.see(tk.END)
