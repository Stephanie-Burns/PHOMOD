import json
import logging
from pathlib import Path

app_logger = logging.getLogger("PHOMODLogger")

PROJECT_ROOT = Path(__file__).resolve().parent.parent
CONFIG_DIR = PROJECT_ROOT / "user"
USER_SETTINGS_FILE = CONFIG_DIR /"user_settings.json"

try:
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
except OSError as e:
    app_logger.warning(f"⚠️ Failed to create config directory: {e}")
    CONFIG_DIR = Path("/tmp")
    USER_SETTINGS_FILE = CONFIG_DIR / "user_settings.json"

class PHOMODConfig:
    """Handles loading, saving, and updating application settings."""
    DEFAULTS = {
        "theme": "arc",
        "sidebar_position": "left",
        "font_size": 12,
        "log_level": "INFO",
        "log_rotation": "Max file size",
        "max_log_size_mb": 5,
        "disable_file_logging": False,
        "recent_projects": [],
        "logs_dir": CONFIG_DIR / "logs",
    }

    def __init__(self):
        self.settings = self._load_settings()
        self.settings["logs_dir"].mkdir(parents=True, exist_ok=True)

    def _load_settings(self):
        if not USER_SETTINGS_FILE.exists():
            app_logger.info("🆕 No settings file found. Using defaults.")
            return self.DEFAULTS.copy()
        try:
            with USER_SETTINGS_FILE.open("r", encoding="utf-8") as f:
                settings = json.load(f)
            # Convert `logs_dir` back to a Path object
            settings["logs_dir"] = Path(settings.get("logs_dir", self.DEFAULTS["logs_dir"]))
            return {**self.DEFAULTS, **settings}
        except (json.JSONDecodeError, IOError) as e:
            app_logger.error(f"⚠️ Error loading settings: {e}")
            return self.DEFAULTS.copy()

    def save(self):
        """Saves the current settings to the user settings file."""
        try:
            settings_to_save = {
                key: str(value) if isinstance(value, Path) else value
                for key, value in self.settings.items()
            }
            with open(USER_SETTINGS_FILE, "w", encoding="utf-8") as f:
                json.dump(settings_to_save, f, indent=4)
            app_logger.info("💾 Settings saved successfully.")
        except IOError as e:
            app_logger.error(f"⚠️ Error saving settings: {e}")

    def _validate_path(self, path: Path, fallback: Path) -> Path:
        return path if path.is_absolute() and path.parent.exists() else fallback

    def get(self, key, default=None):
        return self.settings.get(key, default)

    def __getitem__(self, key):
        return self.settings.get(key)

    def __setitem__(self, key, value):
        if key in self.settings:
            self.settings[key] = value
            app_logger.info(f"⚙️ Setting updated: {key} = {value}")
            self.save()
        else:
            app_logger.warning(f"⚠️ Attempted to set unknown setting: {key}")

    def set(self, key, value):
        """Sets a configuration value (wrapper for `__setitem__`)."""
        self.__setitem__(key, value)

    def reset_to_defaults(self):
        self.settings = self.DEFAULTS.copy()
        self.save()
        app_logger.info("🔄 Settings reset to defaults.")

    def update_from_ui(self, ui_settings):
        self.settings.update(ui_settings)
        self.save()
        app_logger.info("🔄 Settings updated from UI.")

    def toggle_file_logging(self):
        self.settings["disable_file_logging"] = not self.settings["disable_file_logging"]
        self.save()
        app_logger.info(f"📢 File logging {'disabled' if self.settings['disable_file_logging'] else 'enabled'}.")

# Global instance of the settings manager.
SETTINGS = PHOMODConfig()
