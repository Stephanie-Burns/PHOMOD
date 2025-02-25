
import os
import json
import logging

app_logger = logging.getLogger("PHOMODLogger")

# Define project root dynamically
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Path to the user settings file
CONFIG_DIR = os.path.join(PROJECT_ROOT, "config")
USER_SETTINGS_FILE = os.path.join(CONFIG_DIR, "user_settings.json")

# Ensure the config directory exists
try:
    os.makedirs(CONFIG_DIR, exist_ok=True)
except OSError as e:
    app_logger.warning(f"⚠️ Failed to create config directory: {e}")
    CONFIG_DIR = "/tmp"  # Fallback to safe temporary storage
    USER_SETTINGS_FILE = os.path.join(CONFIG_DIR, "user_settings.json")


class ConfigManager:
    """Handles loading, saving, and modifying application settings."""

    DEFAULTS = {
        "theme": "arc",
        "sidebar_position": "left",
        "font_size": 12,
        "log_level": "INFO",
        "log_rotation": "Max file size",
        "max_log_size_mb": 5,
        "disable_file_logging": False,
        "recent_projects": [],
        "logs_dir": os.path.join(PROJECT_ROOT, "logs"),
    }

    def __init__(self):
        self.settings = self._load_settings()
        os.makedirs(self.settings["logs_dir"], exist_ok=True)

    def _load_settings(self):
        """Loads user settings from JSON, merging with defaults."""
        if not os.path.exists(USER_SETTINGS_FILE):
            app_logger.info("🆕 No settings file found. Using defaults.")
            return self.DEFAULTS.copy()

        try:
            with open(USER_SETTINGS_FILE, "r", encoding="utf-8") as f:
                settings = json.load(f)

            # Merge with defaults to ensure missing keys are filled
            settings = {**self.DEFAULTS, **settings}

            # Validate paths
            settings["logs_dir"] = self._validate_path(settings["logs_dir"], self.DEFAULTS["logs_dir"])

            return settings
        except (json.JSONDecodeError, IOError) as e:
            app_logger.error(f"⚠️ Error loading settings: {e}")
            return self.DEFAULTS.copy()  # Return defaults if something goes wrong

    def save(self):
        """Safely saves current settings to JSON."""
        try:
            with open(USER_SETTINGS_FILE, "w", encoding="utf-8") as f:
                json.dump(self.settings, f, indent=4)
            app_logger.info("💾 Settings saved successfully.")
        except IOError as e:
            app_logger.error(f"⚠️ Error saving settings: {e}")

    def _validate_path(self, path, fallback):
        """Ensures a valid directory path, otherwise falls back."""
        if path and os.path.isabs(path) and os.path.exists(os.path.dirname(path)):
            return path
        return fallback

    def get(self, key, default=None):
        """Safely gets a setting value."""
        return self.settings.get(key, default)

    def set(self, key, value, save=True):
        """Sets a setting and optionally saves immediately."""
        if key in self.settings:
            self.settings[key] = value
            app_logger.info(f"⚙️ Setting updated: {key} = {value}")
            if save:
                self.save()
        else:
            app_logger.warning(f"⚠️ Attempted to set unknown setting: {key}")

    def reset_to_defaults(self):
        """Resets all settings to defaults and saves."""
        self.settings = self.DEFAULTS.copy()
        self.save()
        app_logger.info("🔄 Settings reset to defaults.")

    def update_from_ui(self, ui_settings):
        """Updates settings from UI input (dict) and saves."""
        self.settings.update(ui_settings)
        self.save()
        app_logger.info("🔄 Settings updated from UI.")

    def toggle_file_logging(self):
        """Toggles file logging setting."""
        self.settings["disable_file_logging"] = not self.settings["disable_file_logging"]
        self.save()
        app_logger.info(f"📢 File logging {'disabled' if self.settings['disable_file_logging'] else 'enabled'}.")


# Create a global instance of the settings manager
SETTINGS = ConfigManager()




# # Get a setting
# theme = SETTINGS.get("theme")
#
# # Update a setting
# SETTINGS.set("theme", "keramik")
#
# # Toggle file logging
# SETTINGS.toggle_file_logging()
#
# # Reset everything
# SETTINGS.reset_to_defaults()
#
# # Bulk update from UI
# SETTINGS.update_from_ui({"theme": "dark", "font_size": 14})
