import sys
import logging
import tkinter as tk
from ttkthemes import ThemedTk
from tkinter import ttk, font
from views.project_workspace_view import ProjectWorkspaceView
from views.xml_editor_view import XMLEditorView
from views.blotter_feed_view import BlotterFeedView
from views.settings_panel_view import SettingsPanelView
from views.documentation_editor_view import DocumentationEditorView
from components.status_bar import StatusBar

app_logger = logging.getLogger("PHOMODLogger")

class PhomodUI(ThemedTk):
    """
    Main UI class for PHOMOD. Handles window setup, status bar, and workspace (tab) management.
    """

    def __init__(self, controller):
        super().__init__(theme="arc")
        self.controller = controller
        self.controller.set_ui(self)  # Register UI with controller
        self.setup_ui()
        app_logger.info("🚀 UI initialized.")
        self.protocol("WM_DELETE_WINDOW", self.shutdown)

    def setup_ui(self):
        """Initializes window configuration, styles, fonts, status bar, and workspaces."""
        self.configure_window()
        self.create_style()
        self.create_fonts()
        self.create_status_bar()
        self.create_notebook()
        self._initialize_workspaces()

    def configure_window(self):
        self.title("PHOMOD - Mod Organizer")
        self.geometry("1000x618")
        self.minsize(width=1000, height=550)

    def create_style(self):
        self.style = ttk.Style(self)

    def create_fonts(self):
        self.fonts = {
            "italic": font.Font(family="Helvetica", size=10, slant="italic"),
            "bold": font.Font(family="Helvetica", size=10, weight="bold"),
            "default": font.Font(family="Helvetica", size=10),
            "title": font.Font(family="Helvetica", size=12, weight="bold"),
            "log": font.Font(family="Courier", size=11),
            "log_critical": font.Font(family="Courier", size=11, weight="bold"),
        }

    def create_notebook(self):
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill=tk.BOTH, expand=True, pady=(5, 0))

    def create_status_bar(self):
        self.status_var = tk.StringVar(value="Ready")
        self.status_bar = StatusBar(self, initial_text="Ready", delay=300, border=2)
        self.status_bar.pack(side="bottom", fill="x", padx=5, pady=(5, 5))
        self.help_manager = self.status_bar.help_manager

    def update_status_bar_text(self, message: str):
        self.status_bar.update_text(message)

    def _initialize_workspaces(self):
        """Registers workspaces with the workspace manager and adds them to the notebook."""
        workspace_definitions = [
            ("project", "Project", "📦", "🚚", ProjectWorkspaceView),
            ("xml", "XML Preview", "🍳", "🍽️", XMLEditorView),
            ("logs", "Logs", "🌲", "🪵", BlotterFeedView),
            ("settings", "Settings", "⚙️", "🔧", SettingsPanelView),
            ("docs", "Help", "📔", "📖", DocumentationEditorView),
        ]

        for key, label, default_emoji, active_emoji, workspace_class in workspace_definitions:
            config = self.controller.workspace_manager.register_workspace(
                key, label, default_emoji, active_emoji, workspace_class, parent=self.notebook
            )
            self.notebook.add(config.workspace_frame, text=config.get_tab_label(active=False))

        self.notebook.bind("<<NotebookTabChanged>>", self._toggle_workspace_emoji)

    def _toggle_workspace_emoji(self, event=None):
        """Updates the tab label emojis to reflect the active workspace."""
        current_workspace_id = self.notebook.index(self.notebook.select())
        current_text = self.notebook.tab(current_workspace_id, "text")
        active_workspace = self.controller.workspace_manager.get_workspace_by_label(current_text)
        if not active_workspace:
            return

        # Reset all workspace tab labels
        for ws_id in range(self.notebook.index("end")):
            ws_text = self.notebook.tab(ws_id, "text")
            config = self.controller.workspace_manager.get_workspace_by_label(ws_text)
            if config:
                self.notebook.tab(ws_id, text=config.get_tab_label(active=False))
        # Set the active emoji
        self.notebook.tab(current_workspace_id, text=active_workspace.get_tab_label(active=True))
        app_logger.info(f"🔄 Switched to workspace: {active_workspace.label}")

    def shutdown(self):
        """Performs graceful shutdown."""
        self.controller.shutdown()
        self.destroy()
        app_logger.info("✨ Application shutdown complete. Goodbye!")
        sys.exit(0)
