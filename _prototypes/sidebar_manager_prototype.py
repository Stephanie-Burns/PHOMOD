import tkinter as tk
from tkinter import ttk
import logging

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger("SidebarManager")


class SidebarManager:
    """Manages sidebars, ensuring only one is open at a time."""

    def __init__(self, parent):
        self.parent = parent

        # Main PanedWindow to hold content and sidebars
        self.paned = ttk.PanedWindow(parent, orient=tk.HORIZONTAL)
        self.paned.pack(fill="both", expand=True)

        # Notebook (Main UI area)
        self.notebook = ttk.Notebook(self.paned)
        self.paned.add(self.notebook, weight=3)  # Main content area

        # Sidebar storage
        self.sidebars = {}
        self.active_sidebar = None
        self.active_tab = None
        self.sidebar_position = "left"
        self.sidebar_frame = None  # Holds the currently displayed sidebar

        # Tabs
        self.tab1 = TestTab(self.notebook, self, "Tab 1")
        self.tab2 = TestTab(self.notebook, self, "Tab 2", multiple_sidebars=True)

        self.notebook.add(self.tab1, text="Tab 1")
        self.notebook.add(self.tab2, text="Tab 2")

        self.notebook.bind("<<NotebookTabChanged>>", self.close_sidebar)

    def register_sidebar(self, tab_name, key, sidebar):
        """Registers a sidebar for a given tab and key."""
        if tab_name not in self.sidebars:
            self.sidebars[tab_name] = {}
        self.sidebars[tab_name][key] = (sidebar, "left")  # Default to left
        sidebar.pack_forget()
        logger.debug(f"Registered sidebar '{key}' under tab '{tab_name}'")

    def toggle_sidebar(self, tab_name, key):
        """Toggles sidebar visibility."""
        if self.active_tab != tab_name:
            self.hide_sidebar()
            self.active_tab = tab_name

        if self.active_sidebar == key:
            self.hide_sidebar()
            return

        self.hide_sidebar()

        if key in self.sidebars.get(tab_name, {}):
            sidebar, position = self.sidebars[tab_name][key]
            self.sidebar_position = position
            self._add_sidebar(sidebar)
            self.active_sidebar = key
            logger.debug(f"Opened sidebar '{key}' on tab '{tab_name}'")

    def hide_sidebar(self):
        """Hides the currently active sidebar."""
        if self.active_sidebar and self.active_tab:
            sidebar, _ = self.sidebars[self.active_tab][self.active_sidebar]
            self.paned.forget(sidebar)
            sidebar.pack_forget()
            logger.debug(f"Closed sidebar '{self.active_sidebar}' on tab '{self.active_tab}'")
            self.active_sidebar = None
            self.sidebar_frame = None

    def _add_sidebar(self, sidebar):
        """Adds the sidebar to the correct position."""
        if self.sidebar_frame:
            self.paned.forget(self.sidebar_frame)

        if self.sidebar_position == "right":
            self.paned.add(sidebar, weight=1)
        else:
            self.paned.insert(0, sidebar, weight=1)  # Left by default

        self.sidebar_frame = sidebar
        logger.debug(f"Sidebar placed on the {self.sidebar_position}")

    def close_sidebar(self, event=None):
        """Closes sidebar when switching tabs."""
        self.hide_sidebar()


class TestSidebar(ttk.Frame):
    """A sidebar with a button to toggle its position."""

    def __init__(self, parent, tab_name, sidebar_manager, key):
        super().__init__(parent, width=200, relief="sunken", padding=10)
        self.sidebar_manager = sidebar_manager
        self.tab_name = tab_name
        self.key = key

        ttk.Label(self, text=f"Sidebar for {tab_name}", font=("Arial", 12)).pack(pady=10)

        ttk.Button(self, text="Close", command=self.sidebar_manager.hide_sidebar).pack(pady=5)
        ttk.Button(self, text="Move Right", command=lambda: self.change_sidebar_position("right")).pack(pady=5)
        ttk.Button(self, text="Move Left", command=lambda: self.change_sidebar_position("left")).pack(pady=5)

    def change_sidebar_position(self, position):
        """Change sidebar position (left/right) and re-add it."""
        self.sidebar_manager.sidebars[self.tab_name][self.key] = (self, position)
        self.sidebar_manager.hide_sidebar()
        self.sidebar_manager.toggle_sidebar(self.tab_name, self.key)


class TestTab(ttk.Frame):
    """A sample tab with sidebars."""

    def __init__(self, parent, sidebar_manager, tab_name, multiple_sidebars=False):
        super().__init__(parent)
        self.sidebar_manager = sidebar_manager
        self.tab_name = tab_name

        ttk.Label(self, text=f"This is {tab_name}!", font=("Arial", 14)).pack(pady=10)
        ttk.Button(self, text=f"Toggle {tab_name} Sidebar",
                   command=lambda: self.sidebar_manager.toggle_sidebar(self.tab_name, "sidebar")).pack(pady=5)
        sidebar = TestSidebar(parent.master, self.tab_name, self.sidebar_manager, "sidebar")
        self.sidebar_manager.register_sidebar(self.tab_name, "sidebar", sidebar)

        if multiple_sidebars:
            ttk.Button(self, text=f"Toggle {tab_name} Sidebar 2",
                       command=lambda: self.sidebar_manager.toggle_sidebar(self.tab_name, "sidebar2")).pack(pady=5)
            sidebar2 = TestSidebar(parent.master, self.tab_name, self.sidebar_manager, "sidebar2")
            self.sidebar_manager.register_sidebar(self.tab_name, "sidebar2", sidebar2)


if __name__ == "__main__":
    root = tk.Tk()
    root.geometry("800x600")
    root.title("Sidebar Prototype")

    app = SidebarManager(root)
    root.mainloop()
