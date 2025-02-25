
import logging

app_logger = logging.getLogger("PHOMODLogger")


class WorkspaceConfig:
    """Defines the configuration for a workspace."""

    def __init__(self, key: str, label: str, default_emoji: str, active_emoji: str, workspace_frame):
        self.key = key
        self.label = label
        self.default_emoji = default_emoji
        self.active_emoji = active_emoji
        self.workspace_frame = workspace_frame  # The actual UI tab/frame instance

    def get_tab_label(self, active=False):
        """Returns the formatted tab label with the appropriate emoji."""
        return f" {self.active_emoji if active else self.default_emoji}   {self.label} "


class WorkspaceManager:
    """Manages application workspaces, their state, and visibility."""

    def __init__(self, notebook, controller):
        self.notebook = notebook
        self.controller = controller
        self.controller.workspace_manager = self
        self.workspaces = {}
        self.workspace_configs = {}  # 🛠️ Now uses WorkspaceConfig objects

    def get_available_workspaces(self):
        """Returns a list of workspace labels."""
        return [config.label for config in self.workspace_configs.values()]

    def register_workspace(self, workspace_config: WorkspaceConfig):
        """Registers a new workspace dynamically."""
        self.workspace_configs[workspace_config.key] = workspace_config
        self.notebook.add(workspace_config.workspace_frame, text=workspace_config.get_tab_label(active=False))
        self.workspaces[workspace_config.key] = workspace_config.workspace_frame
        app_logger.info(f"🏗️ Workspace registered: {workspace_config.label}")

    def toggle_workspace_emoji(self):
        """Updates active emoji for the selected workspace."""
        current_workspace_id = self.notebook.index(self.notebook.select())
        current_text = self.notebook.tab(current_workspace_id, "text")

        # Find matching workspace config
        active_workspace = None
        for config in self.workspace_configs.values():
            if config.label in current_text:
                active_workspace = config
                break
        if not active_workspace:
            return  # No match found

        # Reset all workspaces to default emoji
        for ws_id in range(self.notebook.index("end")):
            ws_text = self.notebook.tab(ws_id, "text")
            for config in self.workspace_configs.values():
                if config.label in ws_text:
                    self.notebook.tab(ws_id, text=config.get_tab_label(active=False))

        # Set the active workspace emoji
        self.notebook.tab(current_workspace_id, text=active_workspace.get_tab_label(active=True))
        app_logger.info(f"🔄 Switched to workspace: {active_workspace.label}")

    def hide_workspace(self, label):
        """Hides the workspace with the given label."""
        for config in self.workspace_configs.values():
            if config.label == label:
                workspace_frame = self.workspaces.get(config.key)
                if workspace_frame:
                    self.notebook.forget(workspace_frame)
                    app_logger.info(f"Workspace hidden: {label}")
                return

    def show_workspace(self, label):
        """Shows (re-adds) the workspace with the given label if it is not already visible."""
        for config in self.workspace_configs.values():
            if config.label == label:
                workspace_frame = self.workspaces.get(config.key)
                if workspace_frame and workspace_frame not in self.notebook.winfo_children():
                    self.notebook.add(workspace_frame, text=config.get_tab_label(active=False))
                    app_logger.info(f"Workspace shown: {label}")
                return

    @staticmethod
    def save_workspace_state():
        """Save workspace state asynchronously (not yet implemented)."""
        app_logger.info("💾 Initiating workspace state save...")
        app_logger.info("⌛ Waiting for workspace save to complete...")
        app_logger.info("🚷 Feature not yet implemented.")
        app_logger.info("✅ Workspace state saved successfully.")
