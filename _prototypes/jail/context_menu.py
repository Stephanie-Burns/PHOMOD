import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
import os

DEBUG = True

def debug_print(*args):
    if DEBUG:
        print("[DEBUG]", *args)

# ===============================================================
# ContextMenu class
# ===============================================================
class ContextMenu(tk.Toplevel):
    def __init__(self, parent, style_prefix="ContextMenu",
                 enable_shortcuts=True, animation_type="fade"):
        super().__init__(parent)
        self.withdraw()
        self.overrideredirect(True)
        self.transient(parent)
        self.parent = parent
        self.style_prefix = style_prefix
        self.menu_items = []
        self._selected_index = None
        self.buttons = []
        self._default_icon = self._create_placeholder_icon()
        self.enable_shortcuts = enable_shortcuts
        self.animation_type = animation_type
        self._outside_click_id = None  # For outside-click binding

        self.frame = ttk.Frame(self, style=f"{self.style_prefix}.Container.TFrame", padding=10)
        self.frame.pack(fill=tk.BOTH, expand=True)

        self._init_styles()

        # Keyboard bindings
        self.bind("<Up>", self._navigate_up)
        self.bind("<Down>", self._navigate_down)
        self.bind("<Return>", self._select_item)
        self.bind("<Escape>", lambda e: self.hide())
        self.bind("<FocusOut>", self._on_focus_out)

    # ---------------------------------------------------------------
    # SHOW / HIDE and Animation Methods
    # ---------------------------------------------------------------
    def show(self, x, y):
        debug_print("show() called with animation_type =", self.animation_type)
        self.geometry(f"+{x}+{y}")
        self.deiconify()
        if self.animation_type != "fade":
            self.attributes("-alpha", 1.0)  # Ensure opacity is full
        self.lift()
        self.wait_visibility()
        self.update()
        self.focus_force()
        self._bind_outside_click()

        if self.animation_type == "fade":
            debug_print("Running fade animation on show()")
            self.attributes("-alpha", 0.0)
            self._fade_in(0.0)
        elif self.animation_type == "slide":
            debug_print("Running slide animation on show()")
            self._slide_in(x, y)
        elif self.animation_type == "bounce":
            debug_print("Running bounce animation on show()")
            self._bounce_in(x, y)

    def hide(self):
        debug_print("hide() called with animation_type =", self.animation_type)
        if self.animation_type == "fade":
            debug_print("Running fade out animation on hide()")
            self._fade_out(1.0)
        else:
            self.withdraw()
        self._unbind_outside_click()

    # --- Fade Animations ---
    def _fade_in(self, alpha):
        debug_print(f"_fade_in called with alpha = {alpha:.2f}")
        if alpha < 1.0:
            alpha += 0.07  # Slightly faster fade-in
            try:
                self.attributes("-alpha", alpha)
            except tk.TclError:
                return
            self.after(20, lambda: self._fade_in(alpha))  # Faster interval
        else:
            try:
                self.attributes("-alpha", 1.0)
            except tk.TclError:
                return

    def _fade_out(self, alpha):
        debug_print(f"_fade_out called with alpha = {alpha:.2f}")
        try:
            if not self.winfo_exists():
                return
        except tk.TclError:
            return

        if alpha > 0.0:
            alpha -= 0.07  # Faster fade-out
            try:
                self.attributes("-alpha", alpha)
            except tk.TclError:
                return
            self.after(20, lambda: self._fade_out(alpha))  # Faster interval
        else:
            try:
                self.withdraw()
            except tk.TclError:
                return

    # --- Slide Animation ---
    def _slide_in(self, x, y, step=0):
        total_steps = 15  # Slightly fewer steps
        debug_print(f"_slide_in called with step = {step}")
        if step < total_steps:
            offset = int(30 * (1 - step / total_steps))  # Start 30px left
            new_x = x - offset
            self.geometry(f"+{new_x}+{y}")
            self.after(10, lambda: self._slide_in(x, y, step + 1))  # Faster slide
        else:
            self.geometry(f"+{x}+{y}")

    # --- Bounce Animation ---
    def _bounce_in(self, x, y, step=0):
        bounce_heights = [0, -5, -10, -5, 0]  # Less extreme bounce
        debug_print(f"_bounce_in called with step = {step}")
        if step < len(bounce_heights):
            new_y = y + bounce_heights[step]
            self.geometry(f"+{x}+{new_y}")
            self.after(20, lambda: self._bounce_in(x, y, step + 1))  # Faster bounce
        else:
            self.geometry(f"+{x}+{y}")

    # ---------------------------------------------------------------
    # Outside Click and Focus Handling
    # ---------------------------------------------------------------
    def _bind_outside_click(self):
        self._outside_click_id = self.parent.bind("<ButtonPress>", self._on_click_outside, add="+")

    def _unbind_outside_click(self):
        if self._outside_click_id:
            self.parent.unbind("<ButtonPress>", self._outside_click_id)
            self._outside_click_id = None

    def _on_click_outside(self, event):
        try:
            widget_under_cursor = self.winfo_containing(event.x_root, event.y_root)
        except tk.TclError:
            widget_under_cursor = None

        if widget_under_cursor and self._is_descendant(widget_under_cursor):
            debug_print("Click inside menu detected. Ignoring close.")
            return

        debug_print("Click outside detected. Closing menu.")
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
        debug_print("Closing menu.")
        self.hide()

    # ---------------------------------------------------------------
    # Styling and Icon Loading
    # ---------------------------------------------------------------
    def _init_styles(self):
        """Initialize styles and record theme colors for our custom row widgets."""
        style = ttk.Style()
        base_bg = style.lookup("TFrame", "background") or "SystemButtonFace"
        self.base_bg = base_bg
        self.hover_bg = "#d0d0d0"  # Slightly lighter gray for hover.

        # Ensure menu border is visible but not too dark
        style.configure(f"{self.style_prefix}.Container.TFrame",
                        background=base_bg,
                        relief="solid",
                        borderwidth=2,
                        highlightbackground="#3A3A3A",
                        highlightthickness=2)

        # Apply the style to self.frame
        self.frame.configure(style=f"{self.style_prefix}.Container.TFrame")

    @staticmethod
    def _create_placeholder_icon():
        from PIL import Image  # In case it's not imported at the top
        img = Image.new("RGBA", (16, 16), (0, 0, 0, 0))
        return ImageTk.PhotoImage(img)

    def _load_icon(self, icon_path):
        if icon_path and os.path.exists(icon_path):
            try:
                img = Image.open(icon_path).resize((16, 16), Image.Resampling.LANCZOS)
                return ImageTk.PhotoImage(img)
            except Exception as e:
                debug_print(f"Warning: Failed to load icon '{icon_path}'. Error:", e)
        return self._default_icon

    # ---------------------------------------------------------------
    # Menu Items and Navigation
    # ---------------------------------------------------------------
    def set_items(self, menu_items):
        """Set menu items and rebuild the menu. Extra submenu info is ignored."""
        self.menu_items = menu_items
        self._populate_menu()
        self._bind_shortcuts()

    def _populate_menu(self):
        """Rebuilds the menu with a clean layout, proper hover borders, and no extra space before the icon."""
        for widget in self.frame.winfo_children():
            widget.destroy()
        self.buttons.clear()
        self._selected_index = None

        for i, item in enumerate(self.menu_items):
            label, command, icon_path, *_ = item

            if label == "---":
                ttk.Separator(self.frame, orient="horizontal").pack(fill=tk.X, padx=5, pady=6)
                self.buttons.append(None)
                continue

            icon = self._load_icon(icon_path)
            shortcut = item[4] if len(item) > 4 else ""
            formatted_shortcut = self._format_shortcut(shortcut)

            # Create a row with hover effect and no extra spacing
            row = tk.Frame(self.frame, bg=self.base_bg, padx=5, pady=4,
                           highlightthickness=1, highlightbackground=self.base_bg)  # Border hidden by default
            row.pack(fill=tk.X, expand=True, padx=5, pady=2)
            row.bind("<Button-1>", lambda e, cmd=command: self._run_command(cmd) if cmd else None)

            # Hover effect
            def on_hover(event, r=row):
                r.config(bg=self.hover_bg, highlightbackground="#808080")
                for child in r.winfo_children():
                    child.config(bg=self.hover_bg)

            def on_leave(event, r=row):
                r.config(bg=self.base_bg, highlightbackground=self.base_bg)
                for child in r.winfo_children():
                    child.config(bg=self.base_bg)

            row.bind("<Enter>", on_hover)
            row.bind("<Leave>", on_leave)

            # Icon and Label (properly spaced)
            icon_label = tk.Label(row, image=icon, bg=self.base_bg)
            icon_label.image = icon
            icon_label.pack(side=tk.LEFT, padx=(6, 6))  # Remove left space

            main_label = tk.Label(row, text=label, bg=self.base_bg, anchor="w")
            main_label.pack(side=tk.LEFT, fill=tk.X, expand=True)

            # Right-aligned shortcut label
            if formatted_shortcut:
                shortcut_label = tk.Label(row, text=formatted_shortcut, bg=self.base_bg, anchor="e")
                shortcut_label.pack(side=tk.RIGHT, padx=(8, 8))  # Adjust shortcut spacing

            # Ensure full-row clickability
            for widget in row.winfo_children():
                widget.bind("<Button-1>", lambda e, cmd=command: self._run_command(cmd) if cmd else None)
                widget.bind("<Enter>", on_hover)
                widget.bind("<Leave>", on_leave)

            self.buttons.append(row)

    @staticmethod
    def _format_shortcut(shortcut):
        if not shortcut:
            return ""
        formatted = shortcut.replace("<", "").replace(">", "")
        formatted = formatted.replace("Control", "Ctrl")
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
            self.buttons[self._selected_index].invoke()

    def _highlight(self, index):
        if index < len(self.buttons) and self.buttons[index]:
            self._selected_index = index
            self.buttons[index].focus_set()

    # ---------------------------------------------------------------
    # Shortcut Bindings and Command Execution
    # ---------------------------------------------------------------
    def _bind_shortcuts(self):
        if not self.enable_shortcuts:
            return
        for item in self.menu_items:
            if len(item) > 4 and item[4]:
                shortcut = item[4]
                command = item[1]
                if command:
                    self.parent.bind_all(shortcut, lambda e, cmd=command: self._run_command(cmd))

    def _unbind_shortcuts(self):
        for item in self.menu_items:
            if len(item) > 4 and item[4]:
                shortcut = item[4]
                self.parent.unbind_all(shortcut)

    def enable_shortcut_bindings(self):
        self.enable_shortcuts = True
        self._bind_shortcuts()

    def disable_shortcut_bindings(self):
        self.enable_shortcuts = False
        self._unbind_shortcuts()

    def _run_command(self, command):
        if command:
            debug_print("Running command:", command.__name__)
            command()
            debug_print("Closing menu after command execution.")
            self._close_all(force=True)

