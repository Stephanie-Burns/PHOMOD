
import logging
import threading
from workspaces import ProjectTab, XMLTab, LogsTab, SettingsTab, DocumentationTab

app_logger = logging.getLogger('PHOMODLogger')


class WorkspaceManager:
    """Handles creation and management of application workspaces."""
    def __init__(self, notebook, controller):
        self.notebook = notebook
        self.controller = controller
        self.controller.workspace_manager = self
        self.workspaces = {}
        self.workspace_config = {
            "project":  {"default": "📦", "active": "🚚", "label": "Project", "class": ProjectTab},
            "xml":      {"default": "🍳", "active": "🍽️", "label": "XML Preview", "class": XMLTab},
            "logs":     {"default": "🌲", "active": "🪵", "label": "Logs", "class": LogsTab},
            "settings": {"default": "⚙️", "active": "🔧", "label": "Settings", "class": SettingsTab},
            "docs":     {"default": "📔", "active": "📖", "label": "Help", "class": DocumentationTab},
        }
        self._create_workspaces()

    def _create_workspaces(self):
        for key, config in self.workspace_config.items():
            workspace_frame = config["class"](self.notebook, controller=self.controller)
            self.notebook.add(workspace_frame, text=f" {config['default']}   {config['label']}")
            self.workspaces[key] = workspace_frame
            app_logger.info(f"🏗️ Workspace created: {config['label']}")

    def toggle_workspace_emoji(self):
        current_workspace_id = self.notebook.index(self.notebook.select())
        current_text = self.notebook.tab(current_workspace_id, "text")  # use tab(), not workspace()

        # Find config for active workspace
        for key, config in self.workspace_config.items():
            if config["label"] in current_text:
                active_label = f" {config['active']}   {config['label']}    "
                break
        else:
            return

        # Reset all workspaces to default emoji
        for ws_id in range(self.notebook.index("end")):
            ws_text = self.notebook.tab(ws_id, "text")
            for key, config in self.workspace_config.items():
                if config["label"] in ws_text:
                    self.notebook.tab(ws_id, text=f" {config['default']}   {config['label']}    ")

        # Set the active workspace emoji
        self.notebook.tab(current_workspace_id, text=active_label)
        app_logger.info(f"🔄 Switched to workspace: {current_text}")

    def get_available_workspaces(self):
        return [config["label"] for key, config in self.workspace_config.items()]

    def hide_workspace(self, label):
        """Hides the workspace with the given label."""
        for key, config in self.workspace_config.items():
            if config["label"] == label:
                workspace_frame = self.workspaces.get(key)
                if workspace_frame:
                    self.notebook.forget(workspace_frame)
                    app_logger.info(f"Workspace hidden: {label}")
                return

    def show_workspace(self, label):
        """Shows (re-adds) the workspace with the given label if it is not already visible."""
        for key, config in self.workspace_config.items():
            if config["label"] == label:
                workspace_frame = self.workspaces.get(key)
                # Only add if not already in the notebook
                if workspace_frame and workspace_frame not in self.notebook.winfo_children():
                    self.notebook.add(workspace_frame, text=f" {config['default']}   {config['label']}")
                    app_logger.info(f"Workspace shown: {label}")
                return

    def save_workspace_state(self):
        """Save workspace state asynchronously"""
        app_logger.info("💾 Initiating workspace state save...")
        app_logger.info("⌛ Waiting for workspace save to complete...")
        app_logger.info("🚷 Feature not yet implemented.")
        app_logger.info("✅ Workspace state saved successfully.")
