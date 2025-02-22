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
