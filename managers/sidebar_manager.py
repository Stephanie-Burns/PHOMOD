
import logging
from config import SETTINGS

app_log = logging.getLogger("PHOMODLogger")


class SidebarManager:
    """Manages sidebars per tab with persistent positions."""

    def __init__(self, notebook):
        self.notebook = notebook  # Store notebook reference
        self.sidebars = {}  # {"tab_name": {"sidebar_key": (sidebar_class, position)}}
        self.active_sidebar = None
        self.active_tab = None
        self.sidebar_frame = None
        self.sidebar_container = None  # The container (PanedWindow) where the sidebar is attached

        # Load sidebar positions from settings
        self.sidebar_positions = SETTINGS.get("sidebar_positions", {})
        self.cleanup_missing_sidebars()

    def register_sidebar(self, tab_name, key, sidebar_cls):
        """Registers a sidebar class for a given tab and key, keeping previous position."""
        if tab_name not in self.sidebars:
            self.sidebars[tab_name] = {}

        # Load last known position, default to "left"
        position = self.sidebar_positions.get(tab_name, {}).get(key, "left")
        self.sidebars[tab_name][key] = (sidebar_cls, position)
        app_log.debug(f"Registered sidebar '{key}' under tab '{tab_name}' with position '{position}'.")

    def toggle_sidebar(self, tab_name, key):
        """Toggles sidebar visibility inside the active tab."""
        if self.active_tab != tab_name:
            self.hide_sidebar()
            self.active_tab = tab_name

        # Toggle off if the same sidebar is active
        if self.active_sidebar == key:
            self.hide_sidebar()
            return

        self.hide_sidebar()

        if key in self.sidebars.get(tab_name, {}):
            sidebar_cls, position = self.sidebars[tab_name][key]

            # Get the active tab's PanedWindow container
            tab_container = self.get_tab_container(tab_name)
            if not tab_container:
                app_log.warning(f"⚠️ No container found for tab '{tab_name}', sidebar won't open.")
                return

            # Create a new sidebar instance and add it to the tab container
            sidebar = sidebar_cls(tab_container, tab_name, self, key)
            self._add_sidebar(sidebar, tab_name, position)
            self.active_sidebar = key
            app_log.debug(f"✅ Opened sidebar '{key}' inside tab '{tab_name}'.")

    def get_tab_container(self, tab_name):
        """Finds and returns the PanedWindow inside the correct tab."""
        for tab in self.notebook.winfo_children():
            # Expecting each tab to be an instance of TestTab with attribute 'tab_name'
            if hasattr(tab, "tab_name") and tab.tab_name == tab_name:
                return tab.paned  # Return the tab's PanedWindow
        app_log.warning(f"⚠️ Tab '{tab_name}' not found.")
        return None

    def hide_sidebar(self):
        """Hides the currently active sidebar."""
        if self.active_sidebar and self.active_tab and self.sidebar_frame:
            container = self.sidebar_container or self.get_tab_container(self.active_tab)
            if container:
                container.forget(self.sidebar_frame)
            self.sidebar_frame.destroy()
            app_log.debug(f"❌ Closed sidebar '{self.active_sidebar}' on tab '{self.active_tab}'.")

        self.active_sidebar = None
        self.sidebar_frame = None
        self.sidebar_container = None

    def _add_sidebar(self, sidebar, tab_name, position):
        """Adds the sidebar to the tab’s PanedWindow."""
        tab_container = self.get_tab_container(tab_name)
        if not tab_container:
            app_log.warning(f"⚠️ Sidebar '{self.active_sidebar}' could not be placed in '{tab_name}' (Tab missing).")
            return

        # Remove any existing sidebar in this container
        if self.sidebar_frame and self.sidebar_frame != sidebar:
            tab_container.forget(self.sidebar_frame)

        # Place the sidebar on the correct side
        if position == "right":
            tab_container.add(sidebar, weight=1)
        else:
            tab_container.insert(0, sidebar, weight=1)

        self.sidebar_frame = sidebar
        self.sidebar_container = tab_container
        app_log.debug(f"📌 Sidebar placed on the {position} inside tab '{tab_name}'.")

    def _move_sidebar(self, tab_name, key, position):
        """Moves a sidebar left or right, persists setting, and re-adds it."""
        if key in self.sidebars.get(tab_name, {}):
            sidebar_cls, current_position = self.sidebars[tab_name][key]
            if current_position == position:
                return  # No change needed

            # Update position in memory and settings
            self.sidebars[tab_name][key] = (sidebar_cls, position)
            self.sidebar_positions.setdefault(tab_name, {})[key] = position
            SETTINGS.save_settings({"sidebar_positions": self.sidebar_positions})
            self.hide_sidebar()
            self.toggle_sidebar(tab_name, key)
            app_log.debug(f"🔄 Moved sidebar '{key}' on tab '{tab_name}' to the {position}.")

    def _on_sidebar_resize(self, event):
        """Saves the sidebar width when resized."""
        if self.active_sidebar and self.active_tab and self.sidebar_frame:
            try:
                # Use winfo_width to get the current width of the sidebar
                width = self.sidebar_frame.winfo_width()
                sidebar_widths = SETTINGS.get("sidebar_widths", {})
                sidebar_widths.setdefault(self.active_tab, {})[self.active_sidebar] = width
                SETTINGS.save_settings({"sidebar_widths": sidebar_widths})
                app_log.debug(f"💾 Saved sidebar '{self.active_sidebar}' width: {width}.")
            except Exception as e:
                app_log.warning(f"⚠️ Failed to save sidebar width: {e}")

    def cleanup_missing_sidebars(self):
        """Removes settings for sidebars that no longer exist."""
        updated_positions = {}
        updated_widths = {}

        for tab, sidebars in SETTINGS.get("sidebar_positions", {}).items():
            for key in list(sidebars):
                if key not in self.sidebars.get(tab, {}):
                    app_log.warning(f"⚠️ Removing stale sidebar setting: {key} on {tab}")
                else:
                    updated_positions.setdefault(tab, {})[key] = sidebars[key]

        for tab, sidebars in SETTINGS.get("sidebar_widths", {}).items():
            for key in list(sidebars):
                if key in updated_positions.get(tab, {}):
                    updated_widths.setdefault(tab, {})[key] = sidebars[key]

        SETTINGS.save_settings({
            "sidebar_positions": updated_positions,
            "sidebar_widths": updated_widths
        })
