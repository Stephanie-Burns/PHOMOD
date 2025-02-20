import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import threading

class BaseTab(ttk.Frame):
    """A base class for all tabs."""
    def __init__(self, parent, controller, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.controller = controller


class ProjectTab(BaseTab):
    """Project tab containing folder selection, recent projects, and a mod tree view."""
    def __init__(self, parent, controller, *args, **kwargs):
        super().__init__(parent, controller, *args, **kwargs)
        self.create_widgets()

    def create_widgets(self):
        paned = ttk.PanedWindow(self, orient=tk.HORIZONTAL)
        paned.pack(fill=tk.BOTH, expand=True)

        # Sidebar - Recent Projects with a vertical scrollbar.
        sidebar = ttk.Frame(paned, width=200)
        paned.add(sidebar, weight=1)
        ttk.Label(sidebar, text="Recent Projects:").pack(anchor="w", padx=5, pady=5)
        listbox_frame = ttk.Frame(sidebar)
        listbox_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.recent_projects = tk.Listbox(listbox_frame, height=10)
        self.recent_projects.pack(side="left", fill=tk.BOTH, expand=True)
        list_scroll = ttk.Scrollbar(listbox_frame, orient="vertical", command=self.recent_projects.yview)
        list_scroll.pack(side="right", fill="y")
        self.recent_projects.configure(yscrollcommand=list_scroll.set)
        self.recent_projects.bind("<Double-Button-1>", self.load_recent_project)

        # Main Area - Use a frame for folder selection (picker) and a separate frame for the tree.
        main_frame = ttk.Frame(paned)
        paned.add(main_frame, weight=3)

        # Picker frame: does not expand vertically.
        picker_frame = ttk.Frame(main_frame)
        picker_frame.pack(fill=tk.X, padx=5, pady=(32, 10))
        self.project_label = ttk.Label(picker_frame, text="Select a Mod Folder:")
        self.project_label.pack(side="left", padx=(0, 5))
        self.project_entry = ttk.Entry(picker_frame, width=40)
        self.project_entry.pack(side="left", fill=tk.X, expand=True, padx=(0, 10))
        self.browse_button = ttk.Button(picker_frame, text="Browse", command=self.select_folder)
        self.browse_button.pack(side="left")

        # Treeview frame: fills remaining vertical space.
        tree_frame = ttk.Frame(main_frame)
        tree_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        # Update columns: now includes Install Type.
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

        # Enable inline renaming and drag-and-drop support.
        self.tree.bind("<F2>", self.inline_rename)
        self.enable_drag_drop()

        # Disable resizing for fixed columns (Desc? and Img?).
        def disable_resize_for_fixed_columns(event):
            # Check if the click is on a column separator.
            if self.tree.identify_region(event.x, event.y) == "separator":
                col = self.tree.identify_column(event.x)
                # If either side of the separator is a fixed column,
                # block resizing.
                if col in ("#1", "#2", "#3", "#4"):
                    # Also check a few pixels to the left.
                    left_col = self.tree.identify_column(event.x - 5)
                    if left_col in ("#1", "#2", "#3", "#4"):
                        return "break"

        self.tree.bind('<Button-1>', disable_resize_for_fixed_columns)

        def disable_cursor_on_fixed(event):
            if self.tree.identify_region(event.x, event.y) == "separator":
                col = self.tree.identify_column(event.x)
                if col in ("#1", "#2", "#3", "#4"):
                    left_col = self.tree.identify_column(event.x - 5)
                    if left_col in ("#1", "#2", "#3", "#4"):
                        return "break"
        self.tree.bind('<Motion>', disable_cursor_on_fixed)

    def select_folder(self):
        folder = filedialog.askdirectory()
        if folder:
            self.project_entry.delete(0, tk.END)
            self.project_entry.insert(0, folder)

    def load_recent_project(self, event):
        selected_index = self.recent_projects.curselection()
        if selected_index:
            selected_path = self.recent_projects.get(selected_index)
            self.project_entry.delete(0, tk.END)
            self.project_entry.insert(0, selected_path)

    def on_tree_select(self, event):
        selected = self.tree.selection()
        self.controller.enable_details_tab(enable=bool(selected))

    def inline_rename(self, event):
        selected_item = self.tree.selection()
        if not selected_item:
            return
        item_id = selected_item[0]
        item_text = self.tree.item(item_id, "text")
        entry = ttk.Entry(self.tree)
        entry.insert(0, item_text)
        entry.select_range(0, tk.END)
        entry.focus()

        def save_new_name(event=None):
            new_name = entry.get().strip()
            if new_name:
                self.tree.item(item_id, text=new_name)
            entry.destroy()

        entry.bind("<Return>", save_new_name)
        entry.bind("<FocusOut>", save_new_name)
        bbox = self.tree.bbox(item_id)
        if bbox:
            x, y, width, _ = bbox
            self.tree.place(x=x, y=y, width=width)

    def enable_drag_drop(self):
        self.tree.bind("<B1-Motion>", self.drag_item)
        self.tree.bind("<ButtonRelease-1>", self.drop_item)
        self.dragged_item = None

    def drag_item(self, event):
        item = self.tree.identify_row(event.y)
        if item:
            self.dragged_item = item

    def drop_item(self, event):
        if not self.dragged_item:
            return
        target_item = self.tree.identify_row(event.y)
        if target_item and self.dragged_item != target_item:
            parent = self.tree.parent(target_item)
            index = self.tree.index(target_item)
            self.tree.move(self.dragged_item, parent, index)
        self.dragged_item = None



class DetailsTab(BaseTab):
    """Details tab for editing plugin information."""
    def __init__(self, parent, controller, *args, **kwargs):
        super().__init__(parent, controller, *args, **kwargs)
        self.create_widgets()

    def create_widgets(self):
        paned = ttk.PanedWindow(self, orient=tk.HORIZONTAL)
        paned.pack(fill=tk.BOTH, expand=True)

        # Left Panel - Image Selection
        left_frame = ttk.Frame(paned, width=250)
        paned.add(left_frame, weight=1)
        ttk.Label(left_frame, text="Plugin Image:").pack(anchor="w", padx=5, pady=5)
        self.image_preview = ttk.Label(left_frame, text="No Image Selected", relief=tk.SUNKEN)
        self.image_preview.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.image_button = ttk.Button(left_frame, text="Select Image", command=self.select_image)
        self.image_button.pack(pady=5, padx=5)

        # Right Panel - Description Editor
        right_frame = ttk.Frame(paned)
        paned.add(right_frame, weight=3)
        ttk.Label(right_frame, text="Description:").pack(anchor="w", padx=5, pady=5)
        self.description_text = tk.Text(right_frame, height=10, wrap=tk.WORD)
        self.description_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

    def select_image(self):
        file_path = filedialog.askopenfilename(
            # filetypes=[("Image Files", "*.png;*.jpg;*.jpeg;*.bmp")]
        )
        if file_path:
            self.image_preview.config(text=file_path.split("/")[-1])


class XMLTab(BaseTab):
    """XML Preview and Export tab."""
    def __init__(self, parent, controller, *args, **kwargs):
        super().__init__(parent, controller, *args, **kwargs)
        self.create_widgets()

    def create_widgets(self):
        ttk.Label(self, text="Generated FOMOD XML:").pack(anchor="w", padx=5, pady=5)
        self.xml_preview = tk.Text(self, wrap=tk.WORD, height=20)
        self.xml_preview.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.generate_button = ttk.Button(self, text="Generate XML", command=self.start_generate_xml)
        self.generate_button.pack(pady=5, padx=5)

    def start_generate_xml(self):
        threading.Thread(target=self.generate_xml, daemon=True).start()

    def generate_xml(self):
        self.xml_preview.delete("1.0", tk.END)
        self.xml_preview.insert("1.0", "<config>\n  <!-- XML Content Here -->\n</config>")


class SettingsTab(BaseTab):
    """Settings tab for theme selection and customization."""
    def __init__(self, parent, controller, *args, **kwargs):
        super().__init__(parent, controller, *args, **kwargs)
        self.create_widgets()

    def create_widgets(self):
        ttk.Label(self, text="Theme Selection:").pack(anchor="w", padx=5, pady=5)
        self.theme_var = tk.StringVar(value="Default")
        self.theme_menu = ttk.Combobox(
            self, textvariable=self.theme_var,
            values=["Default", "Dark", "Light", "Custom"]
        )
        self.theme_menu.pack(padx=5, pady=5)
        ttk.Button(self, text="Apply Theme", command=self.apply_theme).pack(pady=10)

    def apply_theme(self):
        theme = self.theme_var.get()
        print(f"Applying theme: {theme}")


class DocumentationTab(BaseTab):
    """Documentation tab for in-app help."""
    def __init__(self, parent, controller, *args, **kwargs):
        super().__init__(parent, controller, *args, **kwargs)
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


class LogsTab(BaseTab):
    """Logs tab to display event logs."""
    def __init__(self, parent, controller, *args, **kwargs):
        super().__init__(parent, controller, *args, **kwargs)
        self.create_widgets()

    def create_widgets(self):
        ttk.Label(self, text="Event Logs:").pack(anchor="w", padx=5, pady=5)
        self.log_text = tk.Text(self, wrap=tk.WORD, height=10, state="disabled")
        self.log_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)


