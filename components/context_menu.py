import os
import logging
import tkinter as tk
from dataclasses import dataclass, field
from typing import Callable, List, Optional

from PIL import Image, ImageTk

app_logger = logging.getLogger("PHOMODLogger")

# =============================================================================
#                                Data Objects
# =============================================================================

@dataclass
class MenuItem:
    """
    Represents a single item in the context menu.

    Attributes:
        label (str): The text displayed for the menu item.
        command (Optional[Callable]): The function to be executed when the item is clicked.
        icon_path (Optional[str]): The path to an icon file for this menu item.
        shortcut (Optional[str]): The keyboard shortcut (if applicable).
    """
    label: str
    command: Optional[Callable] = None
    icon_path: Optional[str] = None
    shortcut: Optional[str] = None


@dataclass
class ContextMenuConfig:
    """
    Configuration class for the context menu's appearance and behavior.

    Supports both light and dark mode dynamically.
    """
    show_icons: bool = True
    menu_padding: int = 10         # Overall padding for the menu
    item_spacing: int = 5          # Spacing between items
    title_accelerator_spacing: int = 60
    icon_title_spacing: int = 6
    default_animation: str = "fade"
    fade_duration: int = 20
    slide_distance: int = 30
    bounce_heights: List[int] = field(default_factory=lambda: [0, -5, -10, -5, 0])
    shadow_effect: bool = True

    # Light/Dark mode handling
    mode: str = "light"  # "light" or "dark"

    # Color schemes for both modes
    light_mode: dict = field(default_factory=lambda: {
        "border_color": "#808080",
        "background_color": "#F0F0F0",
        "highlight_color": "#C0C0C0",
        "text_color": "black",
        "shortcut_color": "gray",
        "separator_color": "#808080"
    })

    dark_mode: dict = field(default_factory=lambda: {
        "border_color": "#555555",
        "background_color": "#2B2B2B",
        "highlight_color": "#3D3D3D",
        "text_color": "#E0E0E0",
        "shortcut_color": "#B0B0B0",
        "separator_color": "#555555"
    })

    def get_colors(self) -> dict:
        """Returns the appropriate color set based on the mode."""
        return self.dark_mode if self.mode == "dark" else self.light_mode


# =============================================================================
#                          Context Menu Manager Class
# =============================================================================

class ContextMenuManager:
    """
    Binds and manages a context menu for any widget.
    """

    def __init__(
            self,
            parent: tk.Widget,
            config: ContextMenuConfig,
            asset_manager=None
    ) -> None:
        self.parent = parent
        self.menu = ContextMenu(parent, config=config, asset_manager=asset_manager)

    def attach(self, widget: tk.Widget, menu_items: List[MenuItem]) -> None:
        widget.bind("<Button-3>", lambda e: self._show_menu(e, menu_items))
        widget.bind("<Menu>", lambda e: self._show_menu_keyboard(widget, menu_items))
        widget.bind("<Shift-F10>", lambda e: self._show_menu_keyboard(widget, menu_items))

    def _show_menu(self, event: tk.Event, menu_items: List[MenuItem]) -> None:
        app_logger.debug(f"Right-click detected. Animation: {self.menu.animation_type}")
        self.menu.set_items(menu_items)
        self.menu.show(event.x_root, event.y_root)

    def _show_menu_keyboard(self, widget: tk.Widget, menu_items: List[MenuItem]) -> None:
        app_logger.debug(f"Keyboard-triggered menu. Animation: {self.menu.animation_type}")
        self.menu.set_items(menu_items)
        widget.update_idletasks()
        x = widget.winfo_rootx() + 10
        y = widget.winfo_rooty() + 10
        self.menu.show(x, y)


# =============================================================================
#                              Context Menu Class
# =============================================================================

