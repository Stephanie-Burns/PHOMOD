
import random
import tkinter as tk
from ttkthemes import ThemedTk
import logging
import os
import threading
import random
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, font

from prototype_image_manip import ImageViewerWidget
from phomod_widgets import PHOMODFrame, PHOMODLabel, PHOMODComboBox, PHOMODButton, PHOMODLabelFrame, PHOMODCheckbutton, PHOMODEntry

app_logger = logging.getLogger('FOMODLogger')


# ----------------------------
# ThemeManager: Centralize theme logic.
# ----------------------------


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



# ----------------------------
# ProjectTab: Handles project selection, recent projects, and mod tree view.
# ----------------------------
class ProjectTab(PHOMODFrame):
    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.sidebar_visible = True
        app_logger.info("Initializing ProjectTab")
        self.create_widgets()

    def create_widgets(self):
        self.create_top_bar()
        self.create_paned_area()

    def create_top_bar(self):
        top_bar = ttk.Frame(self)
        top_bar.pack(fill=tk.X, padx=5, pady=5)
        self.toggle_label = PHOMODLabel(
            top_bar,
            text="◀ Recent Projects",
            help_text="Click to collapse or expand the Recent Projects sidebar.",
            cursor="hand2",
            font=("Arial", 10, "bold"),
            anchor="w"
        )


        self.toggle_label.pack(side="left", fill=tk.X, expand=True, padx=(0, 10))
        self.toggle_label.bind("<Button-1>", self.toggle_sidebar)
        self.help_text = ""

        folder_frame = ttk.Frame(top_bar)
        folder_frame.pack(side="left", fill=tk.X, expand=True)
        self.project_label = ttk.Label(folder_frame, text="Select a Mod Folder:")
        self.project_label.pack(side="left", padx=(0, 5))
        self.project_entry = ttk.Entry(folder_frame, width=40)
        self.project_entry.pack(side="left", fill=tk.X, expand=True, padx=(0, 10))
        self.browse_button = ttk.Button(folder_frame, text="Browse", command=self.select_folder)
        self.browse_button.pack(side="left")

    def create_paned_area(self):
        self.paned = ttk.PanedWindow(self, orient=tk.HORIZONTAL)
        self.paned.pack(fill=tk.BOTH, expand=True)
        self.create_sidebar()
        self.create_main_area()

    def create_sidebar(self):
        self.sidebar = ttk.Frame(self.paned, width=200)
        self.paned.add(self.sidebar, weight=1)
        listbox_frame = ttk.Frame(self.sidebar)
        listbox_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.recent_projects = tk.Listbox(listbox_frame, height=10)
        self.recent_projects.pack(side="left", fill=tk.BOTH, expand=True)
        list_scroll = ttk.Scrollbar(listbox_frame, orient="vertical", command=self.recent_projects.yview)
        list_scroll.pack(side="right", fill="y")
        self.recent_projects.configure(yscrollcommand=list_scroll.set)
        self.recent_projects.bind("<Double-Button-1>", self.load_recent_project)

    def create_main_area(self):
        self.main_frame = ttk.Frame(self.paned)
        self.paned.add(self.main_frame, weight=3)
        tree_frame = ttk.Frame(self.main_frame)
        tree_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.tree = ttk.Treeview(tree_frame,
                                 columns=("Type", "Install Type", "Desc?", "Img?"),
                                 show="tree headings")
        self.tree.heading("#0", text="Structure")
        self.tree.heading("Type", text="Category")
        self.tree.heading("Install Type", text="Install Type")
        self.tree.heading("Desc?", text="📝")
        self.tree.heading("Img?", text="🖼️")
        self.tree.column("#0", minwidth=100)
        self.tree.column("Type", minwidth=100)
        self.tree.column("Install Type", width=130, stretch=False)
        self.tree.column("Desc?", width=35, stretch=False)
        self.tree.column("Img?", width=35, stretch=False)
        self.tree.pack(side="left", fill=tk.BOTH, expand=True)
        tree_scroll = ttk.Scrollbar(tree_frame, orient="vertical", command=self.tree.yview)
        tree_scroll.pack(side="right", fill="y")
        self.tree.configure(yscrollcommand=tree_scroll.set)
        self.tree.bind("<<TreeviewSelect>>", self.on_tree_select)

    def toggle_sidebar(self, event=None):
        app_logger.info("Toggling sidebar visibility")
        if self.sidebar_visible:
            self.paned.forget(self.sidebar)
            self.toggle_label.config(text="▶ Recent Projects")
        else:
            self.paned.insert(0, self.sidebar, weight=1)
            self.toggle_label.config(text="◀ Recent Projects")
        self.sidebar_visible = not self.sidebar_visible

    def select_folder(self):
        folder = filedialog.askdirectory()
        if folder:
            app_logger.info(f"Folder selected: {folder}")
            self.project_entry.delete(0, tk.END)
            self.project_entry.insert(0, folder)

    def load_recent_project(self, event):
        selected_index = self.recent_projects.curselection()
        if selected_index:
            selected_path = self.recent_projects.get(selected_index)
            app_logger.info(f"Loading recent project: {selected_path}")
            self.project_entry.delete(0, tk.END)
            self.project_entry.insert(0, selected_path)

    def on_tree_select(self, event):
        selected = self.tree.selection()
        app_logger.info(f"Tree selection changed: {selected}")
        self.controller.toggle_details_tab(enable=bool(selected))


