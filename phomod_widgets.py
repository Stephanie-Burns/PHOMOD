from tkinter import ttk
import logging


app_logger = logging.getLogger('')


class PHOMODWidgetMixin:
    """Mixin to automatically bind help text to widgets if a help manager exists."""

    def _bind_help_text(self, parent, help_text):
        """Automatically binds help text if the parent has a help manager."""
        if help_text:
            controller = self._find_controller(parent)  # Walk up the widget tree
            if controller and hasattr(controller, "help_manager"):
                controller.help_manager.bind_help(self, help_text)
                app_logger.info(f"✅ Bound help text: '{help_text}' to {self.__class__.__name__}")
            else:
                app_logger.warning(f"⚠️ Could not find a valid controller for {self.__class__.__name__} when binding help text.")

    def _find_controller(self, widget):
        """Walks up the widget tree to find the controller."""
        while widget is not None:
            if hasattr(widget, "controller"):  # Found a widget with controller
                return widget.controller
            widget = widget.master  # Move up to the parent widget
        return None  # No controller found


class PHOMODLabel(ttk.Label, PHOMODWidgetMixin):
    def __init__(self, parent, text, help_text=None, *args, **kwargs):
        super().__init__(parent, text=text, *args, **kwargs)
        self._bind_help_text(parent, help_text)


class PHOMODComboBox(ttk.Combobox, PHOMODWidgetMixin):
    def __init__(self, parent, values, help_text=None, *args, **kwargs):
        super().__init__(parent, values=values, *args, **kwargs)

        # Prevent mouse scroll from changing values
        self.bind("<MouseWheel>", self._disable_mouse_wheel)
        self.bind("<Button-4>", self._disable_mouse_wheel)
        self.bind("<Button-5>", self._disable_mouse_wheel)

        self._bind_help_text(parent, help_text)

    def _disable_mouse_wheel(self, event):
        """Prevents mouse scroll from changing the combobox value."""
        return "break"


class PHOMODButton(ttk.Button, PHOMODWidgetMixin):
    def __init__(self, parent, text, command=None, help_text=None, padding=(10, 6), *args, **kwargs):
        kwargs.setdefault("padding", padding)  # Set default if not provided
        super().__init__(parent, text=text, command=command, *args, **kwargs)
        self._bind_help_text(parent, help_text)


class PHOMODCheckbutton(ttk.Checkbutton, PHOMODWidgetMixin):
    def __init__(self, parent, text, variable, help_text=None, *args, **kwargs):
        super().__init__(parent, text=text, variable=variable, *args, **kwargs)
        self._bind_help_text(parent, help_text)


class PHOMODEntry(ttk.Entry, PHOMODWidgetMixin):
    def __init__(self, parent, textvariable, help_text=None, *args, **kwargs):
        super().__init__(parent, textvariable=textvariable, *args, **kwargs)
        self._bind_help_text(parent, help_text)


class PHOMODFrame(ttk.Frame, PHOMODWidgetMixin):
    def __init__(self, parent, controller=None, help_text=None, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.controller = controller  # Store controller at the frame level
        self._bind_help_text(parent, help_text)


class PHOMODLabelFrame(ttk.Labelframe, PHOMODWidgetMixin):
    def __init__(self, parent, controller=None, text="", help_text=None, *args, **kwargs):
        super().__init__(parent, text=text, *args, **kwargs)
        self.controller = controller  # Ensure this label frame has access to the controller
        self._bind_help_text(parent, help_text)
