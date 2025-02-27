import logging
import tkinter as tk
from tkinter import filedialog

from phomod_widgets import PHOMODFrame, PHOMODTextArea
from components import MenuItem

app_logger = logging.getLogger("PHOMODLogger")


class BlotterFeedView(PHOMODFrame):
    """Log viewer with syntax highlighting and context menu support."""

    def __init__(self, parent, controller, *args, **kwargs):
        super().__init__(parent, controller=controller, *args, **kwargs)
        app_logger.info(f"🚦 Initializing {self.__class__.__name__}")
        self.controller = controller
        self.log_manager = self.controller.log_manager

        self.create_widgets()
        self._bind_shortcuts()

        # Attach log handling
        self.log_manager.attach_text_handler(self.log_text)
        self.log_manager.set_text_widget(self.log_text)
        self.log_manager.flush_buffer()

    def create_widgets(self):
        """Creates the main text display area for logs."""
        text_frame = PHOMODFrame(self)
        text_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        log_font = ("Courier", 11)

        log_menu_items = [
            MenuItem("Select All", lambda: self.log_text._clipboard_action("select_all"), None, "<Control-a>"),
            MenuItem("Copy", lambda: self.log_text._clipboard_action("copy"), "copy.png", "<Control-c>"),
            MenuItem("Cancel", self.deselect_all, None, "<Escape>"),
            MenuItem("---"),
            MenuItem("Clear Log", self.clear_logs, "clear.png"),
            MenuItem("Save Log", self.save_logs, "save.png"),
            MenuItem("---"),
            MenuItem("Copy All", self.copy_all_logs, "copy_all.png", "<Control-Shift-C>"),
        ]

        self.log_text = PHOMODTextArea(
            text_frame, wrap=tk.WORD, state="disabled",
            bg="black", fg="white", font=log_font, spacing1=4, spacing3=4,
            attach_y=True, custom_menu_items=log_menu_items
        )
        self.log_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Set up syntax highlighting
        self._configure_syntax_highlighting()

        app_logger.info("✅ BlotterFeedView widgets created.")

    def _configure_syntax_highlighting(self):
        """Applies syntax highlighting to different log levels."""
        self.log_text.tag_configure("info", foreground="lightblue")
        self.log_text.tag_configure("debug", foreground="gray")
        self.log_text.tag_configure("warning", foreground="yellow")
        self.log_text.tag_configure("error", foreground="red")
        self.log_text.tag_configure("critical", foreground="magenta", font=("Courier", 11, "bold"))

    def _bind_shortcuts(self):
        """Binds shortcut keys for log interactions."""
        self.log_text.bind("<Escape>", lambda e: self.deselect_all())

    def deselect_all(self):
        """Deselects any text selection."""
        self.log_text.tag_remove(tk.SEL, "1.0", tk.END)

    def clear_logs(self):
        """Clears all log text."""
        self.log_text._clear_text()
        app_logger.info("🗑️ Log viewer cleared.")

    def copy_all_logs(self):
        """Copies all log content to clipboard."""
        log_content = self.log_text.get("1.0", tk.END).strip()
        if log_content:
            self.log_text.clipboard_clear()
            self.log_text.clipboard_append(log_content)
            self.log_text.update()
            app_logger.info("📋 Logs copied to clipboard.")

    def save_logs(self):
        """Saves logs to a file."""
        log_content = self.log_text.get("1.0", tk.END).strip()
        if not log_content:
            app_logger.warning("⚠️ Attempted to save an empty log file.")
            return

        file_path = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text Files", "*.txt"), ("All Files", "*.*")],
            title="Save Log As..."
        )

        if file_path:
            try:
                with open(file_path, "w", encoding="utf-8") as log_file:
                    log_file.write(log_content)
                app_logger.info(f"💾 Log saved successfully: {file_path}")
            except Exception as e:
                app_logger.error(f"❌ Failed to save log: {e}")
