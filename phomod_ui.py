
import sys
import logging
import tkinter as tk
from ttkthemes import ThemedTk
from tkinter import ttk, font
from appdata import phomod_map

from managers import ThemeManager, WorkspaceManager, LogManager
from status_bar import StatusBar

app_logger = logging.getLogger('PHOMODLogger')


class PhomodUI(ThemedTk):
    def __init__(self):
        super().__init__(theme="arc")
        self.setup_ui()
        app_logger.info(f"🚀 ==== application [{phomod_map()}] started ==== 🚀")

        self.protocol("WM_DELETE_WINDOW", self.shutdown)

    def setup_ui(self):
        self.configure_window()
        self.create_style()
        self.create_fonts()
        self.create_status_bar()
        self.create_notebook()
        self.create_workspaces()
        self.notebook.bind("<<NotebookTabChanged>>", self.on_workspace_change)

    def configure_window(self):
        self.title("PHOMOD - Mod Organizer")
        self.geometry("1000x618")
        self.minsize(width=1000, height=550)

    def create_style(self):
        self.style = ttk.Style(self)
        self.theme_manager = ThemeManager(self)

    def create_fonts(self):
        self.fonts = {
            "italic": font.Font(family="Helvetica", size=10, slant="italic"),
            "bold": font.Font(family="Helvetica", size=10, weight="bold"),
            "default": font.Font(family="Helvetica", size=10),
            "title": font.Font(family="Helvetica", size=12, weight="bold"),
        }

    def create_notebook(self):
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill=tk.BOTH, expand=True, pady=(5, 0))

    def create_status_bar(self):
        """Creates a status bar at the bottom of the window."""
        self.status_var = tk.StringVar(value="Ready")
        self.status_bar = StatusBar(self, initial_text="Ready", delay=300, border=2)
        self.status_bar.pack(side="bottom", fill="x", padx=5, pady=(5, 5))
        self.help_manager = self.status_bar.help_manager

    def update_status_bar_text(self, message):
        """Updates the status bar immediately (if needed) via the StatusBar class."""
        self.status_bar.update_text(message)

    def create_workspaces(self):
        self.workspace_manager = WorkspaceManager(self.notebook, controller=self)

    def on_workspace_change(self, event):
        self.workspace_manager.toggle_workspace_emoji()

    def shutdown(self):
        """Handles graceful application shutdown."""

        app_logger.info("🔚 Initializing shutdown")
        # Save workspace state before quitting
        if hasattr(self, 'workspace_manager'):
            self.workspace_manager.save_workspace_state()

        # Flush logs before closing
        for handler in logging.getLogger().handlers:
            handler.close()


        app_logger.info(f"🛑 ==== application [{phomod_map()}] shutdown complete ==== 🛑")
        self.destroy()
        sys.exit(0)

if __name__ == "__main__":
    from config.logger_config import app_logger
    app_logger.info("Application started")
    app = PhomodUI()
    app.mainloop()
