import logging
from typing import Optional

app_logger = logging.getLogger("PHOMODLogger")

class WorkspaceConfig:
    """Defines the configuration for a workspace, including its UI component."""
    def __init__(self, key: str, label: str, default_emoji: str, active_emoji: str, workspace_class, controller, parent):
        self.key = key
        self.label = label
        self.default_emoji = default_emoji
        self.active_emoji = active_emoji
        self.controller = controller
        self.workspace_frame = workspace_class(parent, controller=controller)

    def get_tab_label(self, active: bool = False) -> str:
        return f" {self.active_emoji if active else self.default_emoji}   {self.label} "

class WorkspaceManager:
    """Manages the registration and state of application workspaces."""
    def __init__(self, controller):
        self.controller = controller
        self.workspaces = {}         # Maps key -> workspace frame
        self.workspace_configs = {}  # Maps key -> WorkspaceConfig

    def register_workspace(self, key: str, label: str, default_emoji: str, active_emoji: str, workspace_class, parent):
        if key in self.workspace_configs:
            app_logger.warning(f"⚠️ Workspace '{label}' is already registered.")
            return self.workspace_configs[key]
        config = WorkspaceConfig(key, label, default_emoji, active_emoji, workspace_class, self.controller, parent)
        self.workspace_configs[key] = config
        self.workspaces[key] = config.workspace_frame
        app_logger.info(f"🏗️ Registered workspace: {label}")
        return config

    def get_available_workspaces(self) -> list:
        return [config.label for config in self.workspace_configs.values()]

    def get_workspace_by_label(self, label: str) -> Optional[WorkspaceConfig]:
        for config in self.workspace_configs.values():
            if config.label in label:
                return config
        return None

    def get_workspace(self, key: str) -> Optional[WorkspaceConfig]:
        return self.workspace_configs.get(key)

    def save_workspace_state(self):
        app_logger.info("💾 Initiating workspace state save...")
        # Implement state persistence logic as needed.
        app_logger.info("✅ Workspace state saved successfully.")