class ContextMenu(tk.Toplevel):
    """
    A customizable, animated context menu for Tkinter applications.

    This Toplevel window is styled and animated according to the provided configuration.
    The styling is based on your bare bones prototype using plain tk widgets.
    """

    def __init__(
            self,
            parent: tk.Widget,
            config: Optional[ContextMenuConfig] = None,
            asset_manager=None,
            enable_shortcuts: bool = True
    ) -> None:
        super().__init__(parent)
        self.withdraw()
        self.overrideredirect(True)
        self.transient(parent)

        self.config_obj: ContextMenuConfig = config or ContextMenuConfig()
        self.animation_type: str = self.config_obj.default_animation
        self.buttons: List[Optional[tk.Widget]] = []
        self.enable_shortcuts: bool = enable_shortcuts
        self.menu_items: List[MenuItem] = []
        self.parent = parent
        self.asset_manager = asset_manager

        # Retrieve color scheme based on the mode.
        colors = self.config_obj.get_colors()
        self.border_color = colors["border_color"]
        self.base_bg = colors["background_color"]
        self.hover_bg = colors["highlight_color"]
        self.text_color = colors["text_color"]
        self.shortcut_color = colors["shortcut_color"]
        self.separator_color = colors["separator_color"]

        # Build the container with an outer border.
        self.container = tk.Frame(self, bg=self.border_color)
        self.container.pack(fill=tk.BOTH, expand=True, padx=2, pady=2)
        # Inner frame holds the menu items.
        self.frame = tk.Frame(self.container, bg=self.base_bg)
        self.frame.pack(fill=tk.BOTH, expand=True, padx=1, pady=1)

        self._apply_shadow()

        # Keyboard navigation bindings.
        self.bind("<Up>", self._navigate_up)
        self.bind("<Down>", self._navigate_down)
        self.bind("<Return>", self._select_item)
        self.bind("<Escape>", lambda e: self.hide())
        self.bind("<FocusOut>", self._on_focus_out)

    # -------------------------------------------------------------------------
    #                          Shadow & Icon Handling
    # -------------------------------------------------------------------------
    def _apply_shadow(self):
        if self.config_obj.shadow_effect:
            try:
                self.tk.call("tk", "scaling", 1.0)
                self.config(bg="black")
                self.attributes("-transparentcolor", "black")
            except tk.TclError:
                app_logger.debug("Shadow effect not supported on this platform.")

    def _create_placeholder_icon(self, size=(16, 16)) -> tk.PhotoImage:
        return ImageTk.PhotoImage(Image.new("RGBA", size, (0, 0, 0, 0)))

    def _load_icon(self, icon_name: Optional[str]) -> tk.PhotoImage:
        if not self.config_obj.show_icons:
            return self._create_placeholder_icon()
        if self.asset_manager and icon_name:
            return self.asset_manager.get_icon(icon_name)
        return self._create_placeholder_icon()

    # -------------------------------------------------------------------------
    #                           Animation Methods
    # -------------------------------------------------------------------------
    def show(self, x: int, y: int):
        app_logger.debug(f"Showing menu with animation '{self.animation_type}' at ({x}, {y})")
        self.geometry(f"+{x}+{y}")
        self.deiconify()
        if self.animation_type != "fade":
            self.attributes("-alpha", 1.0)
        self.lift()
        self.wait_visibility()
        self.update()
        self.focus_force()
        self._bind_outside_click()

        if self.animation_type == "fade":
            self.attributes("-alpha", 0.0)
            self._fade_in(0.0)
        elif self.animation_type == "slide":
            self._slide_in(x, y)
        elif self.animation_type == "bounce":
            self._bounce_in(x, y)

    def hide(self):
        app_logger.debug(f"Hiding menu with animation '{self.animation_type}'")
        if self.animation_type == "fade":
            self._fade_out(1.0)
        else:
            self.withdraw()
        self._unbind_outside_click()

    def _fade_in(self, alpha: float):
        if alpha < 1.0:
            alpha += 0.07
            try:
                self.attributes("-alpha", alpha)
            except tk.TclError:
                return
            self.after(self.config_obj.fade_duration, lambda: self._fade_in(alpha))
        else:
            self.attributes("-alpha", 1.0)

    def _fade_out(self, alpha: float):
        try:
            if not self.winfo_exists():
                return
        except tk.TclError:
            return
        if alpha > 0.0:
            alpha -= 0.07
            try:
                self.attributes("-alpha", alpha)
            except tk.TclError:
                return
            self.after(self.config_obj.fade_duration, lambda: self._fade_out(alpha))
        else:
            self.withdraw()

    def _slide_in(self, x: int, y: int, step: int = 0):
        total_steps = 15
        if step < total_steps:
            offset = int(self.config_obj.slide_distance * (1 - step / total_steps))
            new_x = x - offset
            self.geometry(f"+{new_x}+{y}")
            self.after(10, lambda: self._slide_in(x, y, step + 1))
        else:
            self.geometry(f"+{x}+{y}")

    def _bounce_in(self, x: int, y: int, step: int = 0):
        heights = self.config_obj.bounce_heights
        if step < len(heights):
            new_y = y + heights[step]
            self.geometry(f"+{x}+{new_y}")
            self.after(20, lambda: self._bounce_in(x, y, step + 1))
        else:
            self.geometry(f"+{x}+{y}")

    # -------------------------------------------------------------------------
    #                    Outside Click and Focus Handling
    # -------------------------------------------------------------------------
    def _bind_outside_click(self):
        self._outside_click_id = self.parent.bind("<ButtonPress>", self._on_click_outside, add="+")
        app_logger.debug("Bound outside click event.")

    def _unbind_outside_click(self):
        if hasattr(self, '_outside_click_id') and self._outside_click_id:
            self.parent.unbind("<ButtonPress>", self._outside_click_id)
            self._outside_click_id = None
            app_logger.debug("Unbound outside click event.")

    def _on_click_outside(self, event):
        try:
            widget_under_cursor = self.winfo_containing(event.x_root, event.y_root)
        except tk.TclError:
            widget_under_cursor = None
        if widget_under_cursor and self._is_descendant(widget_under_cursor):
            app_logger.debug("Click inside menu detected.")
            return
        app_logger.debug("Outside click detected. Closing menu.")
        self._close_all(force=True)

    def _on_focus_out(self, event):
        self.after(50, self._check_focus)

    def _check_focus(self):
        try:
            current_focus = self.focus_get()
        except (tk.TclError, KeyError):
            current_focus = None
        if current_focus is None or not self._is_descendant(current_focus):
            self.hide()

    def _is_descendant(self, widget) -> bool:
        while widget:
            if widget == self:
                return True
            widget = widget.master
        return False

    def _close_all(self, force: bool = False):
        app_logger.debug("Closing menu.")
        self.hide()

    # -------------------------------------------------------------------------
    #           Menu Items, Navigation, and Command Execution
    # -------------------------------------------------------------------------
    def set_items(self, menu_items: List[MenuItem]):
        self.menu_items = menu_items
        self._populate_menu()
        self._bind_shortcuts()

    def _populate_menu(self):
        # Clear existing items.
        for child in self.frame.winfo_children():
            child.destroy()
        self.buttons.clear()
        self._selected_index = None

        for index, item in enumerate(self.menu_items):
            if item.label == "---":
                separator = tk.Frame(self.frame, height=1, bg=self.separator_color)
                separator.pack(fill=tk.X, padx=self.config_obj.item_spacing, pady=self.config_obj.item_spacing)
                self.buttons.append(None)
                continue

            # Create a row for the menu item.
            row = tk.Frame(self.frame, bg=self.base_bg, padx=5, pady=4)
            row.pack(fill=tk.X, padx=5, pady=2)
            row.bind("<Enter>", lambda e, r=row: self._set_hover(r, True))
            row.bind("<Leave>", lambda e, r=row: self._set_hover(r, False))
            row.bind("<Button-1>", lambda e, cmd=item.command: self._run_command(cmd))

            # Optionally display an icon.
            if self.config_obj.show_icons:
                icon = self._load_icon(item.icon_path)
                icon_label = tk.Label(row, image=icon, bg=self.base_bg)
                icon_label.image = icon  # Retain reference.
                icon_label.pack(side=tk.LEFT, padx=(self.config_obj.icon_title_spacing, self.config_obj.icon_title_spacing))
                icon_label.bind("<Enter>", lambda e, r=row: self._set_hover(r, True))
                icon_label.bind("<Leave>", lambda e, r=row: self._set_hover(r, False))
                icon_label.bind("<Button-1>", lambda e, cmd=item.command: self._run_command(cmd))

            # Title label.
            main_label = tk.Label(row, text=item.label, bg=self.base_bg, fg=self.text_color, anchor="w", padx=10)
            main_label.pack(side=tk.LEFT, fill=tk.X, expand=True)
            main_label.bind("<Enter>", lambda e, r=row: self._set_hover(r, True))
            main_label.bind("<Leave>", lambda e, r=row: self._set_hover(r, False))
            main_label.bind("<Button-1>", lambda e, cmd=item.command: self._run_command(cmd))

            # Shortcut label (if applicable).
            formatted_shortcut = self._format_shortcut(item.shortcut)
            if formatted_shortcut:
                shortcut_label = tk.Label(row, text=formatted_shortcut, bg=self.base_bg, fg=self.shortcut_color, anchor="e", padx=10)
                shortcut_label.pack(side=tk.RIGHT, padx=(self.config_obj.title_accelerator_spacing, self.config_obj.item_spacing))
                shortcut_label.bind("<Enter>", lambda e, r=row: self._set_hover(r, True))
                shortcut_label.bind("<Leave>", lambda e, r=row: self._set_hover(r, False))
                shortcut_label.bind("<Button-1>", lambda e, cmd=item.command: self._run_command(cmd))

            self.buttons.append(row)

    def _set_hover(self, row, hover):
        bg = self.hover_bg if hover else self.base_bg
        row.config(bg=bg)
        for child in row.winfo_children():
            child.config(bg=bg)

    @staticmethod
    def _format_shortcut(shortcut: Optional[str]) -> str:
        if not shortcut:
            return ""
        formatted = shortcut.replace("<", "").replace(">", "").replace("Control", "Ctrl").replace("Escape", "ESC")
        parts = formatted.split("-")
        if parts:
            parts[-1] = parts[-1].upper()
        return "-".join(parts)

    def _navigate_up(self, event):
        if self._selected_index is None:
            self._highlight(0)
        else:
            new_index = (self._selected_index - 1) % len(self.buttons)
            while self.buttons[new_index] is None:
                new_index = (new_index - 1) % len(self.buttons)
            self._highlight(new_index)

    def _navigate_down(self, event):
        if self._selected_index is None:
            self._highlight(0)
        else:
            new_index = (self._selected_index + 1) % len(self.buttons)
            while self.buttons[new_index] is None:
                new_index = (new_index + 1) % len(self.buttons)
            self._highlight(new_index)

    def _select_item(self, event):
        if self._selected_index is not None and self.buttons[self._selected_index]:
            self._run_command(self.menu_items[self._selected_index].command)

    def _highlight(self, index: int):
        if index < len(self.buttons) and self.buttons[index]:
            self._selected_index = index
            self.buttons[index].focus_set()

    def _bind_shortcuts(self):
        if not self.enable_shortcuts:
            return
        for item in self.menu_items:
            if item.shortcut and item.command:
                self.parent.bind_all(item.shortcut, lambda e, cmd=item.command: self._run_command(cmd))
                app_logger.debug(f"Bound shortcut {item.shortcut} for {item.label}")

    def _unbind_shortcuts(self):
        for item in self.menu_items:
            if item.shortcut:
                self.parent.unbind_all(item.shortcut)
                app_logger.debug(f"Unbound shortcut {item.shortcut} for {item.label}")

    def enable_shortcut_bindings(self):
        self.enable_shortcuts = True
        self._bind_shortcuts()

    def disable_shortcut_bindings(self):
        self.enable_shortcuts = False
        self._unbind_shortcuts()

    def _run_command(self, command: Optional[Callable]):
        if command:
            app_logger.debug(f"Executing command: {command.__name__ if hasattr(command, '__name__') else command}")
            command()
            app_logger.debug("Command executed; closing menu.")
            self._close_all(force=True)