# ----------------------------
# DetailsTab: Handles plugin details, including an image viewer and description editor.
# ----------------------------
class DetailsTab(PHOMODFrame):
    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        app_logger.info("Initializing DetailsTab")
        self.create_widgets()

    def create_widgets(self):
        paned = ttk.PanedWindow(self, orient=tk.HORIZONTAL)
        paned.pack(fill=tk.BOTH, expand=True)
        left_frame = ttk.Frame(paned, width=250)
        paned.add(left_frame, weight=1)
        ttk.Label(left_frame, text="Plugin Image:").pack(anchor="w", padx=5, pady=5)
        self.image_viewer = ImageViewerWidget(left_frame, width=250, height=150)
        self.image_viewer.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        right_frame = ttk.Frame(paned)
        paned.add(right_frame, weight=3)
        ttk.Label(right_frame, text="Description:").pack(anchor="w", padx=5, pady=5)
        self.description_text = tk.Text(right_frame, height=10, wrap=tk.WORD)
        self.description_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        app_logger.info("DetailsTab widgets created")

    def get_image_path(self):
        return self.image_viewer.get_image_path()


# ----------------------------
# XMLTab: Shows generated XML preview and export.
# ----------------------------
class XMLTab(PHOMODFrame):
    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        app_logger.info("Initializing XMLTab")
        self.create_widgets()

    def create_widgets(self):
        ttk.Label(self, text="Generated FOMOD XML:").pack(anchor="w", padx=5, pady=5)
        self.xml_preview = tk.Text(self, wrap=tk.WORD, height=20)
        self.xml_preview.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.generate_button = ttk.Button(self, text="Generate XML", command=self.start_generate_xml)
        self.generate_button.pack(pady=5, padx=5)
        app_logger.info("XMLTab widgets created")

    def start_generate_xml(self):
        app_logger.info("Starting XML generation")
        threading.Thread(target=self.generate_xml, daemon=True).start()

    def generate_xml(self):
        self.xml_preview.delete("1.0", tk.END)
        self.xml_preview.insert("1.0", "<config>\n  <!-- XML Content Here -->\n</config>")
        app_logger.info("XML generated")


