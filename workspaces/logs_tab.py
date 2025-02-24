
import logging
import tkinter as tk
from tkinter import filedialog

from phomod_widgets import PHOMODFrame
from config.logger_config import LOG_BUFFER

app_logger = logging.getLogger('FOMODLogger')


class TextHandler(logging.Handler):
    """A logging handler that writes log messages to a Tkinter Text widget with syntax highlighting."""

    def __init__(self, text_widget):
        super().__init__()
        self.text_widget = text_widget

    def emit(self, record):
        """Handles log message emission with syntax highlighting."""
        log_entry = self.format(record) + "\n"
        level = record.levelname.lower()
        self.text_widget.after(0, self.append_log, log_entry, level)

    def append_log(self, log_entry, level):
        """Appends log entry to the Text widget with color formatting."""
        self.text_widget.configure(state="normal")  # Enable editing
        self.text_widget.insert(tk.END, log_entry, level)  # Insert log message with tag
        self.text_widget.configure(state="disabled")  # Disable editing
        self.text_widget.see(tk.END)  # Auto-scroll to latest log



class LogsTab(PHOMODFrame):
    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        app_logger.info("Initializing LogsTab")
        self.create_widgets()
        self.setup_logging()
        self.create_context_menu()
        self.flush_buffered_logs()  # Flush early logs

    def create_widgets(self):
        # ttk.Label(self, text="Event Logs:").pack(anchor="w", padx=5, pady=5)

        # Create scrollable text frame
        text_frame = tk.Frame(self)
        text_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        log_font = ("Courier", 11)  # Font for better emoji support

        # Create Text widget with a Scrollbar
        self.log_text = tk.Text(
            text_frame, wrap=tk.WORD, height=10, state="disabled",
            bg="black", fg="white", font=log_font, spacing1=4, spacing3=4
        )
        scrollbar = tk.Scrollbar(text_frame, command=self.log_text.yview)
        self.log_text.configure(yscrollcommand=scrollbar.set)

        self.log_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Define color tags for log levels
        self.log_text.tag_configure("info", foreground="lightblue")
        self.log_text.tag_configure("debug", foreground="gray")
        self.log_text.tag_configure("warning", foreground="yellow")
        self.log_text.tag_configure("error", foreground="red")
        self.log_text.tag_configure("critical", foreground="magenta", font=("Courier", 11, "bold"))

        # Bind right-click event to open context menu
        self.log_text.bind("<Button-3>", self.show_context_menu)  # Windows & Linux
        self.log_text.bind("<Control-Button-1>", self.show_context_menu)  # macOS

        app_logger.info("LogsTab widgets created")

    def setup_logging(self):
        """Attach a custom logging handler to the app_logger for real-time logging with syntax highlighting."""
        text_handler = TextHandler(self.log_text)
        formatter = logging.Formatter('%(asctime)s - %(levelname)-8s | %(message)s', datefmt='%H:%M:%S')
        text_handler.setFormatter(formatter)

        # Add the handler only if it isn't already added
        if not any(isinstance(h, TextHandler) for h in app_logger.handlers):
            app_logger.addHandler(text_handler)

        app_logger.info("Logging redirected to LogsTab")

    def flush_buffered_logs(self):
        """Flush buffered logs into the Text widget when ready."""
        while LOG_BUFFER:
            log_entry = LOG_BUFFER.popleft()  # Remove oldest entry
            self.log_text.configure(state="normal")
            self.log_text.insert(tk.END, log_entry + "\n", "info")
            self.log_text.configure(state="disabled")
            self.log_text.see(tk.END)

    def create_context_menu(self):
        """Creates a right-click context menu for logs."""
        self.context_menu = tk.Menu(self, tearoff=0)
        self.context_menu.add_command(label="Copy", command=self.copy_selected_text)
        self.context_menu.add_command(label="Clear Logs", command=self.clear_logs)
        self.context_menu.add_command(label="Save Logs", command=self.save_logs)

    def show_context_menu(self, event):
        """Displays the right-click context menu."""
        self.context_menu.post(event.x_root, event.y_root)

    def copy_selected_text(self):
        """Copies selected text to the clipboard."""
        try:
            selected_text = self.log_text.get(tk.SEL_FIRST, tk.SEL_LAST)
            self.clipboard_clear()
            self.clipboard_append(selected_text)
        except tk.TclError:
            pass  # No selection, do nothing

    def clear_logs(self):
        """Clears all logs from the Text widget."""
        self.log_text.configure(state="normal")
        self.log_text.delete("1.0", tk.END)
        self.log_text.configure(state="disabled")

    def save_logs(self):
        """Saves logs to a file."""
        log_content = self.log_text.get("1.0", tk.END).strip()
        if not log_content:
            return  # No logs to save

        file_path = filedialog.asksaveasfilename(
            defaultextension=".log",
            filetypes=[("Log Files", "*.log"), ("Text Files", "*.txt"), ("All Files", "*.*")],
            title="Save Log File"
        )
        if file_path:
            with open(file_path, "w", encoding="utf-8") as log_file:
                log_file.write(log_content)
