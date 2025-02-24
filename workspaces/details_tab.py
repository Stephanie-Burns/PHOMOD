
import logging
import tkinter as tk
from tkinter import ttk

from _prototypes.image_manipulation_prototype import ImageViewerWidget
from phomod_widgets import PHOMODFrame

app_logger = logging.getLogger('FOMODLogger')


class DetailsTab(PHOMODFrame):
    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        app_logger.info("Initializing DetailsTab")
        self.create_widgets()

    def create_widgets(self):
        paned = ttk.PanedWindow(self, orient=tk.HORIZONTAL)
        paned.pack(fill=tk.BOTH, expand=True)
        left_frame = ttk.Frame(paned, width=250)
        paned.add(left_frame, weight=1)
        ttk.Label(left_frame, text="Plugin Image:").pack(anchor="w", padx=5, pady=5)
        self.image_viewer = ImageViewerWidget(left_frame, width=250, height=150)
        self.image_viewer.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        right_frame = ttk.Frame(paned)
        paned.add(right_frame, weight=3)
        ttk.Label(right_frame, text="Description:").pack(anchor="w", padx=5, pady=5)
        self.description_text = tk.Text(right_frame, height=10, wrap=tk.WORD)
        self.description_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        app_logger.info("DetailsTab widgets created")

    def get_image_path(self):
        return self.image_viewer.get_image_path()
