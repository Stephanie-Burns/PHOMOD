
import logging
import threading
import tkinter as tk

from phomod_context_menu import PHOMODContextMenu
from phomod_widgets import PHOMODFrame, PHOMODLabel, PHOMODTextArea, PHOMODButton

app_logger = logging.getLogger('FOMODLogger')


class XMLTab(PHOMODFrame):
    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        app_logger.info("Initializing XMLTab")
        self.create_widgets()

    def create_widgets(self):
        PHOMODLabel(self, text="Generated FOMOD XML:").pack(anchor="w", padx=5, pady=5)

        self.xml_preview = PHOMODTextArea(self, context_menu=PHOMODContextMenu(self), wrap=tk.WORD, height=20)
        self.xml_preview.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        self.generate_button = PHOMODButton(self, text="Generate XML", command=self.start_generate_xml)
        self.generate_button.pack(pady=5, padx=5)

        app_logger.info("XMLTab widgets created")

    def start_generate_xml(self):
        app_logger.info("Starting XML generation")
        threading.Thread(target=self.generate_xml, daemon=True).start()

    def generate_xml(self):
        self.xml_preview.delete("1.0", tk.END)
        self.xml_preview.insert("1.0", "<config>\n  <!-- XML Content Here -->\n</config>")
        app_logger.info("XML generated")