# ----------------------------
# SettingsTab: Handles theme selection and additional settings.
# ----------------------------
class SettingsTab(PHOMODFrame):
    def __init__(self, parent, controller, *args, **kwargs):
        super().__init__(parent, controller=controller, *args, **kwargs)
        self.controller = controller
        self.create_scrollable_widgets()
        app_logger.info("SettingsTab initialized.")
        # Manually test status update when the tab is created
        self.controller.update_status("🛠️ Settings loaded successfully!")

    def create_scrollable_widgets(self):
        """Creates a scrollable frame for settings."""
        container = PHOMODFrame(self)
        container.pack(fill=tk.BOTH, expand=True)

        self.canvas = tk.Canvas(container, borderwidth=0, highlightthickness=0)
        vsb = tk.Scrollbar(container, orient="vertical", command=self.canvas.yview)
        self.canvas.configure(yscrollcommand=vsb.set)

        vsb.pack(side="right", fill="y")
        self.canvas.pack(side="left", fill=tk.BOTH, expand=True)

        # Create an inner frame to hold all settings widgets
        self.inner_frame = PHOMODFrame(self.canvas, controller=self.controller)  # Pass controller
        self.inner_window = self.canvas.create_window((0, 0), window=self.inner_frame, anchor="nw")

        self.inner_frame.bind("<Configure>", self._on_frame_configure)
        self.canvas.bind("<Configure>", self._on_canvas_configure)

        self.create_widgets_in_inner()

    def _on_frame_configure(self, event):
        """Updates scroll region when the inner frame resizes."""
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def _on_canvas_configure(self, event):
        """Ensures the inner window resizes correctly."""
        self.canvas.itemconfigure(self.inner_window, width=event.width)

    def create_widgets_in_inner(self):
        """Creates all settings widgets inside the scrollable frame."""

        # ==== Theme Selection Section ====
        theme_frame = PHOMODLabelFrame(
            self.inner_frame,
            text="Theme Selection",
            help_text="Change the application's theme."
        )
        theme_frame.pack(fill=tk.X, padx=5, pady=5, expand=True)

        theme_options = self.controller.theme_manager.get_theme_options()
        self.theme_var = tk.StringVar(value="Default")

        self.theme_menu = PHOMODComboBox(
            theme_frame,
            textvariable=self.theme_var,
            values=theme_options,
            state="readonly",
            help_text="Select a theme for the application interface.",
        )
        self.theme_menu.pack(fill=tk.X, padx=5, pady=5)
        self.theme_menu.bind("<<ComboboxSelected>>", self.apply_theme)

        self.current_theme_label = PHOMODLabel(
            theme_frame,
            font=self.controller.fonts["italic"],
            text=f"Current Theme: {self.controller.theme_manager.get_theme()}",
            help_text="Displays the currently active theme."
        )
        self.current_theme_label.pack(pady=5)

        app_logger.info("Theme selection section created.")

        # ==== Logging Settings Section ====
        log_frame = PHOMODLabelFrame(
            self.inner_frame,
            text="Logging Settings",
            help_text="Adjust logging settings and levels."
        )
        log_frame.pack(fill=tk.X, padx=5, pady=10, expand=True)

        PHOMODLabel(
            log_frame, text="Log Level:", help_text="Choose the level of detail for logs."
        ).pack(anchor="w", padx=5, pady=(5, 0))

        self.log_level_var = tk.StringVar(value="INFO")

        self.log_level_menu = PHOMODComboBox(
            log_frame,
            textvariable=self.log_level_var,
            state="readonly",
            values=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
            help_text="Select the minimum log level for displayed logs.",
        )
        self.log_level_menu.pack(fill=tk.X, padx=5, pady=(5, 25))

        PHOMODButton(
            log_frame,
            text="Configure Rotation",
            help_text="Set up automatic log rotation.",
            command=self.configure_log_rotation
        ).pack(padx=5, pady=5)

        app_logger.info("Logging settings section created.")

        # ==== Update Settings Section ====
        update_frame = PHOMODLabelFrame(
            self.inner_frame,
            text="Update Settings",
            help_text="Configure automatic update checks."
        )
        update_frame.pack(fill=tk.X, padx=5, pady=10, expand=True)

        self.auto_update_var = tk.BooleanVar(value=True)

        PHOMODCheckbutton(
            update_frame,
            text="Automatically check for updates",
            variable=self.auto_update_var,
            help_text="Enable or disable automatic update checks."
        ).pack(anchor="w", padx=5, pady=5)

        PHOMODButton(
            update_frame,
            text="Check Now",
            help_text="Manually check for updates.",
            command=self.check_for_updates
        ).pack(padx=5, pady=5)

        app_logger.info("Update settings section created.")

        # ==== Language Section ====
        lang_frame = PHOMODLabelFrame(
            self.inner_frame,
            text="Language",
            help_text="Set the application language."
        )
        lang_frame.pack(fill=tk.X, padx=5, pady=10, expand=True)

        PHOMODLabel(
            lang_frame,
            text="Select Language:",
            help_text="Choose a language for the UI."
        ).pack(anchor="w", padx=5, pady=(5, 0))

        self.lang_var = tk.StringVar(value="English")
        self.lang_menu = PHOMODComboBox(
            lang_frame,
            textvariable=self.lang_var,
            values=["English", "Spanish", "French", "German"],
            state="readonly",
            help_text="Select the language for the application."
        )
        self.lang_menu.pack(anchor="w", padx=5, pady=5)

        PHOMODButton(
            lang_frame,
            text="Help Translate",
            help_text="Assist in translating the app into other languages.",
            command=self.ask_for_translation_help
        ).pack(padx=5, pady=(5, 25))

        app_logger.info("Language settings section created.")

        # ==== About Section ====
        about_frame = PHOMODLabelFrame(
            self.inner_frame,
            text="About",
            help_text="View information about PHOMOD."
        )
        about_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=10)

        about_text = (
            "PHOMOD - Mod Organizer\nVersion 1.0\n\n"
            "Developed by Stephanie Burns\n"
            "Visit the GitHub repository for more info!"
        )

        PHOMODLabel(
            about_frame,
            text=about_text,
            help_text="Application version and credits.",
            anchor="center",
            justify="center"
        ).pack(expand=True, padx=5, pady=5)

        self.after(0, lambda: self.apply_theme(None))

        app_logger.info("About section created.")
        app_logger.info("SettingsTab widgets created successfully.")

    def apply_theme(self, event=None):
        """Applies the selected theme and updates the UI."""
        selected_theme = self.theme_var.get()

        if selected_theme == self.controller.theme_manager.separator:
            self.controller.update_status("Please select a valid theme.")
            return

        applied_theme = self.controller.theme_manager.apply_theme(selected_theme)
        if applied_theme:
            display_theme = f"Random - {applied_theme.capitalize()}" if selected_theme.lower() == "random" else applied_theme.capitalize()
            self.current_theme_label.config(text=f"Current Theme: {display_theme}")
            self.controller.update_status(f"Theme set to {display_theme}.")
            app_logger.info(f"Theme applied: {display_theme}")

    def configure_log_rotation(self):
        """Handles log rotation configuration."""
        self.controller.update_status("Log rotation configuration is not yet implemented.")
        app_logger.info("Configure log rotation button pressed.")

    def check_for_updates(self):
        """Simulates checking for updates."""
        self.controller.update_status("Checking for updates...")
        app_logger.info("Checking for updates...")
        threading.Timer(2.0, lambda: self.controller.update_status("No updates available.")).start()
        app_logger.info("Update check completed.")

    def ask_for_translation_help(self):
        """Opens a dialog for translation assistance."""
        self.controller.update_status("Translation help requested.")
        app_logger.info("Translation help button pressed.")
        messagebox.showinfo("Translation Help", "Please visit our GitHub page to contribute translations.")


