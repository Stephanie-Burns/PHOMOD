
import logging
import re
import tkinter as tk
from tkinter import ttk

from phomod_mixins import PHOMODHelpTextMixin, PHOMODContextMenuMixin, PHOMODScrollRedirectMixin

app_logger = logging.getLogger('PHOMODLogger')


# ----------------------------------------------------------------------------------------------------------------------
#                                                                                              🏗 STRUCTURAL CONTAINERS
# ----------------------------------------------------------------------------------------------------------------------
class PHOMODFrame(ttk.Frame):
    """A basic frame with optional help text integration."""
    def __init__(self, parent, controller=None, **kwargs):
        super().__init__(parent, **kwargs)
        self.controller = controller


class PHOMODLabelFrame(ttk.Labelframe, PHOMODHelpTextMixin):
    """A label frame with optional custom label widget and help text."""
    def __init__(self, parent, controller=None, help_text=None, text="", label_widget=None, **kwargs):
        self.controller = controller
        self._configure_label(kwargs, text, label_widget)
        super().__init__(parent, **kwargs)
        self._bind_help_text(parent, help_text)

    @staticmethod
    def _configure_label(kwargs, text, label_widget):
        """Decide whether to use a label widget or the default text."""
        if label_widget:
            kwargs["labelwidget"] = label_widget
        else:
            kwargs["text"] = text


class PHOMODScrollableFrame(ttk.Frame):
    """A reusable scrollable frame with automatic mousewheel support."""
    def __init__(self, parent, controller=None, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.controller = controller

        self.canvas = tk.Canvas(self, borderwidth=0, highlightthickness=0, bg="white")
        self.scroll_helper = _PHOMODAttachableScrollbar(self.canvas, attach_y=True)  # Handles the scrollbar

        self.canvas.pack(side="left", fill=tk.BOTH, expand=True)

        # Interior Container
        self.inner_frame = ttk.Frame(self.canvas)
        self.inner_window = self.canvas.create_window((0, 0), window=self.inner_frame, anchor="nw")

        # Events
        self.inner_frame.bind("<Configure>", self._on_frame_configure)
        self.canvas.bind("<Configure>", self._on_canvas_configure)

        # Mouse wheel support
        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)
        self.canvas.bind_all("<Button-4>", self._on_mousewheel)  # Linux scroll up
        self.canvas.bind_all("<Button-5>", self._on_mousewheel)  # Linux scroll down

    def _on_frame_configure(self, event=None):
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def _on_canvas_configure(self, event):
        self.canvas.itemconfigure(self.inner_window, width=event.width)

    def _on_mousewheel(self, event):
        """Handles the mouse wheel scrolling."""
        delta = event.delta if event.delta else 120 if event.num == 4 else -120
        norm = -1 if delta < 0 else 1
        app_logger.debug(f"Canvas scrolling: norm delta = {norm}")
        self.canvas.yview_scroll(-norm, "units")
        return "break"


# ----------------------------------------------------------------------------------------------------------------------
#                                                                                                  🖼 BASIC UI ELEMENTS
# ----------------------------------------------------------------------------------------------------------------------
class PHOMODLabel(ttk.Label, PHOMODHelpTextMixin):
    """A basic label with help text integration."""
    def __init__(self, parent, text, help_text=None, **kwargs):
        super().__init__(parent, text=text, **kwargs)
        self._bind_help_text(parent, help_text)


class PHOMODEntry(ttk.Entry, PHOMODHelpTextMixin, PHOMODContextMenuMixin, PHOMODScrollRedirectMixin):
    """An entry widget that redirects mouse scroll events to the parent scrollable frame."""
    def __init__(self, parent, textvariable=None, help_text=None, context_menu=None, **kwargs):
        super().__init__(parent, textvariable=textvariable, **kwargs)
        self._bind_help_text(parent, help_text)
        self._bind_context_menu(context_menu)


class PHOMODTextArea(tk.Text, PHOMODHelpTextMixin, PHOMODContextMenuMixin):
    """A multi-line text widget with help text and context menu integration, now with optional scrollbars."""
    def __init__(self, parent, help_text=None, context_menu=None, attach_x=False, attach_y=True, **kwargs):
        super().__init__(parent, **kwargs)
        self._bind_help_text(parent, help_text)
        self._bind_context_menu(context_menu)
        self.scroll_helper = _PHOMODAttachableScrollbar(self, attach_x=attach_x, attach_y=attach_y)


class PHOMODSyntaxTextArea(PHOMODTextArea):
    """Enhanced Text Area with basic XML syntax highlighting."""

    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.configure(font=("Courier", 12))  # Monospace for better readability
        self._setup_tags()
        self.bind("<KeyRelease>", self._highlight_syntax)  # Highlight on typing

    def _setup_tags(self):
        """Define text color styles for XML syntax."""
        self.tag_configure("tag", foreground="blue")
        self.tag_configure("attribute", foreground="darkred")
        self.tag_configure("value", foreground="green")

    def _highlight_syntax(self, event=None):
        """Apply syntax highlighting dynamically."""
        self.tag_remove("tag", "1.0", "end")
        self.tag_remove("attribute", "1.0", "end")
        self.tag_remove("value", "1.0", "end")

        text = self.get("1.0", "end-1c")  # Get full text

        # XML tag pattern: <tagname> </tagname>
        tag_pattern = re.finditer(r"</?[\w:-]+.*?>", text)
        for match in tag_pattern:
            self.tag_add("tag", f"1.0+{match.start()}c", f"1.0+{match.end()}c")

        # Attribute pattern: key="value"
        attr_pattern = re.finditer(r'(\w+)=', text)
        for match in attr_pattern:
            self.tag_add("attribute", f"1.0+{match.start()}c", f"1.0+{match.end()}c")

        # String values inside quotes: "value"
        value_pattern = re.finditer(r'"[^"]*"', text)
        for match in value_pattern:
            self.tag_add("value", f"1.0+{match.start()}c", f"1.0+{match.end()}c")



