
import logging
import threading
import tkinter as tk

from phomod_widgets import PHOMODFrame, PHOMODLabel, PHOMODTextArea, PHOMODButton, PHOMODSyntaxTextArea

app_logger = logging.getLogger('PHOMODLogger')


class XMLEditorView(PHOMODFrame):
    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        app_logger.info(f"🚦 Initializing {self.__class__.__name__}")
        self.create_widgets()

    def create_widgets(self):
        PHOMODLabel(self, text="Generated FOMOD XML:").pack(anchor="w", padx=5, pady=5)

        text_frame = PHOMODFrame(self)
        text_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        self.xml_preview = PHOMODSyntaxTextArea(text_frame, height=20, attach_y=True)
        self.xml_preview.pack(fill=tk.BOTH, expand=True)

        self.generate_button = PHOMODButton(self, text="Generate XML", command=self.start_generate_xml)
        self.generate_button.pack(pady=5, padx=5)

        app_logger.info("XMLTab widgets created")

    def start_generate_xml(self):
        app_logger.info("Starting XML generation")
        threading.Thread(target=self.generate_xml, daemon=True).start()

    def generate_xml(self):
        sample_xml = """<config>
    <mod name="Example">
        <author>John Doe</author>
        <version>1.0</version>
    </mod>
</config>"""
        self.xml_preview.delete("1.0", tk.END)
        self.xml_preview.insert("1.0", sample_xml)
        self.xml_preview._highlight_syntax()  # Manually trigger highlighting
        app_logger.info("XML generated")
