
import tkinter as tk
from tkinter import ttk, filedialog
import logging

from phomod_widgets import (
    PHOMODFrame, PHOMODLabel, PHOMODTextArea, PHOMODLabelFrame,
    PHOMODEntry, PHOMODButton, PHOMODListbox, PHOMODTreeview
)
from _prototypes.image_manipulation_prototype import ImageViewerWidget

app_log = logging.getLogger('FOMODLogger')


class PluginDetailsSidebar(PHOMODFrame):
    """Sidebar displaying plugin image and description."""

    raise NotImplemented
