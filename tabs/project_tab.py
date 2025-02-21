
import logging
import tkinter as tk
from tkinter import ttk, filedialog

from base_tab import BaseTab


app_logger = logging.getLogger('FOMODLogger')


class ProjectTab(BaseTab):
    def __init__(self, parent, controller, *args, **kwargs):
        super().__init__(parent, controller, *args, **kwargs)
        self.sidebar_visible = True
        app_logger.info("Initializing ProjectTab")
        self.create_widgets()

    def create_widgets(self):
        self.create_top_bar()
        self.create_paned_area()

    def create_top_bar(self):
        top_bar = ttk.Frame(self)
        top_bar.pack(fill=tk.X, padx=5, pady=5)
        self.toggle_label = ttk.Label(top_bar, text="◀ Recent Projects",
                                      cursor="hand2", font=("Arial", 10, "bold"), anchor="w")
        self.toggle_label.pack(side="left", fill=tk.X, expand=True, padx=(0, 10))
        self.toggle_label.bind("<Button-1>", self.toggle_sidebar)
        self.bind_help_message(self.toggle_label, "Click to collapse or expand the Recent Projects sidebar.")

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
