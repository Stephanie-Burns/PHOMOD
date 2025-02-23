
import logging
import tkinter as tk
from tkinter import ttk

from phomod_mixins import PHOMODHelpTextMixin, PHOMODContextMenuMixin

app_logger = logging.getLogger('FOMODLogger')


# ----------------------------------------------------------------------------------------------------------------------
#                                                                                              🏗 STRUCTURAL CONTAINERS
# ----------------------------------------------------------------------------------------------------------------------
class PHOMODFrame(ttk.Frame, PHOMODHelpTextMixin):
    """A basic frame with optional help text integration."""
    def __init__(self, parent, controller=None, help_text=None, **kwargs):
        super().__init__(parent, **kwargs)
        self.controller = controller
        self._bind_help_text(parent, help_text)


class PHOMODLabelFrame(ttk.Labelframe, PHOMODHelpTextMixin):
    """A label frame with optional custom label widget and help text."""
    def __init__(self, parent, controller=None, text="", help_text=None, label_widget=None, **kwargs):
        self.controller = controller
        self._configure_label(kwargs, text, label_widget)
        super().__init__(parent, **kwargs)
        self._bind_help_text(parent, help_text)

    def _configure_label(self, kwargs, text, label_widget):
        """Decide whether to use a label widget or the default text."""
        if label_widget:
            kwargs["labelwidget"] = label_widget
        else:
            kwargs["text"] = text


class PHOMODScrollableFrame(tk.Frame):
    """A reusable scrollable frame with automatic mousewheel support."""
    def __init__(self, parent, controller=None, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.controller = controller
        self._create_scrollable_container()

    def _create_scrollable_container(self):
        """Creates a scrollable frame with a vertical scrollbar."""
        self.canvas = tk.Canvas(self, borderwidth=0, highlightthickness=0)
        vsb = tk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        self.canvas.configure(yscrollcommand=vsb.set)

        vsb.pack(side="right", fill="y")
        self.canvas.pack(side="left", fill=tk.BOTH, expand=True)

        self.inner_frame = PHOMODFrame(self.canvas, controller=self.controller)
        self.inner_window = self.canvas.create_window((0, 0), window=self.inner_frame, anchor="nw")

        self.inner_frame.bind("<Configure>", self._on_frame_configure)
        self.canvas.bind("<Configure>", self._on_canvas_configure)
        self.inner_frame.bind("<Enter>", lambda e: self._bind_mousewheel())
        self.inner_frame.bind("<Leave>", lambda e: self._unbind_mousewheel())

    def _bind_mousewheel(self):
        """Binds mouse wheel scrolling to the canvas and all widgets inside inner_frame."""
        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)
        self.canvas.bind_all("<Button-4>", self._on_mousewheel)  # Linux (scroll up)
        self.canvas.bind_all("<Button-5>", self._on_mousewheel)  # Linux (scroll down)
        for widget in self.inner_frame.winfo_children():
            widget.bind("<Enter>", lambda e: self._bind_mousewheel())
            widget.bind("<Leave>", lambda e: self._unbind_mousewheel())

    def _unbind_mousewheel(self):
        """Unbinds the mouse wheel event when cursor leaves."""
        self.canvas.unbind_all("<MouseWheel>")
        self.canvas.unbind_all("<Button-4>")
        self.canvas.unbind_all("<Button-5>")

    def _on_mousewheel(self, event):
        """Handles the mouse wheel scrolling."""
        if event.num == 5 or event.delta < 0:  # Scroll down (Linux or Windows)
            self.canvas.yview_scroll(1, "units")
        elif event.num == 4 or event.delta > 0:  # Scroll up (Linux or Windows)
            self.canvas.yview_scroll(-1, "units")

    def _on_frame_configure(self, event):
        """Updates scroll region when the inner frame resizes."""
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def _on_canvas_configure(self, event):
        """Ensures the inner window resizes correctly."""
        self.canvas.itemconfigure(self.inner_window, width=event.width)


