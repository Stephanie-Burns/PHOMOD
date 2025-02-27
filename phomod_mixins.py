
import logging
import tkinter as tk
from typing import Optional, List, Callable
from components import ContextMenuManager, MenuItem, ContextMenuConfig

app_logger = logging.getLogger('PHOMODLogger')


class PHOMODHelpTextMixin:
    """Mixin to automatically bind help text to widgets if a help manager exists."""

    def _bind_help_text(self, parent, help_text):
        """Automatically binds help text if the parent has a help manager."""
        if help_text:
            help_manager = self._find_help_manager(parent)
            if help_manager:
                help_manager.bind_help(self, help_text)
                app_logger.debug(f"✅ Bound help text: '{help_text}' to {self.__class__.__name__}")
            else:
                app_logger.warning(f"⚠️ No valid help manager found for {self.__class__.__name__}")

    def _find_help_manager(self, widget):
        """Walks up the widget tree to find the help manager. Falls back to the toplevel widget."""
        while widget:
            if hasattr(widget, "help_manager"):
                return widget.help_manager
            widget = getattr(widget, "master", None)
        # Fallback: try the toplevel widget.
        root = self.winfo_toplevel() if hasattr(self, "winfo_toplevel") else None
        if root and hasattr(root, "help_manager"):
            return root.help_manager
        return None


class PHOMODContextMenuMixin:
    """Mixin to add a customizable context menu to text widgets."""

    def __init__(self, context_menu_config: Optional["ContextMenuConfig"] = None,
                 custom_menu_items: Optional[List[MenuItem]] = None):
        self.context_menu_manager = None  # Set during attachment
        self.context_menu_config = context_menu_config or ContextMenuConfig()

        # Allow customization but fall back to a sensible default if None provided
        self.menu_items = custom_menu_items or self._default_menu_items()

    def attach_context_menu(self, widget: tk.Widget):
        """Attach the context menu to the given widget."""
        if not self.context_menu_manager:
            self.context_menu_manager = ContextMenuManager(widget, self.context_menu_config)
            self.context_menu_manager.attach(widget, self.menu_items)

    def _default_menu_items(self) -> List[MenuItem]:
        """Provide default menu actions for general text areas."""
        return [
            MenuItem("Copy", lambda: self._clipboard_action("copy"), "copy.png", "<Control-c>"),
            MenuItem("Paste", lambda: self._clipboard_action("paste"), "paste.png", "<Control-v>"),
            MenuItem("Select All", lambda: self._clipboard_action("select_all"), None, "<Control-a>"),
        ]

    def _clipboard_action(self, action: str):
        """Perform clipboard-related actions."""
        if action == "cut":
            self.event_generate("<<Cut>>")
        elif action == "copy":
            self.event_generate("<<Copy>>")
        elif action == "paste":
            self.event_generate("<<Paste>>")
        elif action == "select_all":
            self.tag_add("sel", "1.0", "end")

    def _clear_text(self):
        """Clears the text widget's contents."""
        self.configure(state="normal")
        self.delete("1.0", tk.END)
        self.configure(state="disabled")


class PHOMODScrollRedirectMixin:
    """Mixin that redirects mouse wheel events to the nearest scrollable parent's canvas."""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Unbind default scroll behavior at the class level to prevent interference.
        self.unbind_class(self.winfo_class(), "<MouseWheel>")
        self.unbind_class(self.winfo_class(), "<Button-4>")
        self.unbind_class(self.winfo_class(), "<Button-5>")
        # Bind our own handler
        self.bind("<MouseWheel>", self._redirect_mouse_wheel, add="+")
        self.bind("<Button-4>", self._redirect_mouse_wheel, add="+")  # Linux
        self.bind("<Button-5>", self._redirect_mouse_wheel, add="+")

    def _redirect_mouse_wheel(self, event):
        app_logger.debug(f"Scroll event on {self}: num={event.num}, delta={event.delta}")
        # Use a fallback if delta is 0 (Linux might do that)
        delta = event.delta
        if delta == 0:
            if event.num == 4:
                delta = 120
            elif event.num == 5:
                delta = -120
        norm = 1 if delta < 0 else -1

        parent_canvas = self._find_scrollable_parent()
        if parent_canvas:
            app_logger.debug(f"Redirecting scroll to parent canvas: {parent_canvas} by {norm} units")
            parent_canvas.yview_scroll(norm, "units")
            return "break"
        else:
            app_logger.warning(f"No scrollable parent found for {self}")
        return None

    def _find_scrollable_parent(self):
        parent = self.master
        while parent:
            if hasattr(parent, "canvas"):
                return parent.canvas
            parent = parent.master
        return None
