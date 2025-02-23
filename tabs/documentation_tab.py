import logging
import tkinter as tk
from tkinter import ttk

from phomod_widgets import PHOMODFrame, PHOMODTextArea, PHOMODLabel, PHOMODComboBox

app_logger = logging.getLogger('FOMODLogger')


class DocumentationTab(PHOMODFrame):
    """Allows users to browse various PHOMOD documents like README, API Docs, and other guides."""

    DOCUMENTS = {
        "README": "Welcome to PHOMOD!\n\nThis tool helps you generate and package FOMOD installers for your mods.\n\n"
                  "For more info, visit the PHOMOD GitHub repository.",
        "API Documentation": "PHOMOD API Overview\n\nHere you will find a complete guide to the available API endpoints...",
        "Modding Guidelines": "Modding Guidelines\n\nFollow these standards to ensure compatibility with other mods..."
    }

    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        app_logger.info("Initializing DocumentationTab")
        self.create_widgets()

    def create_widgets(self):
        """Creates the UI components for the documentation viewer."""
        PHOMODLabel(self, text="PHOMOD Documentation", font=("Arial", 14, "bold")).pack(pady=10)

        # 📜 Dropdown for selecting document
        selection_frame = PHOMODFrame(self)
        selection_frame.pack(fill=tk.X, padx=10, pady=5)

        PHOMODLabel(selection_frame, text="Select Document:").pack(side="left", padx=5)

        self.doc_selector = PHOMODComboBox(
            selection_frame,
            values=list(self.DOCUMENTS.keys()),
            state="readonly"
        )
        self.doc_selector.pack(side="left", fill=tk.X, expand=True, padx=5)
        self.doc_selector.bind("<<ComboboxSelected>>", self.load_selected_document)

        # 📜 Subframe to contain the text area + scrollbar
        text_container = PHOMODFrame(self)
        text_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        self.doc_text = PHOMODTextArea(text_container, wrap=tk.WORD, height=15, attach_y=True)
        self.doc_text.pack(side="left", fill=tk.BOTH, expand=True)

        # Load default document
        self.load_selected_document()

    def load_selected_document(self, event=None):
        """Loads the selected document into the text area."""
        selected_doc = self.doc_selector.get() or "README"
        content = self.DOCUMENTS.get(selected_doc, "No content available.")

        self.doc_text.configure(state="normal")
        self.doc_text.delete("1.0", tk.END)
        self.doc_text.insert("1.0", content)
        self.doc_text.configure(state="disabled")

        app_logger.info(f"Loaded document: {selected_doc}")
