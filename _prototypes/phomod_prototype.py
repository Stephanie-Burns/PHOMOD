import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os
import xml.etree.ElementTree as ET
from xml.dom.minidom import parseString
import re
from PIL import Image, ImageTk  # Requires Pillow

# Attempt to import tkinterdnd2 for drag-and-drop (optional)
try:
    from tkinterdnd2 import DND_FILES, TkinterDnD

    dnd_available = True
except ImportError:
    dnd_available = False


def clean_name(name):
    """Removes leading numbers and trims spaces from folder names."""
    return re.sub(r"^\d+\s*", "", name)


class EditPanel(tk.Toplevel):
    def __init__(self, master, item_id, tree_item_data, root_dir, current_desc, current_image, callback_save):
        super().__init__(master)
        self.item_id = item_id
        self.tree_item_data = tree_item_data  # Not used further here but could be handy
        self.root_dir = root_dir
        self.callback_save = callback_save
        self.current_desc = current_desc
        self.current_image = current_image
        self.title("Edit Plugin / Mod Root")
        self.geometry("600x300")

        # Create two main panes: left for image and right for description.
        main_frame = tk.Frame(self)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        left_frame = tk.Frame(main_frame)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))
        right_frame = tk.Frame(main_frame)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(5, 0))

        # LEFT PANE: Image preview area.
        self.image_label = tk.Label(left_frame, text="Click or drag an image here", relief=tk.SUNKEN, bg="white")
        self.image_label.pack(fill=tk.BOTH, expand=True)
        self.image_label.bind("<Button-1>", self.select_image)
        if dnd_available:
            # Enable drag-and-drop if available
            self.image_label.drop_target_register(DND_FILES)
            self.image_label.dnd_bind('<<Drop>>', self.handle_drop)

        # RIGHT PANE: Text area for description.
        self.text_area = tk.Text(right_frame, wrap=tk.WORD)
        self.text_area.pack(fill=tk.BOTH, expand=True)
        if self.current_desc:
            self.text_area.insert(tk.END, self.current_desc)

        # Bottom: Save and Cancel buttons.
        button_frame = tk.Frame(self)
        button_frame.pack(fill=tk.X, padx=10, pady=10)
        cancel_button = tk.Button(button_frame, text="Cancel", command=self.destroy)
        cancel_button.pack(side=tk.RIGHT, padx=5)
        save_button = tk.Button(button_frame, text="Save", command=self.save)
        save_button.pack(side=tk.RIGHT, padx=5)

        # Image state
        self.image_path = self.current_image
        self.tk_image = None
        if self.image_path:
            self.load_and_display_image()

    def select_image(self, event=None):
        file_path = filedialog.askopenfilename(
            initialdir=self.root_dir,
            title="Select image",
            filetypes=[("Image files", "*.png;*.jpg;*.jpeg;*.gif;*.bmp")]
        )
        if file_path:
            # Ensure the chosen file is inside the root directory.
            if not os.path.commonpath([self.root_dir, file_path]) == self.root_dir:
                messagebox.showerror("Error", "Image must be inside the root directory!")
                return
            rel_path = os.path.relpath(file_path, self.root_dir)
            self.image_path = rel_path
            self.load_and_display_image()

    def handle_drop(self, event):
        # event.data may include one or more file paths.
        files = self.tk.splitlist(event.data)
        if files:
            file_path = files[0]
            if not os.path.commonpath([self.root_dir, file_path]) == self.root_dir:
                messagebox.showerror("Error", "Image must be inside the root directory!")
                return
            rel_path = os.path.relpath(file_path, self.root_dir)
            self.image_path = rel_path
            self.load_and_display_image()

    def load_and_display_image(self):
        try:
            full_path = os.path.join(self.root_dir, self.image_path) if not os.path.isabs(
                self.image_path) else self.image_path
            img = Image.open(full_path)
            # Create a thumbnail (max 200x200) for preview; note: this does not affect the source image.
            img.thumbnail((200, 200))
            self.tk_image = ImageTk.PhotoImage(img)
            self.image_label.config(image=self.tk_image, text="")
        except Exception as e:
            print("Error loading image:", e)
            self.image_label.config(text="Error loading image")

    def save(self):
        new_desc = self.text_area.get("1.0", tk.END).strip()
        # Pass updated description and image path to the callback.
        self.callback_save(self.item_id, new_desc, self.image_path)
        self.destroy()