# ----------------------------
# DocumentationTab: In-app help and documentation.
# ----------------------------



class DocumentationTab(PHOMODFrame):
    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        app_logger.info("Initializing DocumentationTab")
        self.create_widgets()

    def create_widgets(self):
        ttk.Label(self, text="PHOMOD Documentation", font=("Arial", 14, "bold")).pack(pady=10)
        doc_text = (
            "Welcome to PHOMOD! This tool helps you generate and package FOMOD installers for your mods.\n\n"
            "- 📂 Project Tab: Select or browse your mod directory.\n"
            "- 🎨 Details Panel: Modify descriptions and images for plugins.\n"
            "- 📜 XML Preview: See and export your generated FOMOD XML.\n"
            "- ⚙️ Settings: Customize themes and preferences.\n\n"
            "For more info, visit the PHOMOD GitHub repository."
        )
        self.doc_text = tk.Text(self, wrap=tk.WORD, height=15)
        self.doc_text.insert("1.0", doc_text)
        self.doc_text.configure(state="disabled")
        self.doc_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        app_logger.info("DocumentationTab widgets created")


# ----------------------------
# LogsTab: Displays application event logs.
# ----------------------------
class LogsTab(PHOMODFrame):
    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        app_logger.info("Initializing LogsTab")
        self.create_widgets()

    def create_widgets(self):
        ttk.Label(self, text="Event Logs:").pack(anchor="w", padx=5, pady=5)
        self.log_text = tk.Text(self, wrap=tk.WORD, height=10, state="disabled")
        self.log_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        app_logger.info("LogsTab widgets created")