# ===============================================================
# ContextMenuManager class
# ===============================================================
class ContextMenuManager:
    def __init__(self, parent, style_prefix="ContextMenu"):
        self.parent = parent
        self.menu = ContextMenu(parent, style_prefix)

    def attach(self, widget, menu_items):
        widget.bind("<Button-3>", lambda e: self._show_menu(e, menu_items))
        widget.bind("<Menu>", lambda e: self._show_menu_keyboard(widget, menu_items))
        widget.bind("<Shift-F10>", lambda e: self._show_menu_keyboard(widget, menu_items))

    def _show_menu(self, event, menu_items):
        debug_print("Button right-click detected. Current animation type:", self.menu.animation_type)
        self.menu.set_items(menu_items)
        self.menu.show(event.x_root, event.y_root)

    def _show_menu_keyboard(self, widget, menu_items):
        debug_print("Keyboard menu triggered. Current animation type:", self.menu.animation_type)
        self.menu.set_items(menu_items)
        widget.update_idletasks()
        x = widget.winfo_rootx() + 10
        y = widget.winfo_rooty() + 10
        self.menu.show(x, y)

# ===============================================================
# Main Application Code
# ===============================================================
if __name__ == "__main__":
    root = tk.Tk()
    root.geometry("400x300")
    root.title("Advanced Context Menu Demo")

    style = ttk.Style()
    style.theme_use("clam")

    # Sample functions
    def copy_function():
        print("Copying function")

    def paste_function():
        print("Pasting button")

    def theme_toggle():
        theme = "alt" if style.theme_use() == "clam" else "clam"
        style.theme_use(theme)
        cm.menu._init_styles()

    # Define menu items (submenu removed)
    menu_items = [
        ("Copy", copy_function, "global.png", None, "<Control-c>"),
        ("Paste", paste_function, "paste.png", None, "<Control-v>"),
        ("---", None, None, None, None),  # Separator
        ("Exit with a long title", root.quit, "exit.png", None, "<Alt-F4>"),
    ]

    # Create a button to trigger the context menu
    button = ttk.Button(root, text="Right Click or Press Menu Key")
    button.pack(pady=50, padx=50)

    # Attach the context menu
    cm = ContextMenuManager(root)
    cm.attach(button, menu_items)

    # Animation selection UI
    animation_label = ttk.Label(root, text="Select Animation:")
    animation_label.pack()

    animation_var = tk.StringVar(value="fade")
    animation_options = ["fade", "slide", "bounce"]
    animation_menu = ttk.Combobox(root, textvariable=animation_var,
                                  values=animation_options, state="readonly")
    animation_menu.pack()

    def update_animation():
        new_animation = animation_var.get()
        debug_print("Animation type updated to:", new_animation)
        cm.menu.animation_type = new_animation

    apply_animation_button = ttk.Button(root, text="Apply Animation", command=update_animation)
    apply_animation_button.pack(pady=10)

    # Theme toggle button
    theme_button = ttk.Button(root, text="Toggle Theme", command=theme_toggle)
    theme_button.pack(pady=20)

    root.mainloop()
