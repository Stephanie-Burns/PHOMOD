
import logging
import tkinter as tk
from tkinter import ttk, filedialog

from phomod_widgets import (
    PHOMODFrame, PHOMODLabel, PHOMODTextArea, PHOMODLabelFrame,
    PHOMODEntry, PHOMODButton, PHOMODListbox, PHOMODTreeview
)
from _prototypes.image_manipulation_prototype import ImageViewerWidget

app_logger = logging.getLogger('PHOMODLogger')


# ----------------------------------------------------------------------------------------------------------------------
#                                                                                                    🎚️ Sidebar Toggles
# ----------------------------------------------------------------------------------------------------------------------
class SidebarToggleBar(PHOMODFrame):
    """Interactive widget for toggling sidebars."""

    def __init__(self, parent, toggle_callback, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.toggle_callback = toggle_callback
        self._create_widgets()

    def _create_widgets(self):
        self.loader_toggle = PHOMODLabel(
            self,
            text="▶ Project Loader",
            help_text="Toggle the Project Loader sidebar.",
            cursor="hand2",
            font=("Arial", 10, "bold"),
            anchor="w"
        )
        self.loader_toggle.pack(fill=tk.X, padx=5, pady=(0, 2))
        self.loader_toggle.bind("<Button-1>", lambda e: self.toggle_callback("loader"))

        self.details_toggle = PHOMODLabel(
            self,
            text="▶ Plugin Details",
            help_text="Toggle the Plugin Details sidebar.",
            cursor="hand2",
            font=("Arial", 10, "bold"),
            anchor="w"
        )
        self.details_toggle.pack(fill=tk.X, padx=5, pady=(2, 0))
        self.details_toggle.bind("<Button-1>", lambda e: self.toggle_callback("details"))

    def update_toggle_text(self, sidebar, is_open):
        """Updates toggle labels based on sidebar state."""
        text_map = {
            "loader": "◀ Project Loader" if is_open else "▶ Project Loader",
            "details": "◀ Plugin Details" if is_open else "▶ Plugin Details",
        }
        if sidebar in text_map:
            getattr(self, f"{sidebar}_toggle").config(text=text_map[sidebar])


# ----------------------------------------------------------------------------------------------------------------------
#                                                                                             📂 Project Loader Sidebar
# ----------------------------------------------------------------------------------------------------------------------
class ProjectLoaderSidebar(PHOMODFrame):
    """Sidebar for selecting a project folder and displaying recent projects."""

    def __init__(self, parent, load_callback, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.load_callback = load_callback
        self._create_widgets()

    def _create_widgets(self):
        """Creates the project loader UI components."""
        self.project_dir_var = tk.StringVar()

        frame = PHOMODFrame(self)
        frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        PHOMODLabel(frame, text="Project Directory:").pack(anchor="w", padx=5, pady=2)

        self.project_entry = PHOMODEntry(
            frame, width=40, textvariable=self.project_dir_var, help_text="Select the directory for your project."
        )
        self.project_entry.pack(fill=tk.X, padx=5, pady=2)

        btn_frame = PHOMODFrame(frame)
        btn_frame.pack(fill=tk.X, padx=5, pady=(2, 5))

        PHOMODButton(
            btn_frame, text="Browse", command=self.select_folder
        ).pack(side="left", expand=True, fill=tk.X, padx=2)
        PHOMODButton(
            btn_frame, text="Load", command=self._load_project
        ).pack(side="left", expand=True, fill=tk.X, padx=2)

        ttk.Separator(frame, orient="horizontal").pack(fill=tk.X, padx=5, pady=5)

        PHOMODLabel(frame, text="Recent Projects:").pack(anchor="w", padx=5, pady=2)

        listbox_frame = PHOMODFrame(frame)
        listbox_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=2)

        self.recent_projects = PHOMODListbox(
            listbox_frame, attach_y=True, height=10, help_text="Double-click to load a recent project."
        )
        self.recent_projects.pack(side="left", fill=tk.BOTH, expand=True)
        self.recent_projects.bind("<Double-Button-1>", self._load_recent_project)

    def select_folder(self):
        """Opens a folder dialog and loads the selected project."""
        folder = filedialog.askdirectory()
        if folder:
            self.project_dir_var.set(folder)
            self._load_project()

    def _load_project(self):
        """Loads the selected project path."""
        path = self.project_dir_var.get()
        if path:
            app_logger.info(f"📂 Loading project: {path}")
            self.load_callback(path)

    def _load_recent_project(self, event):
        """Loads a project from the recent projects list."""
        selection = self.recent_projects.curselection()
        if selection:
            project = self.recent_projects.get(selection)
            self.project_dir_var.set(project)
            self._load_project()


# ----------------------------------------------------------------------------------------------------------------------
#                                                                                             🔍 Plugin Details Sidebar
# ----------------------------------------------------------------------------------------------------------------------
class PluginDetailsSidebar(PHOMODFrame):
    """Sidebar displaying plugin image and description."""

    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self._create_widgets()

    def _create_widgets(self):
        """Creates UI elements for plugin details."""
        self.details_paned = ttk.PanedWindow(self, orient=tk.VERTICAL)
        self.details_paned.pack(fill=tk.BOTH, expand=True, padx=(10, 5), pady=(0, 11))

        image_frame = PHOMODLabelFrame(self.details_paned, text="Plugin Image")
        self.details_paned.add(image_frame, weight=1)

        self.image_viewer = ImageViewerWidget(image_frame)
        self.image_viewer.pack(fill=tk.BOTH, expand=True, padx=0, pady=0)

        desc_frame = PHOMODLabelFrame(self.details_paned, text="Description")
        self.details_paned.add(desc_frame, weight=1)

        container = PHOMODFrame(desc_frame)
        container.pack(fill=tk.BOTH, expand=True, padx=5, pady=0)

        self.description_text = PHOMODTextArea(
            container, attach_y=True, height=4, width=37, wrap=tk.WORD,
            help_text="Enter plugin details here."
        )
        self.description_text.pack(side="left", fill=tk.BOTH, expand=True)


# ----------------------------------------------------------------------------------------------------------------------
#                                                                                                 🏗️ ModStructureEditor
# ----------------------------------------------------------------------------------------------------------------------
class ModStructureEditor(PHOMODFrame):
    """Main area where the mod/directory structure is displayed and edited."""

    def __init__(self, parent, tree_select_callback, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.tree_select_callback = tree_select_callback
        self._create_widgets()

    def _create_widgets(self):
        container = PHOMODFrame(self)
        container.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        self.mod_tree = PHOMODTreeview(
            container,
            columns=("Type", "Install Type", "Desc", "Img"),
            show="tree headings",
            attach_y=True
        )
        self.mod_tree.heading("#0", text="Structure")
        self.mod_tree.heading("Type", text="Category")
        self.mod_tree.heading("Install Type", text="Install Type")
        self.mod_tree.heading("Desc", text="📝")
        self.mod_tree.heading("Img", text="🖼️")
        self.mod_tree.column("#0", minwidth=100)
        self.mod_tree.column("Type", minwidth=100)
        self.mod_tree.column("Install Type", width=130, stretch=False)
        self.mod_tree.column("Desc", width=35, stretch=False)
        self.mod_tree.column("Img", width=35, stretch=False)

        self.mod_tree.pack(side="left", fill=tk.BOTH, expand=True, padx=0, pady=5)
        self.mod_tree.bind("<<TreeviewSelect>>", self._on_tree_select)

    def _on_tree_select(self, event):
        selection = self.mod_tree.selection()
        app_logger.info(f"Tree selection changed: {selection}")
        self.tree_select_callback(selection)


# ----------------------------------------------------------------------------------------------------------------------
#                                                                                                        📦 Project Tab
# ----------------------------------------------------------------------------------------------------------------------
class ProjectTab(PHOMODFrame):
    """
    ProjectTab is the main interface where users load a project, view and edit the mod structure,
    and check plugin details. It assembles the SidebarToggleBar, ProjectLoaderSidebar,
    ModStructureEditor, and PluginDetailsSidebar.
    """

    def __init__(self, parent, controller, *args, **kwargs):
        super().__init__(parent, controller=controller, *args, **kwargs)
        self.controller = controller
        self.active_sidebar = None  # Tracks the currently open sidebar ('loader', 'details', or None)

        self._create_widgets()
        app_logger.info("🚀 ProjectTab initialized.")

    def _create_widgets(self):
        """Create UI components and structure."""
        # Sidebar Toggle Bar
        self.toggle_bar = SidebarToggleBar(self, self.toggle_sidebar)
        self.toggle_bar.pack(fill=tk.X, padx=5, pady=(8, 5))
        ttk.Separator(self, orient="horizontal").pack(fill=tk.X, padx=5, pady=3)

        # Main Layout
        self.paned = ttk.PanedWindow(self, orient=tk.HORIZONTAL)
        self.paned.pack(fill=tk.BOTH, expand=True)

        # Sidebar Components
        self.project_loader = ProjectLoaderSidebar(self, self.load_project)
        self.mod_editor = ModStructureEditor(self, self.on_tree_select)
        self.plugin_details = PluginDetailsSidebar(self)

        # Initially, only show the mod structure editor.
        self.paned.add(self.mod_editor, weight=3)

    def load_project(self, path):
        """Handles project loading."""
        app_logger.info(f"📦 Project loaded: {path}")
        # TODO: Implement actual project loading logic.

    def on_tree_select(self, selection):
        """Handles tree selection updates."""
        # Toggle Plugin Details sidebar when a selection exists.
        self.toggle_sidebar("details" if selection else None, force_open=True)

    def toggle_sidebar(self, sidebar_key, force_open=False):
        """
        Toggles sidebar visibility.

        :param sidebar_key: 'loader' for Project Loader, 'details' for Plugin Details, or None to close sidebars.
        :param force_open: If True, forces the sidebar to open even if it's already active.
        """
        # If closing the active sidebar, remove it and reset tracking.
        if sidebar_key is None or (sidebar_key == self.active_sidebar and not force_open):
            if self.active_sidebar:
                self._remove_sidebar(self.active_sidebar)
                self.active_sidebar = None
            return

        # Always remove the currently active sidebar before adding a new one.
        if self.active_sidebar:
            self._remove_sidebar(self.active_sidebar)

        # Add the requested sidebar.
        self._add_sidebar(sidebar_key)

    def _remove_sidebar(self, sidebar_key):
        """Handles sidebar removal logic."""
        sidebar = self.project_loader if sidebar_key == "loader" else self.plugin_details
        self.paned.forget(sidebar)
        self.toggle_bar.update_toggle_text(sidebar_key, False)
        app_logger.info(f"Closed sidebar: {sidebar_key}")

    def _add_sidebar(self, sidebar_key):
        """Handles sidebar addition logic."""
        sidebar = self.project_loader if sidebar_key == "loader" else self.plugin_details
        self.paned.insert(0, sidebar, weight=1)
        self.toggle_bar.update_toggle_text(sidebar_key, True)
        self.active_sidebar = sidebar_key
        app_logger.info(f"Opened sidebar: {sidebar_key}")
