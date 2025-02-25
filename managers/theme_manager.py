import logging
import random
import tkinter as tk
from tkinter import ttk
from config.settings import USER_SETTINGS, save_settings

app_logger = logging.getLogger("PHOMODLogger")

class ThemeManager:
    """Handles application theming, including saving/restoring theme preferences and refreshing UI styles."""

    DEFAULT_BLACKLIST = {"equilux"}

    def __init__(self, root):
        self.root = root
        self.style = ttk.Style(self.root)
        self.current_theme = USER_SETTINGS.get("theme", "Arc").capitalize()
        # Merge user settings with our defaults
        self.blacklisted_themes = set(USER_SETTINGS.get("theme_blacklist", [])).union(self.DEFAULT_BLACKLIST)
        self.apply_theme(self.current_theme, force=True)

    def get_theme(self):
        """Returns the currently applied theme."""
        return self.current_theme

    def get_themes(self):
        """Retrieves a sorted list of available themes, excluding blacklisted ones."""
        try:
            all_themes = sorted(t.capitalize() for t in self.root.get_themes())
            return [t for t in all_themes if t.lower() not in self.blacklisted_themes]
        except AttributeError:
            app_logger.warning("⚠️ Theme retrieval not supported by root.")
            return ["Arc"]

    def get_smart_random_theme(self):
        """Retrieves a random theme different from the current one."""
        valid_themes = [t for t in self.get_themes() if t.lower() != self.current_theme.lower()]
        if not valid_themes:
            return None
        return random.choice(valid_themes)

    def apply_theme(self, theme, force=False):
        """
        Applies the selected theme if it isn’t blacklisted.
        Optionally forces reapplication even if it’s already active.
        """
        theme = theme.capitalize()
        if theme.lower() in self.blacklisted_themes:
            app_logger.warning(f"🚫 Attempted to apply blacklisted theme: {theme}")
            return None

        if theme == self.current_theme and not force:
            app_logger.debug(f"Theme '{theme}' is already active.")
            return theme

        try:
            # Use the ttkthemes API to set the theme
            self.root.set_theme(theme.lower())
            self.current_theme = theme
            USER_SETTINGS["theme"] = theme
            save_settings(USER_SETTINGS)
            app_logger.info(f"🎨 Theme changed: {theme}")
            self.refresh_ui_styles()
            return theme
        except tk.TclError as e:
            app_logger.error(f"⚠️ Error applying theme '{theme}': {e}")
            return None

    def refresh_ui_styles(self):
        """
        Recursively updates the style of all widgets in the application.
        This helps ensure that changes propagate through the entire widget tree.
        """
        self.root.update_idletasks()
        self.style.theme_use(self.current_theme.lower())
        self._refresh_widget_styles(self.root)
        app_logger.debug("🔄 UI styles refreshed after theme change.")

    def _refresh_widget_styles(self, widget):
        """Recursively refreshes the style of the given widget and its children."""
        try:
            current_style = widget.cget("style")
            widget.configure(style=current_style)
        except (tk.TclError, AttributeError):
            pass
        for child in widget.winfo_children():
            self._refresh_widget_styles(child)

    def modify_blacklist(self, theme, add=True):
        """Adds or removes a theme from the blacklist."""
        theme = theme.lower()
        if add:
            self.blacklisted_themes.add(theme)
            app_logger.info(f"🚫 Theme '{theme.capitalize()}' added to blacklist.")
        else:
            self.blacklisted_themes.discard(theme)
            app_logger.info(f"✅ Theme '{theme.capitalize()}' removed from blacklist.")