# ----------------------------
# PhomodUI: Main application window managing tabs, status bar, and theme logic.
# ----------------------------
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
        }

    def create_notebook(self):
        """Creates a notebook (tab container)."""
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill=tk.BOTH, expand=True, pady=(5, 0))

    def create_tabs(self):
        """Initializes and adds all application tabs."""
        self.tab_config = {
            "project": {"default": "📦", "active": "🚚", "label": "Project", "class": ProjectTab},
            "details": {"default": "🖌️", "active": "🎨", "label": "Details", "class": DetailsTab},
            "xml": {"default": "🍳", "active": "🍽️", "label": "XML Preview", "class": XMLTab},
            "logs": {"default": "🌲", "active": "🪵", "label": "Logs", "class": LogsTab},
            "settings": {"default": "⚙️", "active": "🔧", "label": "Settings", "class": SettingsTab},
            "docs": {"default": "📔", "active": "📖", "label": "Help", "class": DocumentationTab},
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
        self.help_manager = HelpTextManager(self.status_var)  # ✅ Ensure HelpTextManager is initialized
        self.status_bar = ttk.Label(self, textvariable=self.status_var, relief=tk.SUNKEN, anchor="w")
        self.status_bar.pack(side="bottom", fill="x", padx=5, pady=5)

    def toggle_tab_emoji(self, event):
        """Changes the emoji of the active tab."""
        current_tab_id = self.notebook.index(self.notebook.select())
        current_text = self.notebook.tab(current_tab_id, "text")
        for key, config in self.tab_config.items():
            if config["label"] in current_text:
                new_text = f" {config['active']}   {config['label']}    "
                break
        else:
            return
        for tab_id in range(self.notebook.index("end")):
            tab_text = self.notebook.tab(tab_id, "text")
            for key, config in self.tab_config.items():
                if config["label"] in tab_text:
                    self.notebook.tab(tab_id, text=f" {config['default']}   {config['label']}    ")
        self.notebook.tab(current_tab_id, text=new_text)
        app_logger.info(f"Switched to tab: {current_text}")

    def toggle_details_tab(self, enable=True):
        """Enables or disables the Details tab based on selection."""
        details_index = None
        for i in range(self.notebook.index("end")):
            tab_text = self.notebook.tab(i, "text")
            if self.tab_config["details"]["label"] in tab_text:
                details_index = i
                break
        if details_index is not None:
            state = "normal" if enable else "disabled"
            self.notebook.tab(details_index, state=state)
            app_logger.info(f"Details tab {'enabled' if enable else 'disabled'}.")

    def update_status(self, message):
        """Updates the status bar text."""
        self.status_var.set(message)
        app_logger.debug(f"Status updated: {message}")

if __name__ == "__main__":
    from logger_config import app_logger
    app_logger.info("Application started")

    app = PhomodUI()
    app.mainloop()