# ----------------------------------------------------------------------------------------------------------------------
#                                                                                                  🖼 BASIC UI ELEMENTS
# ----------------------------------------------------------------------------------------------------------------------
class PHOMODLabel(ttk.Label, PHOMODHelpTextMixin):
    """A basic label with help text integration."""
    def __init__(self, parent, text, help_text=None, **kwargs):
        super().__init__(parent, text=text, **kwargs)
        self._bind_help_text(parent, help_text)


class PHOMODEntry(ttk.Entry, PHOMODHelpTextMixin, PHOMODContextMenuMixin):
    """An entry widget that redirects mouse scroll events to the parent scrollable frame."""

    def __init__(self, parent, textvariable=None, help_text=None, context_menu=None, **kwargs):
        super().__init__(parent, textvariable=textvariable, **kwargs)
        self._bind_help_text(parent, help_text)
        self._bind_context_menu(context_menu)

        # Redirect mouse wheel events to the scrollable container
        self.bind("<MouseWheel>", self._redirect_mouse_wheel)
        self.bind("<Button-4>", self._redirect_mouse_wheel)  # Linux scroll up
        self.bind("<Button-5>", self._redirect_mouse_wheel)  # Linux scroll down

    def _redirect_mouse_wheel(self, event):
        """Redirects the scroll event to the nearest scrollable parent (if any)."""
        parent = self._find_scrollable_parent()
        if parent:
            parent.event_generate("<MouseWheel>", delta=event.delta)
            parent.event_generate("<Button-4>" if event.num == 4 else "<Button-5>")
        return "break"  # Prevents the entry itself from handling the scroll

    def _find_scrollable_parent(self):
        """Finds the nearest scrollable frame (PHOMODScrollableFrame)."""
        parent = self.master
        while parent:
            if isinstance(parent, PHOMODScrollableFrame):
                return parent.canvas
            parent = parent.master
        return None  # No scrollable parent found


class PHOMODTextArea(tk.Text, PHOMODHelpTextMixin, PHOMODContextMenuMixin):
    """A multi-line text widget with help text and context menu integration."""
    def __init__(self, parent, help_text=None, context_menu=None, **kwargs):
        super().__init__(parent, **kwargs)
        self._bind_help_text(parent, help_text)
        self._bind_context_menu(context_menu)


# ----------------------------------------------------------------------------------------------------------------------
#                                                                                                🎛 INTERACTIVE WIDGETS
# ----------------------------------------------------------------------------------------------------------------------
class PHOMODComboBox(ttk.Combobox, PHOMODHelpTextMixin):
    """A combobox that redirects mouse scroll events to the parent scrollable frame."""

    def __init__(self, parent, values, help_text=None, **kwargs):
        super().__init__(parent, values=values, **kwargs)
        self._bind_help_text(parent, help_text)

        # Redirect mouse wheel events to the scrollable container
        self.bind("<MouseWheel>", self._redirect_mouse_wheel)
        self.bind("<Button-4>", self._redirect_mouse_wheel)  # Linux scroll up
        self.bind("<Button-5>", self._redirect_mouse_wheel)  # Linux scroll down

    def _redirect_mouse_wheel(self, event):
        """Redirects the scroll event to the nearest scrollable parent (if any)."""
        parent = self._find_scrollable_parent()
        if parent:
            parent.event_generate("<MouseWheel>", delta=event.delta)
            parent.event_generate("<Button-4>" if event.num == 4 else "<Button-5>")
        return "break"  # Prevents the combobox itself from scrolling

    def _find_scrollable_parent(self):
        """Finds the nearest scrollable frame (PHOMODScrollableFrame)."""
        parent = self.master
        while parent:
            if isinstance(parent, PHOMODScrollableFrame):
                return parent.canvas
            parent = parent.master
        return None  # No scrollable parent found


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
