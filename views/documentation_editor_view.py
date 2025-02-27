import logging
import tkinter as tk
from tkinter import filedialog
import webbrowser
import re

from phomod_widgets import PHOMODFrame, PHOMODTextArea, PHOMODLabel, PHOMODComboBox, PHOMODButton, PHOMODCheckbutton

app_logger = logging.getLogger('PHOMODLogger')


class DocumentationEditorView(PHOMODFrame):
    """Allows users to browse various PHOMOD documents like README, API Docs, and other guides."""

    DOCUMENTS = {
        "README": """# Welcome to PHOMOD!

This tool helps you generate and package FOMOD installers for your mods.

## Features
- 📂 **Project Tab**: Select or browse your mod directory.
- 🎨 **Details Panel**: Modify descriptions and images for plugins.
- 📜 **XML Preview**: See and export your generated FOMOD XML.
- ⚙️ **Settings**: Customize themes and preferences.

For more info, visit the [PHOMOD GitHub repository](https://github.com/your_repo).
""",
        "API Documentation": """# PHOMOD API Overview
Here you will find a complete guide to the available API endpoints.

## Endpoints:
- `/load_project` - Loads a project
- `/generate_xml` - Generates XML config

For details, visit our [API Docs](https://api.phomod.com).
""",
        "Modding Guidelines": """# Modding Guidelines
Follow these standards to ensure compatibility with other mods.

## Best Practices:
- Use **consistent folder structure**.
- Avoid **conflicting file names**.
- Test your FOMOD installer before release.

For more details, check the PHOMOD guidelines.
"""
    }

    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        app_logger.info(f"🚦 Initializing {self.__class__.__name__}")
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

        # ✍️ Edit Mode Toggle
        self.edit_var = tk.BooleanVar(value=False)
        self.edit_toggle = PHOMODCheckbutton(
            selection_frame,
            text="Edit Mode",
            variable=self.edit_var,
            command=self.toggle_edit_mode
        )
        self.edit_toggle.pack(side="left", padx=10)

        # 📜 Subframe to contain the text area + scrollbar
        text_container = PHOMODFrame(self)
        text_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        self.doc_text = PHOMODTextArea(text_container, wrap=tk.WORD, height=20, attach_y=True)
        self.doc_text.pack(side="left", fill=tk.BOTH, expand=True)

        # 📥 Export Button
        button_frame = PHOMODFrame(self)
        button_frame.pack(fill=tk.X, padx=10, pady=5)

        PHOMODButton(button_frame, text="Export", command=self.export_document).pack(side="right", padx=5)

        # Load default document
        self.load_selected_document()

    def load_selected_document(self, event=None):
        """Loads the selected document and applies Markdown formatting."""
        selected_doc = self.doc_selector.get() or "README"
        content = self.DOCUMENTS.get(selected_doc, "No content available.")

        self.doc_text.configure(state="normal")
        self.doc_text.delete("1.0", tk.END)

        self._apply_markdown_formatting(content)

        self.doc_text.configure(state="disabled")
        app_logger.info(f"💾 Loaded document: {selected_doc}")

    def _apply_markdown_formatting(self, content):
        """Applies Markdown formatting in the Tkinter Text widget."""
        # Define styling
        self.doc_text.tag_configure("header1", font=("Arial", 14, "bold"))
        self.doc_text.tag_configure("header2", font=("Arial", 12, "bold"))
        self.doc_text.tag_configure("bold", font=("Arial", 10, "bold"))
        self.doc_text.tag_configure("italic", font=("Arial", 10, "italic"))
        self.doc_text.tag_configure("list", lmargin1=20, lmargin2=40)
        self.doc_text.tag_configure("link", foreground="blue", underline=True)
        self.doc_text.tag_configure("code", font=("Courier", 10, "bold"), background="#f5f5f5", foreground="#d63384")
        self.doc_text.tag_configure("codeblock", font=("Courier", 10), background="#282c34", foreground="#abb2bf",
                                    lmargin1=10, lmargin2=20)

        # Regex patterns
        link_pattern = re.compile(r"\[([^\]]+)\]\((https?:\/\/[^\s)]+)\)")
        bold_pattern = re.compile(r"\*\*(.*?)\*\*")
        italic_pattern = re.compile(r"_(.*?)_")
        code_pattern = re.compile(r"`([^`]+)`")
        codeblock_pattern = re.compile(r"```([\s\S]*?)```")

        # Handling code blocks separately
        lines = content.split("\n")
        inside_code_block = False
        for line in lines:
            start_index = self.doc_text.index(tk.END)

            # Code Blocks (Multiline)
            if line.startswith("```") or inside_code_block:
                if inside_code_block:
                    if line.startswith("```"):
                        inside_code_block = False
                    self.doc_text.insert(tk.END, line + "\n", "codeblock")
                else:
                    inside_code_block = True
                continue

            # Headers
            if line.startswith("# "):
                self.doc_text.insert(tk.END, line[2:] + "\n", "header1")
            elif line.startswith("## "):
                self.doc_text.insert(tk.END, line[3:] + "\n", "header2")

            # Lists
            elif line.startswith("- "):
                self.doc_text.insert(tk.END, "• " + line[2:] + "\n", "list")

            else:
                # Apply Markdown formatting
                formatted_line = line
                last_end = 0

                # Apply links
                for match in link_pattern.finditer(line):
                    text, url_pattern = match.groups()
                    self.doc_text.insert(tk.END, formatted_line[last_end:match.start()])
                    start_idx = self.doc_text.index(tk.END)
                    self.doc_text.insert(tk.END, text, "link")
                    self.doc_text.tag_bind("link", "<Enter>", lambda e: self.doc_text.config(cursor="hand2"))
                    self.doc_text.tag_bind("link", "<Leave>", lambda e: self.doc_text.config(cursor=""))
                    self.doc_text.tag_bind("link", "<Button-1>", lambda e, url=url_pattern: webbrowser.open(url))
                    last_end = match.end()

                self.doc_text.insert(tk.END, formatted_line[last_end:] + "\n")

                # Apply bold
                for match in bold_pattern.finditer(formatted_line):
                    self.doc_text.tag_add("bold", f"{start_index}+{match.start()}c", f"{start_index}+{match.end()}c")

                # Apply italics
                for match in italic_pattern.finditer(formatted_line):
                    self.doc_text.tag_add("italic", f"{start_index}+{match.start()}c", f"{start_index}+{match.end()}c")

                # Apply inline code
                for match in code_pattern.finditer(formatted_line):
                    self.doc_text.tag_add("code", f"{start_index}+{match.start()}c", f"{start_index}+{match.end()}c")

    def _open_url(url):
        """Opens a given URL in the default web browser."""
        webbrowser.open(url)

    def toggle_edit_mode(self):
        """Toggles between editable and read-only states."""
        if self.edit_var.get():
            self.doc_text.configure(state="normal")
        else:
            self.doc_text.configure(state="disabled")

    def export_document(self):
        """Exports the current document to a user-selected file."""
        selected_doc = self.doc_selector.get() or "README"
        file_path = filedialog.asksaveasfilename(
            defaultextension=".md",
            filetypes=[("Markdown Files", "*.md"), ("Text Files", "*.txt"), ("All Files", "*.*")]
        )

        if file_path:
            content = self.doc_text.get("1.0", tk.END).strip()
            with open(file_path, "w", encoding="utf-8") as file:
                file.write(content)
            app_logger.info(f"Exported document: {selected_doc} to {file_path}")
