from tkinter import ttk
import tkinter as tk
import logging

from phomod_mixins import PHOMODHelpTextMixin, PHOMODContextMenuMixin

app_logger = logging.getLogger('FOMODLogger')


class PHOMODLabel(ttk.Label, PHOMODHelpTextMixin):
    def __init__(self, parent, text, help_text=None, **kwargs):
        super().__init__(parent, text=text, **kwargs)
        self._bind_help_text(parent, help_text)


class PHOMODComboBox(ttk.Combobox, PHOMODHelpTextMixin):
    def __init__(self, parent, values, help_text=None, **kwargs):
        super().__init__(parent, values=values, **kwargs)

        # Prevent mouse scroll from changing values
        self.bind("<MouseWheel>", self._disable_mouse_wheel)
        self.bind("<Button-4>", self._disable_mouse_wheel)
        self.bind("<Button-5>", self._disable_mouse_wheel)

        self._bind_help_text(parent, help_text)

    def _disable_mouse_wheel(self, event):
        """Prevents mouse scroll from changing the combobox value."""
        return "break"


class PHOMODButton(ttk.Button, PHOMODHelpTextMixin):
    def __init__(self, parent, text, command=None, help_text=None, padding=(10, 6), **kwargs):
        kwargs.setdefault("padding", padding)  # Set default if not provided
        super().__init__(parent, text=text, command=command, **kwargs)
        self._bind_help_text(parent, help_text)


class PHOMODCheckbutton(ttk.Checkbutton, PHOMODHelpTextMixin):
    def __init__(self, parent, text, variable, help_text=None, **kwargs):
        super().__init__(parent, text=text, variable=variable, **kwargs)
        self._bind_help_text(parent, help_text)


class PHOMODEntry(ttk.Entry, PHOMODHelpTextMixin, PHOMODContextMenuMixin):
    """Entry widget with both help text and context menu integration."""

    def __init__(self, parent, textvariable=None, help_text=None, context_menu=None, **kwargs):
        super().__init__(parent, textvariable=textvariable, **kwargs)
        self._bind_help_text(parent, help_text)
        self._bind_context_menu(context_menu)


class PHOMODTextArea(tk.Text, PHOMODHelpTextMixin, PHOMODContextMenuMixin):
    """Multi-line text widget with both help text and context menu integration."""

    def __init__(self, parent, help_text=None, context_menu=None, **kwargs):
        super().__init__(parent, **kwargs)
        self._bind_help_text(parent, help_text)
        self._bind_context_menu(context_menu)


class PHOMODFrame(ttk.Frame, PHOMODHelpTextMixin):
    def __init__(self, parent, controller=None, help_text=None, **kwargs):
        super().__init__(parent, **kwargs)
        self.controller = controller
        self._bind_help_text(parent, help_text)


class PHOMODLabelFrame(ttk.Labelframe, PHOMODHelpTextMixin):
    def __init__(self, parent, controller=None, text="", help_text=None, **kwargs):
        super().__init__(parent, text=text, **kwargs)
        self.controller = controller
        self._bind_help_text(parent, help_text)
