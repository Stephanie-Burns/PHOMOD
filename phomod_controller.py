import logging
from managers.theme_manager import ThemeManager
from managers.workspace_manager import WorkspaceManager
from managers.log_manager import LogManager
from managers.asset_manager import AssetManager
from config import SETTINGS

app_logger = logging.getLogger("PHOMODLogger")


class PhomodController:
    """Manages the core application state and shared resources, coordinating between the model and UI."""

    def __init__(self):
        self.log_manager = LogManager(max_buffer=100)  # Create a single shared LogManager
        self.asset_manager = AssetManager("/path/to/assets/icons")
        self.theme_manager = ThemeManager(SETTINGS)
        self.workspace_manager = WorkspaceManager(controller=self)
        self.ui = None

    def set_ui(self, ui_instance):
        """Registers the UI instance with the controller and initializes dependent components."""
        self.ui = ui_instance
        self.theme_manager.register_ui(ui_instance)


    def update_status_bar_text(self, message: str):
        if self.ui:
            self.ui.update_status_bar_text(message)
        else:
            app_logger.warning("No UI registered; cannot update status bar.")

    def shutdown(self):
        SETTINGS.save()
        app_logger.info("🔚 Controller shutting down.")
        if self.workspace_manager:
            self.workspace_manager.save_workspace_state()
        for handler in logging.getLogger().handlers:
            try:
                handler.close()
            except Exception:
                pass
