import logging

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
    """Mixin that redirects mouse scroll events to the nearest scrollable parent."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Bind mouse wheel events
        self.bind("<MouseWheel>", self._redirect_mouse_wheel)
        self.bind("<Button-4>", self._redirect_mouse_wheel)  # Linux scroll up
        self.bind("<Button-5>", self._redirect_mouse_wheel)  # Linux scroll down

    def _redirect_mouse_wheel(self, event):
        """Redirects the scroll event to the nearest scrollable parent (if any)."""
        parent = self._find_scrollable_parent()
        if parent:
            parent.event_generate("<MouseWheel>", delta=event.delta)
            parent.event_generate("<Button-4>" if event.num == 4 else "<Button-5>")
        return "break"  # Prevents the widget itself from handling the scroll

    def _find_scrollable_parent(self):
        """Finds the nearest PHOMODScrollableFrame and returns its canvas."""
        from phomod_widgets import PHOMODScrollableFrame  # 👈 Import here to avoid circular imports

        parent = self.master
        while parent:
            if isinstance(parent, PHOMODScrollableFrame):
                return parent.canvas
            parent = parent.master
        return None  # No scrollable parent found
