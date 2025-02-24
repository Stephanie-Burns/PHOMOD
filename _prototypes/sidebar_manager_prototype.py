import tkinter as tk
from tkinter import ttk
import logging

app_log = logging.getLogger('FOMODLogger')


class SidebarManager:
    """Manages sidebars, ensuring only one is open at a time."""

    def __init__(self, parent):
        self.parent = parent

        # Main PanedWindow to hold content and sidebar
        self.paned = ttk.PanedWindow(parent, orient=tk.HORIZONTAL)
        self.paned.pack(fill="both", expand=True)

        self.content_frame = ttk.Frame(self.paned)
        self.paned.add(self.content_frame, weight=3)  # Default main content

        self.sidebars = {}  # {"tab_name": {"sidebar_key": (sidebar_class, position)}}
        self.active_sidebar = None
        self.active_tab = None
        self.sidebar_position = "left"
        self.sidebar_frame = None

    def register_sidebar(self, tab_name, key, sidebar_cls):
        """Registers a sidebar class for a given tab and key."""
        if tab_name not in self.sidebars:
            self.sidebars[tab_name] = {}
        self.sidebars[tab_name][key] = (sidebar_cls, "left")  # Store class, not instance
        app_log.debug(f"Registered sidebar '{key}' under tab '{tab_name}' with position 'left'.")

    def toggle_sidebar(self, tab_name, key):
        """Toggles sidebar visibility, ensuring only one is open at a time."""
        if self.active_tab != tab_name:
            self.hide_sidebar()
            self.active_tab = tab_name

        if self.active_sidebar == key:
            self.hide_sidebar()
            return

        self.hide_sidebar()

        if key in self.sidebars.get(tab_name, {}):
            sidebar_cls, position = self.sidebars[tab_name][key]

            # Only create a new instance if it doesn't already exist
            if not isinstance(self.sidebar_frame, sidebar_cls):
                sidebar = sidebar_cls(self.paned, tab_name, self, key)  # Instantiate fresh
                self.sidebars[tab_name][key] = (sidebar_cls, position)  # Keep class reference
                self._add_sidebar(sidebar, position)
                self.active_sidebar = key
                app_log.debug(f"Opened sidebar '{key}' on tab '{tab_name}'.")

    def hide_sidebar(self):
        """Hides the currently active sidebar."""
        if self.active_sidebar and self.active_tab:
            sidebar_cls, _ = self.sidebars[self.active_tab][self.active_sidebar]
            if isinstance(self.sidebar_frame, sidebar_cls):
                self.paned.forget(self.sidebar_frame)
                self.sidebar_frame.destroy()  # ✅ Proper cleanup
                app_log.debug(f"Closed sidebar '{self.active_sidebar}' on tab '{self.active_tab}'.")

        self.active_sidebar = None
        self.sidebar_frame = None

    def _add_sidebar(self, sidebar, position):
        """Adds the sidebar in the correct position if it's not already placed."""
        if self.sidebar_frame:
            if self.sidebar_frame == sidebar:
                return  # Prevent duplicate addition
            self.paned.forget(self.sidebar_frame)

        if position == "right":
            self.paned.add(sidebar, weight=1)
        else:
            self.paned.insert(0, sidebar, weight=1)

        self.sidebar_frame = sidebar
        app_log.debug(f"Sidebar placed on the {position}.")

    def _move_sidebar(self, tab_name, key, position):
        """Moves a sidebar left or right and re-adds it."""
        if key in self.sidebars.get(tab_name, {}):
            sidebar_cls, current_position = self.sidebars[tab_name][key]

            if current_position == position:
                return  # No need to move if already at the desired position

            self.sidebars[tab_name][key] = (sidebar_cls, position)  # Update position
            self.hide_sidebar()
            self.toggle_sidebar(tab_name, key)
            app_log.debug(f"Moved sidebar '{key}' on tab '{tab_name}' to the {position}.")


class TestSidebar(ttk.Frame):
    """A sidebar with buttons to change its position."""

    def __init__(self, parent, tab_name, sidebar_manager, key):
        super().__init__(parent, width=200, relief="sunken", padding=10)
        self.sidebar_manager = sidebar_manager
        self.tab_name = tab_name
        self.key = key

        ttk.Label(self, text=f"Sidebar: {key} in {tab_name}", font=("Arial", 12)).pack(pady=10)

        ttk.Button(self, text="Close", command=self.sidebar_manager.hide_sidebar).pack(pady=5)
        ttk.Button(self, text="Move Right", command=lambda: self.sidebar_manager._move_sidebar(tab_name, key, "right")).pack(pady=5)
        ttk.Button(self, text="Move Left", command=lambda: self.sidebar_manager._move_sidebar(tab_name, key, "left")).pack(pady=5)


class TestTab(ttk.Frame):
    """A sample tab with sidebars."""

    def __init__(self, parent, sidebar_manager, tab_name, multiple_sidebars=False):
        super().__init__(parent)
        self.sidebar_manager = sidebar_manager
        self.tab_name = tab_name

        ttk.Label(self, text=f"This is {tab_name}!", font=("Arial", 14)).pack(pady=10)

        ttk.Button(
            self,
            text=f"Toggle {tab_name} Sidebar",
            command=lambda: self.sidebar_manager.toggle_sidebar(self.tab_name, "sidebar"),
        ).pack(pady=5)

        self.sidebar_manager.register_sidebar(self.tab_name, "sidebar", TestSidebar)

        if multiple_sidebars:
            ttk.Button(
                self,
                text=f"Toggle {tab_name} Sidebar 2",
                command=lambda: self.sidebar_manager.toggle_sidebar(self.tab_name, "sidebar2"),
            ).pack(pady=5)

            self.sidebar_manager.register_sidebar(self.tab_name, "sidebar2", TestSidebar)


class SidebarTestApp:
    """Main application to test sidebar positioning."""

    def __init__(self, root):
        self.root = root
        self.root.title("Sidebar Persistence Test")
        self.root.geometry("800x600")

        self.sidebar_manager = SidebarManager(root)

        self.notebook = ttk.Notebook(self.sidebar_manager.content_frame)
        self.notebook.pack(fill="both", expand=True)

        self.tab1 = TestTab(self.notebook, self.sidebar_manager, "Tab 1")
        self.tab2 = TestTab(self.notebook, self.sidebar_manager, "Tab 2", multiple_sidebars=True)

        self.notebook.add(self.tab1, text="Tab 1")
        self.notebook.add(self.tab2, text="Tab 2")

        self.notebook.bind("<<NotebookTabChanged>>", lambda _: self.sidebar_manager.hide_sidebar())


if __name__ == "__main__":
    root = tk.Tk()
    app = SidebarTestApp(root)
    root.mainloop()
    # TODO Move sidebar inside of tab
