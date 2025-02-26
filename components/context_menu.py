
import os
import logging
import tkinter as tk
from dataclasses import dataclass, field
from tkinter import ttk
from typing import Callable, Optional, List

from PIL import Image, ImageTk

app_logger = logging.getLogger('PHOMODLogger')


# ======================================================================================================================
#                                                                                                            Objects 🏗️
# ======================================================================================================================
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

    Attributes:
        show_icons (bool): Whether to display icons in menu items. Default is True.
        menu_padding (int): Padding inside the context menu (in pixels). Default is 10.
        item_spacing (int): Spacing between menu items (in pixels). Default is 5.
        title_accelerator_spacing (int): Horizontal spacing between the item title and its accelerator/shortcut. Default is 8.
        icon_title_spacing (int): Horizontal spacing between the icon and the item title. Default is 6.
        border_color (str): Color of the menu border, specified as a hex string. Default is "#3A3A3A".
        highlight_color (str): Background color used for hover effects. Default is "#D0D0D0".
        separator_color (str): Color of the menu separators. Default is "#808080".
        default_animation (str): Default animation type for showing/hiding the menu. Options include "fade", "slide", and "bounce". Default is "fade".
        fade_duration (int): Duration in milliseconds between steps in the fade animation. Lower values yield a faster fade. Default is 20.
        slide_distance (int): Distance in pixels that the menu moves during the slide animation. Default is 30.
        bounce_heights (List[int]): A list of pixel offsets defining the bounce animation. Default is [0, -5, -10, -5, 0].
        shadow_effect (bool): Whether to apply a subtle drop shadow to the menu. Default is True.
    """
    show_icons: bool = True
    menu_padding: int = 10
    item_spacing: int = 5
    title_accelerator_spacing: int = 8
    icon_title_spacing: int = 6
    border_color: str = "#3A3A3A"
    highlight_color: str = "#D0D0D0"
    separator_color: str = "#808080"
    default_animation: str = "fade"
    fade_duration: int = 20
    slide_distance: int = 30
    bounce_heights: List[int] = field(default_factory=lambda: [0, -5, -10, -5, 0])
    shadow_effect: bool = True


# ======================================================================================================================
#                                                                                                  ContextMenu Class 📜
# ======================================================================================================================
class ContextMenu(tk.Toplevel):
    def __init__(self, parent, config: ContextMenuConfig, style_prefix="ContextMenu", enable_shortcuts=True):
        super().__init__(parent)
        self.withdraw()
        self.overrideredirect(True)
        self.transient(parent)
        self.parent = parent
        self.style_prefix = style_prefix
        self.config_obj = config
        self.menu_items: List[MenuItem] = []
        self._selected_index = None
        self.buttons = []
        self._default_icon = self._create_placeholder_icon()
        self.enable_shortcuts = enable_shortcuts
        self.animation_type = self.config_obj.default_animation
        self._outside_click_id = None  # For outside-click binding

        self.frame = ttk.Frame(self, style=f"{self.style_prefix}.Container.TFrame",
                                padding=self.config_obj.menu_padding)
        self.frame.pack(fill=tk.BOTH, expand=True)

        self._init_styles()
        self._apply_shadow()

        # Keyboard bindings
        self.bind("<Up>", self._navigate_up)
        self.bind("<Down>", self._navigate_down)
        self.bind("<Return>", self._select_item)
        self.bind("<Escape>", lambda e: self.hide())
        self.bind("<FocusOut>", self._on_focus_out)

    # ------------------------------------------------------------------------------------------------------------------
    #                                                                                                        Styling 🎨
    # ------------------------------------------------------------------------------------------------------------------
    def _init_styles(self):
        style = ttk.Style()
        base_bg = style.lookup("TFrame", "background") or "SystemButtonFace"
        self.base_bg = base_bg
        self.hover_bg = self.config_obj.highlight_color

        style.configure(f"{self.style_prefix}.Container.TFrame",
                        background=base_bg,
                        relief="solid",
                        borderwidth=2,
                        highlightbackground=self.config_obj.border_color,
                        highlightthickness=2)

        self.frame.configure(style=f"{self.style_prefix}.Container.TFrame")

    def _apply_shadow(self):
        if self.config_obj.shadow_effect:
            try:
                # This uses a simple overrideredirect trick to simulate shadow.
                self.tk.call("tk", "scaling", 1.0)
                self.config(bg="black")
                self.attributes("-transparentcolor", "black")
            except tk.TclError:
                app_logger.debug("🖥️  Shadow effect not supported on this platform.")

    @staticmethod
    def _create_placeholder_icon():
        img = Image.new("RGBA", (16, 16), (0, 0, 0, 0))
        return ImageTk.PhotoImage(img)

    def _load_icon(self, icon_path):
        if self.config_obj.show_icons and icon_path and os.path.exists(icon_path):
            try:
                img = Image.open(icon_path).resize((16, 16), Image.Resampling.LANCZOS)
                return ImageTk.PhotoImage(img)
            except Exception as e:
                app_logger.debug(f"⚠️  Failed to load icon '{icon_path}': {e}")
        return self._default_icon

    # ------------------------------------------------------------------------------------------------------------------
    #                                                                                              Animation Methods 🎭
    # ------------------------------------------------------------------------------------------------------------------
    def show(self, x, y):
        app_logger.debug(f"📂 Showing menu with animation '{self.animation_type}' at ({x}, {y})")
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
        app_logger.debug(f"❌ Hiding menu with animation '{self.animation_type}'")
        if self.animation_type == "fade":
            self._fade_out(1.0)
        else:
            self.withdraw()
        self._unbind_outside_click()

    def _fade_in(self, alpha):
        if alpha < 1.0:
            alpha += 0.07
            try:
                self.attributes("-alpha", alpha)
            except tk.TclError:
                return
            self.after(self.config_obj.fade_duration, lambda: self._fade_in(alpha))
        else:
            self.attributes("-alpha", 1.0)

    def _fade_out(self, alpha):
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

    def _slide_in(self, x, y, step=0):
        total_steps = 15
        if step < total_steps:
            offset = int(self.config_obj.slide_distance * (1 - step / total_steps))
            new_x = x - offset
            self.geometry(f"+{new_x}+{y}")
            self.after(10, lambda: self._slide_in(x, y, step + 1))
        else:
            self.geometry(f"+{x}+{y}")

    def _bounce_in(self, x, y, step=0):
        heights = self.config_obj.bounce_heights
        if step < len(heights):
            new_y = y + heights[step]
            self.geometry(f"+{x}+{new_y}")
            self.after(20, lambda: self._bounce_in(x, y, step + 1))
        else:
            self.geometry(f"+{x}+{y}")

    # ------------------------------------------------------------------------------------------------------------------
    #                                                                               Outside Click and Focus Handling 🖱️
    # ------------------------------------------------------------------------------------------------------------------
    def _bind_outside_click(self):
        self._outside_click_id = self.parent.bind("<ButtonPress>", self._on_click_outside, add="+")
        app_logger.debug("🔗 Bound outside click event.")

    def _unbind_outside_click(self):
        if self._outside_click_id:
            self.parent.unbind("<ButtonPress>", self._outside_click_id)
            self._outside_click_id = None
            app_logger.debug("🔓 Unbound outside click event.")

    def _on_click_outside(self, event):
        try:
            widget_under_cursor = self.winfo_containing(event.x_root, event.y_root)
        except tk.TclError:
            widget_under_cursor = None

        if widget_under_cursor and self._is_descendant(widget_under_cursor):
            app_logger.debug("🖱️  Click inside menu detected.")
            return
        app_logger.debug("🛑 Outside click detected. Closing menu.")
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

    def _is_descendant(self, widget):
        while widget:
            if widget == self:
                return True
            widget = widget.master
        return False

    def _close_all(self, force=False):
        app_logger.debug("🐞 Closing menu.")
        self.hide()

    # ------------------------------------------------------------------------------------------------------------------
    #                                                                                      Menu Items and Navigation 🧭
    # ------------------------------------------------------------------------------------------------------------------
    def set_items(self, menu_items: List[MenuItem]):
        self.menu_items = menu_items
        self._populate_menu()
        self._bind_shortcuts()

    def _populate_menu(self):
        for widget in self.frame.winfo_children():
            widget.destroy()
        self.buttons.clear()
        self._selected_index = None

        for i, item in enumerate(self.menu_items):
            if item.label == "---":
                sep = ttk.Separator(self.frame, orient="horizontal")
                sep.configure(style=f"{self.style_prefix}.Separator.TSeparator")
                sep.pack(fill=tk.X, padx=self.config_obj.item_spacing, pady=self.config_obj.item_spacing)
                self.buttons.append(None)
                continue

            icon = self._load_icon(item.icon_path)
            formatted_shortcut = self._format_shortcut(item.shortcut)

            row = tk.Frame(self.frame, bg=self.base_bg, padx=5, pady=4,
                           highlightthickness=1, highlightbackground=self.base_bg)
            row.pack(fill=tk.X, expand=True, padx=5, pady=2)
            row.bind("<Button-1>", lambda e, cmd=item.command: self._run_command(cmd) if cmd else None)

            # Hover effects with logging
            def on_hover(event, r=row):
                r.config(bg=self.hover_bg, highlightbackground=self.config_obj.separator_color)
                for child in r.winfo_children():
                    child.config(bg=self.hover_bg)
                app_logger.debug(f"🖱️  Hover started on item: {item.label}")

            def on_leave(event, r=row):
                r.config(bg=self.base_bg, highlightbackground=self.base_bg)
                for child in r.winfo_children():
                    child.config(bg=self.base_bg)
                app_logger.debug(f"🖱️  Hover ended on item: {item.label}")

            row.bind("<Enter>", on_hover)
            row.bind("<Leave>", on_leave)

            # Icon and label
            if self.config_obj.show_icons:
                icon_label = tk.Label(row, image=icon, bg=self.base_bg)
                icon_label.image = icon

                icon_label.pack(side=tk.LEFT,
                                padx=(self.config_obj.icon_title_spacing, self.config_obj.icon_title_spacing))
            main_label = tk.Label(row, text=item.label, bg=self.base_bg, anchor="w")
            main_label.pack(side=tk.LEFT, fill=tk.X, expand=True)

            if formatted_shortcut:
                shortcut_label = tk.Label(row, text=formatted_shortcut, bg=self.base_bg, anchor="e")
                shortcut_label.pack(side=tk.RIGHT,
                                    padx=(self.config_obj.title_accelerator_spacing, self.config_obj.item_spacing))

            for widget in row.winfo_children():
                widget.bind("<Button-1>", lambda e, cmd=item.command: self._run_command(cmd) if cmd else None)
                widget.bind("<Enter>", on_hover)
                widget.bind("<Leave>", on_leave)

            self.buttons.append(row)

    @staticmethod
    def _format_shortcut(shortcut):
        if not shortcut:
            return ""
        formatted = shortcut.replace("<", "").replace(">", "").replace("Control", "Ctrl")
        parts = formatted.split("-")
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

    def _highlight(self, index):
        if index < len(self.buttons) and self.buttons[index]:
            self._selected_index = index
            self.buttons[index].focus_set()

    # ------------------------------------------------------------------------------------------------------------------
    #                                                                        Shortcut Bindings and Command Execution ⌨️
    # ------------------------------------------------------------------------------------------------------------------
    def _bind_shortcuts(self):
        if not self.enable_shortcuts:
            return
        for item in self.menu_items:
            if item.shortcut:
                shortcut = item.shortcut
                command = item.command
                if command:
                    self.parent.bind_all(shortcut, lambda e, cmd=command: self._run_command(cmd))
                    app_logger.debug(f"⌨️  Bound shortcut {shortcut} for {item.label}")

    def _unbind_shortcuts(self):
        for item in self.menu_items:
            if item.shortcut:
                self.parent.unbind_all(item.shortcut)
                app_logger.debug(f"⌨️  Unbound shortcut {item.shortcut} for {item.label}")

    def enable_shortcut_bindings(self):
        self.enable_shortcuts = True
        self._bind_shortcuts()

    def disable_shortcut_bindings(self):
        self.enable_shortcuts = False
        self._unbind_shortcuts()

    def _run_command(self, command):
        if command:
            app_logger.debug(f"🚀 Executing command: {command.__name__}")
            command()
            app_logger.debug("🚀 Command executed; closing menu.")
            self._close_all(force=True)


# ======================================================================================================================
#                                                                                           ContextMenuManager Class 🎮
# ======================================================================================================================
class ContextMenuManager:
    def __init__(self, parent, config: ContextMenuConfig, style_prefix="ContextMenu"):
        self.parent = parent
        self.menu = ContextMenu(parent, config, style_prefix)

    def attach(self, widget, menu_items: List[MenuItem]):
        widget.bind("<Button-3>", lambda e: self._show_menu(e, menu_items))
        widget.bind("<Menu>", lambda e: self._show_menu_keyboard(widget, menu_items))
        widget.bind("<Shift-F10>", lambda e: self._show_menu_keyboard(widget, menu_items))

    def _show_menu(self, event, menu_items: List[MenuItem]):
        app_logger.debug("📂 Right-click detected. Animation: " + self.menu.animation_type)
        self.menu.set_items(menu_items)
        self.menu.show(event.x_root, event.y_root)

    def _show_menu_keyboard(self, widget, menu_items: List[MenuItem]):
        app_logger.debug("📂 Keyboard-triggered menu. Animation: " + self.menu.animation_type)
        self.menu.set_items(menu_items)
        widget.update_idletasks()
        x = widget.winfo_rootx() + 10
        y = widget.winfo_rooty() + 10
        self.menu.show(x, y)