class FomodTreeApp:
    def __init__(self, root):
        self.root = root
        self.root.title("FOMOD Tree View")

        # Frame for directory selection.
        self.frame = tk.Frame(root)
        self.frame.pack(fill=tk.X, padx=10, pady=5)

        self.dir_label = tk.Label(self.frame, text="Select a directory:")
        self.dir_label.pack(side=tk.LEFT, padx=5)
        self.dir_button = tk.Button(self.frame, text="Browse", command=self.select_directory)
        self.dir_button.pack(side=tk.LEFT, padx=5)

        # Button to generate XML.
        self.xml_button = tk.Button(self.frame, text="Generate FOMOD XML", command=self.generate_fomod_xml)
        self.xml_button.pack(side=tk.LEFT, padx=5)

        # Button to edit descriptions and images.
        self.edit_button = tk.Button(self.frame, text="Edit Selected", command=self.open_edit_panel, state=tk.DISABLED)
        self.edit_button.pack(side=tk.LEFT, padx=5)

        # Create treeview with four columns.
        self.tree = ttk.Treeview(root, columns=("Category", "FOMOD Name", "Desc?", "Img?"), show="tree headings")
        self.tree.heading("#0", text="Directory Structure")
        self.tree.heading("Category", text="Category", anchor=tk.W)
        self.tree.heading("FOMOD Name", text="FOMOD Name", anchor=tk.W)
        self.tree.heading("Desc?", text="✔", anchor=tk.CENTER)
        self.tree.heading("Img?", text="🖼", anchor=tk.CENTER)
        self.tree.column("Category", width=120)
        self.tree.column("Desc?", width=40, anchor=tk.CENTER, stretch=False)
        self.tree.column("Img?", width=40, anchor=tk.CENTER, stretch=False)
        self.tree.pack(expand=True, fill=tk.BOTH, padx=10, pady=10)
        self.tree.bind("<<TreeviewSelect>>", self.on_tree_select)

        # Legend for categories.
        self.legend_frame = tk.Frame(root)
        self.legend_frame.pack(fill=tk.X, padx=10, pady=5)
        self.add_legend("📂 Root (Step)", "white")
        self.add_legend("📁 Group", "lightblue")
        # Flipped colors: Plugins now yellow and Files green.
        self.add_legend("📜 Plugin", "lightyellow")
        self.add_legend("📄 Files", "lightgreen")
        self.add_legend("🚫 Ignored", "lightgray")

        # Data storage for description and image.
        self.structure = {}
        self.description_data = {}  # Keyed by tree item id.
        self.image_data = {}  # Keyed by tree item id.

        # Your desired default directory.
        self.default_dir = "/home/dougr/Games/prefixes/morrowind_gog/pfx/drive_c/users/steamuser/My Documents/Dwemer Interface Suite/thetsing_delete_later/100 UI Enhancements"
        self.select_directory(initial=True)

    def add_legend(self, text, color):
        label = tk.Label(self.legend_frame, text=text, bg=color, fg="black", padx=5, pady=2)
        label.pack(side=tk.LEFT, padx=5)

    def select_directory(self, initial=False):
        directory = self.default_dir if initial else filedialog.askdirectory()
        if directory:
            self.tree.delete(*self.tree.get_children())  # Clear old tree.
            self.structure.clear()
            root_name = clean_name(os.path.basename(directory))
            # For the mod root (Step), status is initially missing (❌).
            root_item = self.tree.insert("", "end", text=f"📂 {root_name}", values=("Step", root_name, "❌", "❌"),
                                         tags=("root",))
            self.structure = {"name": root_name, "type": "root", "children": []}
            self.walk_directory(directory, root_item, self.structure)

            self.tree.tag_configure("root", background="white")
            self.tree.tag_configure("group", background="lightblue")
            self.tree.tag_configure("plugin", background="lightyellow")
            self.tree.tag_configure("files", background="lightgreen")
            self.tree.tag_configure("ignored", background="lightgray")

    def walk_directory(self, path, parent, struct):
        folder_name = os.path.basename(path)
        # Special handling for a folder named "fomod".
        if folder_name.lower() == "fomod":
            node = self.tree.insert(parent, "end", text=f"🚫 {folder_name}", values=("Ignored", "", "", ""),
                                    tags=("ignored",))
            struct["children"].append({"name": folder_name, "type": "ignored", "children": []})
            for item in sorted(os.listdir(path)):
                if item.lower() == "fomod":
                    continue
                full_path = os.path.join(path, item)
                self.tree.insert(node, "end", text=f"🚫 {item}", values=("Ignored", "", "", ""), tags=("ignored",))
                struct["children"][-1]["children"].append({"name": item, "type": "ignored"})
            return  # Skip further processing.

        # Process subdirectories.
        for item in sorted(os.listdir(path)):
            full_path = os.path.join(path, item)
            if os.path.isdir(full_path):
                if struct.get("type") in ("root", "group"):
                    if item.lower() == "data files":
                        # Treat "data files" as a plugin.
                        plugin_name = clean_name(struct["name"])
                        node = self.tree.insert(parent, "end", text=f"📜 {item}",
                                                values=("Plugin", plugin_name, "❌", "❌"), tags=("plugin",))
                        sub_struct = {"name": item, "type": "plugin", "plugin_name": plugin_name, "children": []}
                        self.walk_directory(full_path, node, sub_struct)
                        struct.setdefault("children", []).append(sub_struct)
                    else:
                        group_name = clean_name(item)
                        node = self.tree.insert(parent, "end", text=f"📁 {item}", values=("Group", group_name, "", ""),
                                                tags=("group",))
                        sub_struct = {"name": item, "type": "group", "children": []}
                        self.walk_directory(full_path, node, sub_struct)
                        struct.setdefault("children", []).append(sub_struct)
                elif struct.get("type") == "plugin":
                    # For files, leave the FOMOD Name column blank.
                    node = self.tree.insert(parent, "end", text=f"📄 {item}", values=("Files", "", "", ""),
                                            tags=("files",))
                    sub_struct = {"name": item, "type": "files"}
                    self.walk_directory(full_path, node, sub_struct)
                    sub_struct.setdefault("children", [])
                    struct.setdefault("children", []).append(sub_struct)

    def on_tree_select(self, event):
        selected = self.tree.selection()
        if selected:
            category = self.tree.item(selected[0], "values")[0]
            # Enable editing only for mod root ("Step") and plugins.
            if category in ("Step", "Plugin"):
                self.edit_button.config(state=tk.NORMAL)
            else:
                self.edit_button.config(state=tk.DISABLED)

    def open_edit_panel(self):
        selected = self.tree.selection()
        if not selected:
            return
        item_id = selected[0]
        current_desc = self.description_data.get(item_id, "")
        current_img = self.image_data.get(item_id, "")
        # Open the edit panel. The root directory is passed so that file selections remain relative.
        EditPanel(self.root, item_id, self.tree.item(item_id), self.default_dir, current_desc, current_img,
                  self.update_plugin_data)

    def update_plugin_data(self, item_id, desc, img_path):
        """Callback from the edit panel to update stored description and image data."""
        self.description_data[item_id] = desc
        self.image_data[item_id] = img_path
        # Update the tree view status symbols.
        values = list(self.tree.item(item_id, "values"))
        values[2] = "✅" if desc else "❌"
        values[3] = "✅" if img_path else "❌"
        self.tree.item(item_id, values=tuple(values))

    def generate_fomod_xml(self):
        fomod_dir = "fomod"
        os.makedirs(fomod_dir, exist_ok=True)
        info_xml_path = os.path.join(fomod_dir, "info.xml")
        if not os.path.exists(info_xml_path):
            with open(info_xml_path, "w", encoding="utf-8") as f:
                f.write("<fomod/>")

        root_name = clean_name(self.structure.get("name", "Unnamed Mod"))
        fomod_root = ET.Element("config", {
            "xmlns:xsi": "http://www.w3.org/2001/XMLSchema-instance",
            "xsi:noNamespaceSchemaLocation": "http://qconsulting.ca/fo3/ModConfig5.0.xsd"
        })
        module_name = ET.SubElement(fomod_root, "moduleName")
        module_name.text = root_name
        install_steps = ET.SubElement(fomod_root, "installSteps", order="Explicit")
        root_step = ET.SubElement(install_steps, "installStep", name=root_name)
        file_groups = ET.SubElement(root_step, "optionalFileGroups", order="Explicit")

        for step in self.structure.get("children", []):
            if step["type"] == "group" and step["name"].lower() != "fomod":
                step_name = clean_name(step["name"])
                group_element = ET.SubElement(file_groups, "group", name=step_name, type="SelectAny")
                plugins = ET.SubElement(group_element, "plugins", order="Explicit")
                for child in step.get("children", []):
                    if child["type"] == "plugin":
                        plugin_name = child.get("plugin_name", step_name)
                        plugin_element = ET.SubElement(plugins, "plugin", name=plugin_name)
                        # Use the edited description if available.
                        description = ET.SubElement(plugin_element, "description")
                        description.text = self.description_data.get(child.get("tree_id", ""),
                                                                     "Auto-generated description.")
                        files = ET.SubElement(plugin_element, "files")
                        source_path = f"{step['name']}\\{child['name']}".replace("/", "\\")
                        ET.SubElement(files, "folder", source=source_path, destination="\\", priority="0")
                        for sub in child.get("children", []):
                            if sub["type"] == "files":
                                sub_source_path = f"{child['name']}\\{sub['name']}".replace("/", "\\")
                                ET.SubElement(files, "folder", source=sub_source_path, destination="\\", priority="0")
                        type_descriptor = ET.SubElement(plugin_element, "typeDescriptor")
                        ET.SubElement(type_descriptor, "type", name="Optional")

        xml_str = ET.tostring(fomod_root, encoding="utf-8")
        pretty_xml = parseString(xml_str).toprettyxml(indent="  ")
        with open(os.path.join(fomod_dir, "ModuleConfig.xml"), "w", encoding="utf-8") as f:
            f.write(pretty_xml)

        print(f"✅ FOMOD XML saved successfully in '{fomod_dir}/ModuleConfig.xml'")
        print("✅ Info.xml created if missing.")


if __name__ == "__main__":
    # If drag-and-drop support is desired and tkinterdnd2 is available,
    # you might replace tk.Tk() with TkinterDnD.Tk() below.
    root = tk.Tk()
    app = FomodTreeApp(root)
    root.mainloop()
