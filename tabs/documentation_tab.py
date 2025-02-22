
import logging
import tkinter as tk
from tkinter import ttk

from phomod_widgets import PHOMODFrame

app_logger = logging.getLogger('FOMODLogger')


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
