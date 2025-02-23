
import logging
import random
import tkinter as tk
from ttkthemes import ThemedTk
from tkinter import ttk, font

from tabs import (
    ProjectTab,
    DetailsTab,
    XMLTab,
    LogsTab,
    SettingsTab,
    DocumentationTab,
)

app_logger = logging.getLogger('FOMODLogger')



class ThemeManager:
    def __init__(self, root):
        self.root = root
        self.style = ttk.Style(self.root)
        self.separator = "----------"
        self.themes_always_on_top = ["Default", "Random"]

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
        """Apply the selected theme to the application and return the applied theme's name."""
        if theme == self.separator:
            print("Please select a valid theme.")
            return None
        if theme.lower() == "random":
            all_themes = self.get_themes()
            choices = [t for t in all_themes if t.lower() != "default"]
            theme = random.choice(choices) if choices else "default"
        try:
            self.root.set_theme(theme.lower())
            print(f"Applied theme: {theme}")
            self.root.update_idletasks()
            return theme  # Return the name of the applied theme
        except tk.TclError as e:
            print(f"Error applying theme '{theme}': {e}")
            return None


class HelpTextManager:
    """Centralized help text manager that binds tooltips to widgets and updates a status bar."""

    def __init__(self, status_var: tk.StringVar):
        """
        Initializes the help text manager.

        :param status_var: The StringVar used for the status bar.
        """
        self.status_var = status_var

    def bind_help(self, widget, help_text: str):
        """
        Binds a help message to a widget. When hovered, it updates the status bar.

        :param widget: The Tkinter widget to bind the help text to.
        :param help_text: The help text to display when hovering over the widget.
        """
        if help_text:
            widget.bind("<Enter>", lambda event: self.update_status(help_text))
            widget.bind("<Leave>", lambda event: self.update_status("Ready"))
            app_logger.info(f"🔗 Help text bound: '{help_text}' to {widget.__class__.__name__}")

    def update_status(self, message):
        """Updates the status bar text."""
        self.status_var.set(message)
        app_logger.info(f"📢 Status updated: {message}")


class PhomodUI(ThemedTk):
    def __init__(self):
        super().__init__(theme="arc")
        self.setup_ui()
        app_logger.info("Application started.")

    def setup_ui(self):
        """Sets up the main UI components."""
        self.configure_window()
        self.create_style()
        self.create_fonts()
        self.create_status_bar()
        self.create_notebook()
        self.create_tabs()
        self.notebook.bind("<<NotebookTabChanged>>", self.toggle_tab_emoji)

    def configure_window(self):
        """Configures the main window properties."""
        self.title("PHOMOD - Mod Organizer")
        self.geometry("1000x618")
        self.minsize(width=1000, height=550)

    def create_style(self):
        """Initializes and applies the default theme."""
        self.style = ttk.Style(self)
        self.theme_manager = ThemeManager(self)
        self.theme_manager.apply_theme("arc")  # Apply default theme

    def create_fonts(self):
        """Initializes and stores custom fonts."""
        self.fonts = {
            "italic": font.Font(family="Helvetica", size=10, slant="italic"),
            "bold": font.Font(family="Helvetica", size=10, weight="bold"),
            "default": font.Font(family="Helvetica", size=10),
            "title": font.Font(family="Helvetica", size=12, weight="bold"),
        }

    def create_notebook(self):
        """Creates a notebook (tab container)."""
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill=tk.BOTH, expand=True, pady=(5, 0))

    def create_tabs(self):
        """Initializes and adds all application tabs."""
        self.tab_config = {
            "project":      {"default": "📦", "active": "🚚", "label": "Project", "class": ProjectTab},
            # "details":      {"default": "🖌️", "active": "🎨", "label": "Details", "class": DetailsTab},
            "xml":          {"default": "🍳", "active": "🍽️", "label": "XML Preview", "class": XMLTab},
            "logs":         {"default": "🌲", "active": "🪵", "label": "Logs", "class": LogsTab},
            "settings":     {"default": "⚙️", "active": "🔧", "label": "Settings", "class": SettingsTab},
            "docs":         {"default": "📔", "active": "📖", "label": "Help", "class": DocumentationTab},
        }
        self.tabs = {}
        for key, config in self.tab_config.items():
            tab_frame = config["class"](self.notebook, controller=self)
            self.notebook.add(tab_frame, text=f" {config['default']}   {config['label']}")
            self.tabs[key] = tab_frame
            app_logger.info(f"Tab created: {config['label']}")

    def create_status_bar(self):
        """Creates a status bar at the bottom of the window."""
        self.status_var = tk.StringVar(value="Ready")
        self.help_manager = HelpTextManager(self.status_var)
        self.status_bar = ttk.Label(self, textvariable=self.status_var, relief=tk.SUNKEN, anchor="w",border=2)
        self.status_bar.pack(side="bottom", fill="x", padx=5, pady=(5,5))

    def update_status_bar_text(self, message):
        """Updates the status bar text."""
        self.status_var.set(message)
        app_logger.debug(f"Status updated: {message}")

    def toggle_tab_emoji(self, event):
        """Changes the emoji of the active tab and resets others."""
        current_tab_id = self.notebook.index(self.notebook.select())
        current_text = self.notebook.tab(current_tab_id, "text")

        # Find the corresponding config
        for key, config in self.tab_config.items():
            if config["label"] in current_text:
                active_label = f" {config['active']}   {config['label']}    "
                default_label = config["default"]
                break
        else:
            return  # Exit if no matching tab config is found

        # Reset all tabs to default emoji
        for tab_id in range(self.notebook.index("end")):
            tab_text = self.notebook.tab(tab_id, "text")
            for key, config in self.tab_config.items():
                if config["label"] in tab_text:
                    self.notebook.tab(tab_id, text=f" {config['default']}   {config['label']}    ")

        # Set the active tab emoji
        self.notebook.tab(current_tab_id, text=active_label)

        app_logger.info(f"Switched to tab: {current_text}")

    def get_available_tabs(self):
        """Returns a list of available tab labels."""
        return [config["label"] for key, config in self.tab_config.items()]


if __name__ == "__main__":
    from logger_config import app_logger
    app_logger.info("Application started")

    app = PhomodUI()
    app.mainloop()
