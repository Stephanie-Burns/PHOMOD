import logging
import random
import tkinter as tk
from tkinter import ttk
from config.settings import USER_SETTINGS, save_settings  # Import settings

app_logger = logging.getLogger("FOMODLogger")


class ThemeManager:
    """Handles application theming, including saving/restoring theme preferences."""

    def __init__(self, root):
        self.root = root
        self.style = ttk.Style(self.root)
        self.separator = "----------"
        self.themes_always_on_top = ["Default", "Random"]
        self.current_theme = USER_SETTINGS.get("theme", "arc")  # Load from settings

        self.apply_theme(self.current_theme)  # Apply saved theme on startup

    def get_themes(self):
        """Retrieve a list of available themes."""
        return self.root.get_themes()

    def get_theme(self):
        """Retrieve the name of the currently active theme."""
        return self.style.theme_use()

    def get_theme_options(self):
        """Retrieve organized theme options for display."""
        themes = self.get_themes()
        themes_alphabetical = [t for t in themes if t.lower() not in [s.lower() for s in self.themes_always_on_top]]
        themes_alphabetical = sorted([t.capitalize() for t in themes_alphabetical])
        return self.themes_always_on_top + [self.separator] + themes_alphabetical

    def apply_theme(self, theme):
        """Apply the selected theme and save the preference."""
        if theme == self.separator:
            app_logger.warning("⚠️ Invalid theme selection attempt.")
            return None

        if theme.lower() == "random":
            all_themes = self.get_themes()
            choices = [t for t in all_themes if t.lower() != "default"]
            theme = random.choice(choices) if choices else "default"

        try:
            self.root.set_theme(theme.lower())
            app_logger.info(f"✅ Applied theme: {theme}")
            self.root.update_idletasks()

            # Save theme to settings only if changed
            if theme != self.current_theme:
                self.current_theme = theme
                USER_SETTINGS["theme"] = theme
                save_settings(USER_SETTINGS)
                app_logger.info(f"💾 Theme saved: {theme}")

            return theme
        except tk.TclError as e:
            app_logger.error(f"⚠️ Error applying theme '{theme}': {e}")
            return None
