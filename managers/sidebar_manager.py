# managers/sidebar_manager.py
import logging
import tkinter as tk
from config import SETTINGS

app_logger = logging.getLogger("PHOMODLogger")

class SidebarManager:
    """
    Manages sidebars for each tab with persistent positions and widths.
    Sidebars can be registered, toggled, repositioned, and resized with their settings saved.
    """
    def __init__(self, notebook):
        self.notebook = notebook  # Reference to the main Notebook widget
        self.sidebars = {}  # {tab_name: {sidebar_key: (sidebar_cls, position)}}
        self.active_sidebar_key = None
        self.active_tab_name = None
        self.active_sidebar_widget = None  # Currently displayed sidebar widget instance
        self.sidebar_container = None  # The container (typically a PanedWindow) where the sidebar is attached

        # Load persisted positions and widths
        self.sidebar_positions = SETTINGS.get("sidebar_positions", {})
        self.sidebar_widths = SETTINGS.get("sidebar_widths", {})
        self.cleanup_missing_sidebars()

    def register_sidebar(self, tab_name, sidebar_key, sidebar_cls):
        """
        Registers a sidebar class for a specific tab under a unique key.
        Loads the last known position from settings (default is "left").
        """
        if tab_name not in self.sidebars:
            self.sidebars[tab_name] = {}
        position = self.sidebar_positions.get(tab_name, {}).get(sidebar_key, "left")
        self.sidebars[tab_name][sidebar_key] = (sidebar_cls, position)
        app_logger.debug(f"Registered sidebar '{sidebar_key}' for tab '{tab_name}' with position '{position}'.")

    def toggle_sidebar(self, tab_name, sidebar_key):
        """
        Toggles the visibility of a sidebar within a given tab.
        If the sidebar is already active, it is hidden; otherwise, it is shown.
        """
        # If switching tabs, hide any active sidebar first.
        if self.active_tab_name != tab_name:
            self.hide_sidebar()
            self.active_tab_name = tab_name

        # If the same sidebar is active, toggle it off.
        if self.active_sidebar_key == sidebar_key:
            self.hide_sidebar()
            return

        self.hide_sidebar()  # Hide any active sidebar before showing the new one.

        # Check that the sidebar is registered for the tab.
        if sidebar_key not in self.sidebars.get(tab_name, {}):
            app_logger.warning(f"Sidebar '{sidebar_key}' not registered for tab '{tab_name}'.")
            return

        sidebar_cls, position = self.sidebars[tab_name][sidebar_key]
        tab_container = self.get_tab_container(tab_name)
        if not tab_container:
            app_logger.warning(f"No container found for tab '{tab_name}'; cannot show sidebar.")
            return

        # Instantiate and add the sidebar widget.
        sidebar_widget = sidebar_cls(tab_container, tab_name, self, sidebar_key)
        self._add_sidebar(sidebar_widget, tab_name, position)
        self.active_sidebar_key = sidebar_key
        self.active_sidebar_widget = sidebar_widget
        app_logger.debug(f"Sidebar '{sidebar_key}' toggled on for tab '{tab_name}'.")

    def get_tab_container(self, tab_name):
        """
        Retrieves the container widget (e.g., a PanedWindow) for the specified tab.
        It first checks if the tab has an attribute 'sidebar_container'; otherwise, it searches
        for a PanedWindow child.
        """
        for tab in self.notebook.winfo_children():
            if getattr(tab, "tab_name", None) == tab_name:
                container = getattr(tab, "sidebar_container", None)
                if container:
                    return container
                # Fallback: return the first PanedWindow child.
                for child in tab.winfo_children():
                    if isinstance(child, tk.PanedWindow):
                        return child
        app_logger.warning(f"Tab container for '{tab_name}' not found.")
        return None

    def hide_sidebar(self):
        """Hides and destroys the currently active sidebar widget."""
        if self.active_sidebar_widget and self.active_tab_name:
            container = self.sidebar_container or self.get_tab_container(self.active_tab_name)
            if container and self.active_sidebar_widget in container.panes():
                container.forget(self.active_sidebar_widget)
            try:
                self.active_sidebar_widget.destroy()
            except Exception as e:
                app_logger.error(f"Error destroying sidebar: {e}")
            app_logger.debug(f"Sidebar '{self.active_sidebar_key}' hidden for tab '{self.active_tab_name}'.")
        self.active_sidebar_key = None
        self.active_sidebar_widget = None
        self.sidebar_container = None

    def _add_sidebar(self, sidebar_widget, tab_name, position):
        """
        Adds the sidebar widget to the container in the specified position.
        """
        tab_container = self.get_tab_container(tab_name)
        if not tab_container:
            app_logger.warning(f"Cannot add sidebar; container for tab '{tab_name}' not found.")
            return
        # Remove any existing sidebar.
        if self.active_sidebar_widget and self.active_sidebar_widget != sidebar_widget:
            tab_container.forget(self.active_sidebar_widget)
        # Place the sidebar widget based on the desired position.
        if position.lower() == "right":
            tab_container.add(sidebar_widget, weight=1)
        else:
            # Default to left; insert at index 0.
            tab_container.insert(0, sidebar_widget, weight=1)
        self.sidebar_container = tab_container
        app_logger.debug(f"Sidebar added to '{position}' side of tab '{tab_name}'.")

    def move_sidebar(self, tab_name, sidebar_key, new_position):
        """
        Moves a sidebar to a new position ('left' or 'right') within its tab.
        Persists the change to settings.
        """
        if sidebar_key not in self.sidebars.get(tab_name, {}):
            app_logger.warning(f"Sidebar '{sidebar_key}' not registered for tab '{tab_name}'.")
            return
        sidebar_cls, current_position = self.sidebars[tab_name][sidebar_key]
        if current_position == new_position:
            return  # No change required.
        # Update the in-memory record.
        self.sidebars[tab_name][sidebar_key] = (sidebar_cls, new_position)
        # Update and save settings.
        positions = SETTINGS.get("sidebar_positions", {})
        positions.setdefault(tab_name, {})[sidebar_key] = new_position
        SETTINGS["sidebar_positions"] = positions
        SETTINGS.save()
        self.hide_sidebar()
        self.toggle_sidebar(tab_name, sidebar_key)
        app_logger.debug(f"Sidebar '{sidebar_key}' moved to '{new_position}' in tab '{tab_name}'.")

    def on_sidebar_resize(self, event):
        """
        Callback to persist the sidebar width when resized.
        """
        if self.active_sidebar_key and self.active_tab_name and self.active_sidebar_widget:
            try:
                width = self.active_sidebar_widget.winfo_width()
                widths = SETTINGS.get("sidebar_widths", {})
                widths.setdefault(self.active_tab_name, {})[self.active_sidebar_key] = width
                SETTINGS["sidebar_widths"] = widths
                SETTINGS.save()
                app_logger.debug(f"Sidebar '{self.active_sidebar_key}' width saved as {width}.")
            except Exception as e:
                app_logger.warning(f"Failed to save sidebar width: {e}")

    def cleanup_missing_sidebars(self):
        """
        Removes any stored settings for sidebars that are no longer registered.
        """
        updated_positions = {}
        updated_widths = {}
        stored_positions = SETTINGS.get("sidebar_positions", {})
        for tab, sidebars in stored_positions.items():
            if tab in self.sidebars:
                for key, pos in sidebars.items():
                    if key in self.sidebars[tab]:
                        updated_positions.setdefault(tab, {})[key] = pos
                    else:
                        app_logger.warning(f"Removing stale sidebar setting '{key}' in tab '{tab}'.")
        stored_widths = SETTINGS.get("sidebar_widths", {})
        for tab, sidebars in stored_widths.items():
            if tab in updated_positions:
                for key, width in sidebars.items():
                    if key in updated_positions[tab]:
                        updated_widths.setdefault(tab, {})[key] = width
        SETTINGS["sidebar_positions"] = updated_positions
        SETTINGS["sidebar_widths"] = updated_widths
        SETTINGS.save()
