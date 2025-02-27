import tkinter as tk
from dataclasses import dataclass
from typing import Callable, Optional, List


@dataclass
class MenuItem:
    """Represents a single item in the context menu."""
    label: str
    command: Optional[Callable] = None
    shortcut: Optional[str] = None


class SimpleContextMenu(tk.Toplevel):
    """A lightweight manually controlled context menu."""

    def __init__(self, parent: tk.Widget, menu_items: List[MenuItem]):
        super().__init__(parent)
        self.withdraw()
        self.overrideredirect(True)
        self.transient(parent)
        self.parent = parent
        self.menu_items = menu_items
        self._selected_index = None
        self.buttons = []

        # Define colors
        self.bg_color = "#F0F0F0"  # Light gray background
        self.highlight_color = "#C0C0C0"  # Slightly darker hover
        self.border_color = "#808080"  # Classic border

        # Create main container
        self.frame = tk.Frame(self, bg=self.border_color)
        self.frame.pack(fill=tk.BOTH, expand=True, padx=2, pady=2)

        # Inner menu frame
        self.inner_frame = tk.Frame(self.frame, bg=self.bg_color)
        self.inner_frame.pack(fill=tk.BOTH, expand=True, padx=1, pady=1)

        self._populate_menu()

        # Keyboard bindings
        self.bind("<Up>", self._navigate_up)
        self.bind("<Down>", self._navigate_down)
        self.bind("<Return>", self._select_item)
        self.bind("<Escape>", lambda e: self.hide())
        self.bind("<FocusOut>", self._on_focus_out)

    def _populate_menu(self):
        """Creates menu items inside the menu."""
        for widget in self.inner_frame.winfo_children():
            widget.destroy()
        self.buttons.clear()
        self._selected_index = None

        for index, item in enumerate(self.menu_items):
            if item.label == "---":
                tk.Frame(self.inner_frame, height=1, bg=self.border_color).pack(fill=tk.X, padx=5, pady=2)
                self.buttons.append(None)
                continue

            row = tk.Frame(self.inner_frame, bg=self.bg_color, padx=5, pady=4)
            row.pack(fill=tk.X, padx=5, pady=2)

            # Hover effects
            def on_hover(event, r=row):
                r.config(bg=self.highlight_color)
                for child in r.winfo_children():
                    child.config(bg=self.highlight_color)

            def on_leave(event, r=row):
                r.config(bg=self.bg_color)
                for child in r.winfo_children():
                    child.config(bg=self.bg_color)

            row.bind("<Enter>", on_hover)
            row.bind("<Leave>", on_leave)
            row.bind("<Button-1>", lambda e, cmd=item.command: self._run_command(cmd) if cmd else None)

            # Title label (left)
            title_label = tk.Label(row, text=item.label, bg=self.bg_color, anchor="w", padx=10)
            title_label.pack(side=tk.LEFT, fill=tk.X, expand=True)
            title_label.bind("<Enter>", on_hover)
            title_label.bind("<Leave>", on_leave)
            title_label.bind("<Button-1>", lambda e, cmd=item.command: self._run_command(cmd) if cmd else None)

            # Accelerator label (right)
            if item.shortcut:
                shortcut_label = tk.Label(row, text=item.shortcut, fg="gray", bg=self.bg_color, anchor="e", padx=10)
                shortcut_label.pack(side=tk.RIGHT)
                shortcut_label.bind("<Enter>", on_hover)
                shortcut_label.bind("<Leave>", on_leave)
                shortcut_label.bind("<Button-1>", lambda e, cmd=item.command: self._run_command(cmd) if cmd else None)

            self.buttons.append(row)

    def show(self, x, y):
        """Displays the menu at the given coordinates."""
        self.geometry(f"+{x}+{y}")
        self.deiconify()
        self.lift()
        self.focus_force()
        self._bind_outside_click()

    def hide(self):
        """Hides the menu."""
        self.withdraw()

    def _bind_outside_click(self):
        """Bind an event that listens for any click outside the menu."""
        self.parent.bind_all("<Button-1>", self._on_click_outside, add="+")
        self.parent.bind_all("<Button-3>", self._on_click_outside, add="+")

    def _on_click_outside(self, event):
        """Closes the menu if the click is outside the menu's bounds."""
        try:
            if not self.winfo_ismapped():
                return

            x1, y1, x2, y2 = self.winfo_rootx(), self.winfo_rooty(), self.winfo_rootx() + self.winfo_width(), self.winfo_rooty() + self.winfo_height()

            if not (x1 <= event.x_root <= x2 and y1 <= event.y_root <= y2):
                self.hide()
        except tk.TclError:
            self.hide()

    def _on_focus_out(self, event):
        self.hide()

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

    def _run_command(self, command):
        if command:
            command()
            self.hide()


# =============================================================================
#                               Usage Example
# =============================================================================

if __name__ == "__main__":
    root = tk.Tk()
    root.geometry("400x300")

    def test_command():
        print("Clicked!")

    # Define menu items
    menu_items = [
        MenuItem("Copy", test_command, "Ctrl+C"),
        MenuItem("Paste", test_command, "Ctrl+V"),
        MenuItem("---"),
        MenuItem("Exit", root.quit, "Alt+F4")
    ]

    # Function to show the menu
    def show_menu(event):
        context_menu = SimpleContextMenu(root, menu_items)
        context_menu.show(event.x_root, event.y_root)

    # Create a button to trigger the menu
    button = tk.Button(root, text="Right Click Me")
    button.pack(pady=50)
    button.bind("<Button-3>", show_menu)

    root.mainloop()
