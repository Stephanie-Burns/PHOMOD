import logging
import tkinter as tk

app_logger = logging.getLogger('FOMODLogger')


class PHOMODHelpTextMixin:
    """Mixin to automatically bind help text to widgets if a help manager exists."""

    def _bind_help_text(self, parent, help_text):
        """Automatically binds help text if the parent has a help manager."""
        if help_text:
            controller = self._find_controller(parent)  # Walk up the widget tree
            if controller and hasattr(controller, "help_manager"):
                controller.help_manager.bind_help(self, help_text)
                app_logger.info(
                    f"✅ Bound help text: '{help_text}' to {self.__class__.__name__}"
                )
            else:
                app_logger.warning(
                    f"⚠️ Could not find a valid controller for {self.__class__.__name__} when binding help text."
                )

    def _find_controller(self, widget):
        """Walks up the widget tree to find the controller."""
        while widget is not None:
            if hasattr(widget, "controller"):  # Found a widget with a controller
                return widget.controller
            widget = getattr(widget, "master", None)  # Move up the widget tree
        return None  # No controller found


class PHOMODContextMenuMixin:
    """Mixin to attach a shared context menu to widgets with OS compatibility."""

    def _bind_context_menu(self, context_menu):
        """Binds the context menu to right-click events."""
        if context_menu:
            self.context_menu = context_menu
            self.bind("<Button-3>", self._show_context_menu)  # Right-click (Linux/Windows)
            self.bind("<Button-2>", self._show_context_menu)  # MacOS secondary click

    def _show_context_menu(self, event):
        """Displays the context menu at the mouse position."""
        if hasattr(self, "context_menu") and self.context_menu:
            self.context_menu.show_menu(event, self)


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
