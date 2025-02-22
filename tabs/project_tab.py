import logging
import tkinter as tk
from tkinter import ttk, filedialog

from phomod_widgets import PHOMODFrame, PHOMODLabel
from _prototypes.image_manipulation_prototype import ImageViewerWidget

app_logger = logging.getLogger('FOMODLogger')


class ProjectTab(PHOMODFrame):
    def __init__(self, parent, controller, *args, **kwargs):
        super().__init__(parent, controller=controller, *args, **kwargs)
        self.controller = controller
        self.active_sidebar = None  # No sidebar is open by default
        app_logger.info("Initializing ProjectTab")
        self.create_widgets()

    def create_widgets(self):
        self.create_sidebar_buttons()
        ttk.Separator(self, orient="horizontal").pack(fill=tk.X, padx=5, pady=3)  # Divider below buttons
        self.create_paned_area()

    def create_sidebar_buttons(self):
        """Creates the sidebar toggle buttons with spacing."""
        button_frame = ttk.Frame(self)
        button_frame.pack(fill=tk.X, padx=5, pady=(8, 5))  # Extra padding on top

        # 📂 Toggle for Project Manager
        self.toggle_sidebar_label = PHOMODLabel(
            button_frame,
            text="▶ Project Manager",
            help_text="Click to show/hide the Project Manager.",
            cursor="hand2",
            font=("Arial", 10, "bold"),
            anchor="w"
        )
        self.toggle_sidebar_label.pack(fill=tk.X, padx=5, pady=(0, 2))  # Stacked vertically
        self.toggle_sidebar_label.bind("<Button-1>", lambda e: self.toggle_sidebar("sidebar"))

        # 📝 Toggle for Plugin Details
        self.toggle_details_label = PHOMODLabel(
            button_frame,
            text="▶ Plugin Details",
            help_text="Click to show/hide Plugin Details.",
            cursor="hand2",
            font=("Arial", 10, "bold"),
            anchor="w"
        )
        self.toggle_details_label.pack(fill=tk.X, padx=5, pady=(2, 0))
        self.toggle_details_label.bind("<Button-1>", lambda e: self.toggle_sidebar("details"))

    def create_paned_area(self):
        """Creates the main editor area with optional sidebars."""
        self.paned = ttk.PanedWindow(self, orient=tk.HORIZONTAL)
        self.paned.pack(fill=tk.BOTH, expand=True)

        self.sidebar = ttk.Frame(self.paned, width=250)  # No border
        self.details_sidebar = ttk.Frame(self.paned, width=250)  # No border

        self.create_project_manager_sidebar()
        self.create_main_area()
        self.create_plugin_details_sidebar()

        # Start with no sidebars visible
        self.paned.add(self.main_frame, weight=3)

    def create_project_manager_sidebar(self):
        """Sidebar for managing projects (includes recent projects + directory picker)."""
        frame = ttk.Frame(self.sidebar)
        frame.pack(fill=tk.BOTH, expand=True, padx=(5, 0), pady=5)

        # 📂 Directory Picker
        ttk.Label(frame, text="Project Directory:").pack(anchor="w", padx=5, pady=2)

        self.project_entry = ttk.Entry(frame, width=40)
        self.project_entry.pack(fill=tk.X, padx=5, pady=2)

        # Move Browse & Load buttons **below** the entry field
        button_frame = ttk.Frame(frame)
        button_frame.pack(fill=tk.X, padx=5, pady=(2, 5))

        ttk.Button(button_frame, text="Browse", command=self.select_folder).pack(side="left", expand=True, fill=tk.X,
                                                                                 padx=2)
        ttk.Button(button_frame, text="Load", command=self.load_project).pack(side="left", expand=True, fill=tk.X,
                                                                              padx=2)

        ttk.Separator(frame, orient="horizontal").pack(fill=tk.X, padx=5, pady=5)

        # 📋 Recent Projects List
        ttk.Label(frame, text="Recent Projects:").pack(anchor="w", padx=5, pady=2)

        listbox_frame = ttk.Frame(frame)
        listbox_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=2)

        self.recent_projects = tk.Listbox(listbox_frame, height=10)
        self.recent_projects.pack(side="left", fill=tk.BOTH, expand=True)

        list_scroll = ttk.Scrollbar(listbox_frame, orient="vertical", command=self.recent_projects.yview)
        list_scroll.pack(side="right", fill="y")
        self.recent_projects.configure(yscrollcommand=list_scroll.set)

        self.recent_projects.bind("<Double-Button-1>", self.load_recent_project)

    def create_main_area(self):
        """Main project area with mod tree structure."""
        self.main_frame = ttk.Frame(self.paned)

        tree_frame = ttk.Frame(self.main_frame)
        tree_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        self.tree = ttk.Treeview(
            tree_frame,
            columns=("Type", "Install Type", "Desc?", "Img?"),
            show="tree headings"
        )
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

        self.tree.pack(side="left", fill=tk.BOTH, expand=True, padx=(0,0), pady=(5,5))
        tree_scroll = ttk.Scrollbar(tree_frame, orient="vertical", command=self.tree.yview)
        tree_scroll.pack(side="right", fill="y", padx=(0,5), pady=(5,5))
        self.tree.configure(yscrollcommand=tree_scroll.set)

        self.tree.bind("<<TreeviewSelect>>", self.on_tree_select)

    def create_plugin_details_sidebar(self):
        """Sidebar for plugin details with an adjustable divider (cleaner borders)."""
        self.details_paned = ttk.PanedWindow(self.details_sidebar, orient=tk.VERTICAL)
        self.details_paned.pack(fill=tk.BOTH, expand=True, padx=(10, 5), pady=(0, 11))  # ⬅️ Bottom padding

        # 📸 Plugin Image Section
        image_frame = ttk.LabelFrame(self.details_paned, text="Plugin Image")
        self.details_paned.add(image_frame, weight=1)
        self.image_viewer = ImageViewerWidget(image_frame)
        self.image_viewer.pack(fill=tk.BOTH, expand=True, padx=0, pady=0)

        # 📝 Description Section
        desc_frame = ttk.LabelFrame(self.details_paned, text="Description", padding=0)
        self.details_paned.add(desc_frame, weight=1)

        # Textbox + Scrollbar Frame
        text_frame = ttk.Frame(desc_frame)
        text_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=(0, 0))

        self.description_text = tk.Text(text_frame, height=4, width=30, wrap=tk.WORD)
        text_scroll = ttk.Scrollbar(text_frame, orient="vertical", command=self.description_text.yview)
        self.description_text.configure(yscrollcommand=text_scroll.set)

        self.description_text.pack(side="left", fill=tk.BOTH, expand=True)
        text_scroll.pack(side="right", fill="y")  # Scrollbar on the right

    def select_folder(self):
        folder = filedialog.askdirectory()
        if folder:
            self.project_entry.delete(0, tk.END)
            self.project_entry.insert(0, folder)
            self.load_project()

    def load_project(self):
        path = self.project_entry.get()
        if path:
            app_logger.info(f"Loading project: {path}")

    def load_recent_project(self, event):
        selected_index = self.recent_projects.curselection()
        if selected_index:
            self.project_entry.delete(0, tk.END)
            self.project_entry.insert(0, self.recent_projects.get(selected_index))
            self.load_project()

    def toggle_sidebar(self, sidebar):
        """Ensures only one sidebar is open at a time or closes both."""
        if sidebar == self.active_sidebar:
            self.paned.forget(self.sidebar if sidebar == "sidebar" else self.details_sidebar)
            self.toggle_sidebar_label.config(text="▶ Project Manager")
            self.toggle_details_label.config(text="▶ Plugin Details")
            self.active_sidebar = None  # No sidebar active
        else:
            # Close any currently open sidebar first
            if self.active_sidebar:
                self.paned.forget(self.sidebar if self.active_sidebar == "sidebar" else self.details_sidebar)

            # Open the requested sidebar
            if sidebar == "sidebar":
                self.paned.insert(0, self.sidebar, weight=1)
                self.toggle_sidebar_label.config(text="◀ Project Manager")
                self.toggle_details_label.config(text="▶ Plugin Details")
            else:
                self.paned.insert(0, self.details_sidebar, weight=1)
                self.toggle_sidebar_label.config(text="▶ Project Manager")
                self.toggle_details_label.config(text="◀ Plugin Details")

            self.active_sidebar = sidebar

    def on_tree_select(self, event):
        """Handles selection changes in the tree view."""
        selected = self.tree.selection()
        has_selection = bool(selected)

        # Toggle Plugin Details based on selection
        self.toggle_sidebar("details" if has_selection else None)

        app_logger.info(f"Tree selection changed: {selected}")
