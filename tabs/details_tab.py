
import logging
import os
import threading
import random
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, font
import tkinter as tk
from ttkthemes import ThemedTk

#
# def create_widgets_in_inner(self):
#     # ==== Theme Selection Section
#     theme_frame = ttk.Labelframe(self.inner_frame, text="Theme Selection")
#     theme_frame.pack(fill=tk.X, padx=5, pady=5, expand=True)
#
#     self.theme_var = tk.StringVar(value="Default")
#     self.theme_selector_menu = PHOMODComboBox(
#         theme_frame,
#         controller=self.controller,
#         textvariable=self.theme_var,
#         values=self.controller.theme_manager.get_theme_options(),
#         label_text="Select Theme:",
#         help_text="Select a theme. 'Default' and 'Random' are at the top."
#     )
#     self.theme_selector_menu.pack(fill=tk.X, padx=5, pady=5)
#     self.theme_selector_menu.bind("<<ComboboxSelected>>", self.apply_theme)
#
#     self.current_theme_label = PHOMODLabel(
#         theme_frame,
#         controller=self.controller,
#         text=f"Current Theme: {self.controller.theme_manager.get_theme()}",
#         help_text="Displays the currently active theme.",
#         font=self.italic_font
#     )
#     self.current_theme_label.pack(pady=5)
#
#     # self.bind_help_message(self.theme_menu, "Select a theme. 'Default' and 'Random' are at the top.")
#     # self.bind_help_message(self.current_theme_label, "Displays the currently active theme.")


import tkinter as tk
from tkinter import ttk

class PHOMODComboBox(ttk.Combobox):
    def __init__(self, parent, values, help_text=None, *args, **kwargs):
        """
        Custom ComboBox with optional help text and mouse scroll prevention.

        :param parent: Parent Tkinter widget.
        :param values: List of values for the ComboBox.
        :param help_text: Optional help text to display on hover.
        """
        super().__init__(parent, values=values, *args, **kwargs)

        # Prevent mouse scroll from changing values
        self.bind("<MouseWheel>", self._disable_mouse_wheel)  # Windows/macOS
        self.bind("<Button-4>", self._disable_mouse_wheel)    # Linux (scroll up)
        self.bind("<Button-5>", self._disable_mouse_wheel)    # Linux (scroll down)

        # Automatically fetch help_manager from the controller if available
        self._bind_help_text(parent, help_text)

    def _disable_mouse_wheel(self, event):
        """Prevents mouse scroll from changing the combobox value."""
        return "break"  # Stops the event from propagating

    def _bind_help_text(self, parent, help_text):
        """Automatically binds help text if the parent has a help manager."""
        if help_text and hasattr(parent, "controller") and hasattr(parent.controller, "help_manager"):
            parent.controller.help_manager.bind_help(self, help_text)


class PHOMODLabel(ttk.Label):
    def __init__(self, parent, text, help_text=None, *args, **kwargs):
        """
        Custom Label with optional help text binding.

        :param parent: Parent Tkinter widget.
        :param text: The label text.
        :param help_text: Optional help text to display on hover.
        """
        super().__init__(parent, text=text, *args, **kwargs)

        # Automatically fetch help_manager from the controller if available
        self._bind_help_text(parent, help_text)

    def _bind_help_text(self, parent, help_text):
        """Automatically binds help text if the parent has a help manager."""
        if help_text and hasattr(parent, "controller") and hasattr(parent.controller, "help_manager"):
            parent.controller.help_manager.bind_help(self, help_text)

# Example usage
if __name__ == "__main__":
    root = tk.Tk()
    root.geometry("300x200")

    values = ["Option 1", "Option 2", "Option 3"]

    combobox = PHOMODComboBox(root, values=values, state="readonly")
    combobox.pack(pady=20)

    root.mainloop()