class PhomodUI(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("PHOMOD - Mod Organizer")
        self.geometry("1000x618")
        self.minsize(width=1000, height=550)

        # Create the main notebook
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill=tk.BOTH, expand=True, pady=(5,0))

        # Create tabs as before...
        self.tab_config = {
            "project": {"default": "📦", "active": "🚚", "label": "Project", "class": ProjectTab},
            "details": {"default": "🖌️", "active": "🎨", "label": "Details", "class": DetailsTab},
            "xml": {"default": "🍳", "active": "🍽️", "label": "XML Preview", "class": XMLTab},
            "settings": {"default": "⚙️", "active": "🔧", "label": "Settings", "class": SettingsTab},
            "logs": {"default": "🌲", "active": "🪵", "label": "Logs", "class": LogsTab},
            "docs": {"default": "📔", "active": "📖", "label": "Documentation", "class": DocumentationTab},
        }
        self.tabs = {}
        self.create_tabs()
        self.notebook.bind("<<NotebookTabChanged>>", self.toggle_tab_emoji)

        # Create the status bar (the "help" field at the bottom)
        self.status_var = tk.StringVar(value="Ready")
        self.status_bar = ttk.Label(self, textvariable=self.status_var, relief=tk.SUNKEN, anchor="w")
        self.status_bar.pack(side="bottom", fill="x", padx=5, pady=5)

    def create_tabs(self):
        for key, config in self.tab_config.items():
            tab_frame = config["class"](self.notebook, controller=self)
            self.notebook.add(tab_frame, text=f"{config['default']} {config['label']}")
            self.tabs[key] = tab_frame

    def toggle_tab_emoji(self, event):
        current_tab_id = self.notebook.index(self.notebook.select())
        current_text = self.notebook.tab(current_tab_id, "text")
        for key, config in self.tab_config.items():
            if config["label"] in current_text:
                new_text = f"{config['active']} {config['label']}"
                break
        else:
            return
        for tab_id in range(self.notebook.index("end")):
            tab_text = self.notebook.tab(tab_id, "text")
            for key, config in self.tab_config.items():
                if config["label"] in tab_text:
                    self.notebook.tab(tab_id, text=f"{config['default']} {config['label']}")
        self.notebook.tab(current_tab_id, text=new_text)

    def enable_details_tab(self, enable=True):
        details_index = None
        for i in range(self.notebook.index("end")):
            tab_text = self.notebook.tab(i, "text")
            if self.tab_config["details"]["label"] in tab_text:
                details_index = i
                break
        if details_index is not None:
            state = "normal" if enable else "disabled"
            self.notebook.tab(details_index, state=state)

    def update_status(self, message):
        """Update the text displayed in the status bar."""
        self.status_var.set(message)


if __name__ == "__main__":
    app = PhomodUI()
    app.mainloop()