# ----------------------------------------------------------------------------------------------------------------------
#                                                                                                🎛 INTERACTIVE WIDGETS
# ----------------------------------------------------------------------------------------------------------------------
class PHOMODButton(ttk.Button, PHOMODHelpTextMixin):
    """A button with customizable padding and help text integration."""
    def __init__(self, parent, text, command=None, help_text=None, padding=(10, 6), **kwargs):
        kwargs.setdefault("padding", padding)  # Set default if not provided
        super().__init__(parent, text=text, command=command, **kwargs)
        self._bind_help_text(parent, help_text)


class PHOMODCheckbutton(ttk.Checkbutton, PHOMODHelpTextMixin):
    """A checkbutton with help text integration."""
    def __init__(self, parent, text, variable, help_text=None, **kwargs):
        super().__init__(parent, text=text, variable=variable, **kwargs)
        self._bind_help_text(parent, help_text)


class PHOMODComboBox(ttk.Combobox, PHOMODHelpTextMixin, PHOMODScrollRedirectMixin):
    """A combobox that redirects mouse scroll events to the parent scrollable frame."""
    def __init__(self, parent, values, state="readonly", help_text=None, **kwargs):
        super().__init__(parent, values=values, state=state, **kwargs)
        self._bind_help_text(parent, help_text)

        self.unbind_class("TCombobox", "<MouseWheel>")
        self.bind("<MouseWheel>", self._redirect_mouse_wheel, add="+")
        self.bind("<Button-4>", self._redirect_mouse_wheel, add="+")
        self.bind("<Button-5>", self._redirect_mouse_wheel, add="+")

    # Optionally, override click behavior if needed:
    def _open_dropdown(self, event):
        # Let the dropdown open normally.
        self.event_generate("<Down>")

    def set_state(self, state: str):
        """Dynamically updates the combobox state."""
        self.config(state=state)


class PHOMODListbox(tk.Listbox, PHOMODHelpTextMixin, PHOMODContextMenuMixin):
    """A listbox widget with a built-in scrollbar, padding, and optional help text/context menu."""

    def __init__(self, parent, height=10, help_text=None, context_menu=None, attach_x=False, attach_y=True, **kwargs):
        super().__init__(parent, height=height, **kwargs)

        self.scroll_helper = _PHOMODAttachableScrollbar(self, attach_x=attach_x, attach_y=attach_y)

        self._bind_help_text(parent, help_text)
        self._bind_context_menu(context_menu)

    def add_item(self, item: str):
        """Adds an item to the listbox."""
        self.insert(tk.END, item)

    def remove_selected(self):
        """Removes the selected item(s) from the listbox."""
        selected_indices = self.curselection()
        for index in reversed(selected_indices):  # Reverse order to avoid index shift issues
            self.delete(index)

    def clear_items(self):
        """Removes all items from the listbox."""
        self.delete(0, tk.END)


class PHOMODTreeview(ttk.Treeview, PHOMODHelpTextMixin, PHOMODContextMenuMixin):
    """A treeview widget with a built-in scrollbar, padded properly, and optional help text/context menu."""

    def __init__(self, parent, columns, help_text=None, context_menu=None, attach_x=False, attach_y=True, **kwargs):
        kwargs.setdefault("show", "tree headings")  # Only set `show` if not already provided
        super().__init__(parent, columns=columns, **kwargs)

        # Attach scrollbars dynamically
        self.scroll_helper = _PHOMODAttachableScrollbar(self, attach_x=attach_x, attach_y=attach_y, pady=5)

        # Properly inherit from mixins (automatic binding)
        self._bind_help_text(parent, help_text)
        self._bind_context_menu(context_menu)

    def add_item(self, parent, text, values=None):
        """Adds an item to the tree under the specified parent node."""
        return self.insert(parent, tk.END, text=text, values=values or [])

    def remove_selected(self):
        """Removes the selected item(s) from the tree."""
        selected_items = self.selection()
        for item in selected_items:
            self.delete(item)

    def clear_items(self):
        """Removes all items from the tree."""
        for item in self.get_children():
            self.delete(item)


# ----------------------------------------------------------------------------------------------------------------------
#                                                                                                            👀 Private
# ----------------------------------------------------------------------------------------------------------------------
class _PHOMODAttachableScrollbar:
    """Helper class to attach a scrollbar to any widget without modifying its behavior."""

    def __init__(self, widget, attach_x=False, attach_y=True, **kwargs):
        self.widget = widget
        self.parent = widget.master

        if attach_y:
            self.scrollbar_y = ttk.Scrollbar(self.parent, orient="vertical", command=self.widget.yview)
            self.widget.configure(yscrollcommand=self.scrollbar_y.set)
            self.scrollbar_y.pack(side="right", fill="y", **kwargs)  # Attach scrollbar to the right

        if attach_x:
            self.scrollbar_x = ttk.Scrollbar(self.parent, orient="horizontal", command=self.widget.xview, **kwargs)
            self.widget.configure(xscrollcommand=self.scrollbar_x.set,  **kwargs)
            self.scrollbar_x.pack(side="bottom", fill="x")  # Attach scrollbar at bottom

    def remove(self):
        """Removes the scrollbar from the widget."""
        if hasattr(self, "scrollbar_y"):
            self.scrollbar_y.pack_forget()
            self.widget.configure(yscrollcommand="")

        if hasattr(self, "scrollbar_x"):
            self.scrollbar_x.pack_forget()
            self.widget.configure(xscrollcommand="")
