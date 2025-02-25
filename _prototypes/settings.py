import os
import json

# Define project root dynamically
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Path to the user settings file
CONFIG_DIR = os.path.join(PROJECT_ROOT, "config")
USER_SETTINGS_FILE = os.path.join(CONFIG_DIR, "user_settings.json")

# Ensure the config directory exists
try:
    os.makedirs(CONFIG_DIR, exist_ok=True)
except OSError as e:
    print(f"⚠️ Failed to create config directory: {e}")
    CONFIG_DIR = "/tmp"  # Fallback to safe temporary storage
    USER_SETTINGS_FILE = os.path.join(CONFIG_DIR, "user_settings.json")

# Default settings
DEFAULT_SETTINGS = {
    "theme": "arc",  # All TTK themes available
    "sidebar_position": "left",  # "left" or "right"
    "font_size": 12,
    "log_level": "INFO",
    "recent_projects": [],
    "logs_dir": os.path.join(PROJECT_ROOT, "logs"),
}


# Ensure paths are absolute and exist
def validate_path(path, fallback):
    """Ensures a valid directory path, otherwise falls back."""
    if path and os.path.isabs(path) and os.path.exists(os.path.dirname(path)):
        return path
    return fallback


def load_settings():
    """Loads user settings from JSON file, ensuring valid paths."""
    if not os.path.exists(USER_SETTINGS_FILE):
        return DEFAULT_SETTINGS  # No settings file, return defaults

    try:
        with open(USER_SETTINGS_FILE, "r", encoding="utf-8") as f:
            settings = json.load(f)

        # Validate paths to prevent bad configurations
        settings["logs_dir"] = validate_path(settings.get("logs_dir"), DEFAULT_SETTINGS["logs_dir"])

        return {**DEFAULT_SETTINGS, **settings}  # Merge with defaults
    except (json.JSONDecodeError, IOError):
        print("⚠️ Corrupt settings file, using defaults.")
        return DEFAULT_SETTINGS  # If file is corrupt, return defaults


def save_settings(updated_settings):
    """Safely saves user settings to JSON file."""
    try:
        with open(USER_SETTINGS_FILE, "w", encoding="utf-8") as f:
            json.dump(updated_settings, f, indent=4)
    except IOError as e:
        print(f"⚠️ Error saving settings: {e}")


# Load settings at module import
USER_SETTINGS = load_settings()

# Ensure logs directory exists
os.makedirs(USER_SETTINGS["logs_dir"], exist_ok=True)
