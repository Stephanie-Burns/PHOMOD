import logging
import random
from ttkthemes import ThemedTk
from tkinter import ttk, TclError

app_logger = logging.getLogger("PHOMODLogger")


class ThemeManager:
    """Handles application theming, including saving/restoring theme preferences and refreshing UI styles."""

    DEFAULT_BLACKLIST = {"equilux"}

    def __init__(self, settings):
        self.settings = settings
        self.style = None
        self.root = None
        self.current_theme = (settings.get("theme", "Arc")).capitalize()
        self.blacklisted_themes = set(settings.get("theme_blacklist", [])) | self.DEFAULT_BLACKLIST

    def register_ui(self, root: ThemedTk):
        """Registers the UI root for theme management and ensures `ttkthemes` is used."""
        if not isinstance(root, ThemedTk):
            app_logger.warning("⚠️ UI is not using ThemedTk. Some themes may be missing.")
        self.root = root
        self.style = ttk.Style(root)
        self.apply_theme(self.current_theme)

    def get_theme(self) -> str:
        return self.current_theme

    def get_themes(self) -> list:
        """Retrieves all available themes, including `ttkthemes` if ThemedTk is used."""
        if not self.root:
            app_logger.warning("⚠️ ThemeManager has no registered UI.")
            return ["Arc"]

        try:
            all_themes = self.root.get_themes() if isinstance(self.root, ThemedTk) else self.style.theme_names()
            all_themes = sorted(t.capitalize() for t in all_themes)
            return [t for t in all_themes if t.lower() not in self.blacklisted_themes]
        except AttributeError:
            app_logger.warning("⚠️ Theme retrieval not supported.")
            return ["Arc"]

    def get_smart_random_theme(self) -> str | None:
        valid_themes = [t for t in self.get_themes() if t.lower() != self.current_theme.lower()]
        return random.choice(valid_themes) if valid_themes else None

    def apply_theme(self, theme: str, force: bool = False) -> str | None:
        theme = theme.lower()  # work in lower-case consistently
        if theme in self.blacklisted_themes:
            app_logger.warning(f"🚫 Attempted to apply blacklisted theme: {theme.capitalize()}")
            return None
        if theme == self.current_theme and not force:
            app_logger.debug(f"Theme '{theme.capitalize()}' is already active.")
            return theme
        try:
            if not self.root:
                raise RuntimeError("ThemeManager has no registered UI. Call register_ui() first.")
            self.root.set_theme(theme)
            self.current_theme = theme
            self.settings["theme"] = theme.capitalize()  # if you want to show capitalized names in settings
            self.settings.save()
            app_logger.info(f"🎨 Theme changed: {theme.capitalize()}")
            self.refresh_ui_styles()
            # Optionally: notify other windows to refresh their styles
            return theme
        except TclError as e:
            app_logger.error(f"⚠️ Error applying theme '{theme.capitalize()}': {e}")
            return None

    def refresh_ui_styles(self) -> None:
        if not self.style:
            app_logger.warning("⚠️ Cannot refresh styles - no registered UI.")
            return
        self.style.theme_use(self.current_theme.lower())
        app_logger.debug("🔄 UI styles refreshed.")

    def modify_blacklist(self, theme: str, add: bool = True) -> None:
        theme = theme.lower()
        if add:
            self.blacklisted_themes.add(theme)
            app_logger.info(f"🚫 Theme '{theme.capitalize()}' added to blacklist.")
        else:
            self.blacklisted_themes.discard(theme)
            app_logger.info(f"✅ Theme '{theme.capitalize()}' removed from blacklist.")
