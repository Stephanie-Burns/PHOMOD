
import tkinter as tk
from tkinter import ttk, Menu
import logging
import pyperclip
from enum import Enum
from collections import namedtuple

app_logger = logging.getLogger("FOMODLogger")

MenuAction = namedtuple("MenuAction", ["label", "accelerator", "group", "separator", "enabled"])


class ContextMenuAction(Enum):
    """Enum for context menu actions with labels, accelerators, grouping, separators, and state."""

    CUT = MenuAction("Cut", "Ctrl+X", "text_edit", False, True)
    COPY = MenuAction("Copy", "Ctrl+C", "text_edit", False, True)
    PASTE = MenuAction("Paste", "Ctrl+V", "text_edit", False, True)
    DELETE = MenuAction("Delete", None, "text_edit", False, True)
    SEPARATOR_TEXT = MenuAction(None, None, "text_edit", True, True)
    SELECT_ALL = MenuAction("Select All", "Ctrl+A", "text_edit", False, True)
    EMPTY_DISABLED = MenuAction("(Coming Soon)", None, "text_edit", False, False)

    @property
    def label(self):
        return self.value.label

    @property
    def accelerator(self):
        return self.value.accelerator

    @property
    def group(self):
        return self.value.group

    @property
    def is_separator(self):
        return self.value.separator

    @property
    def is_enabled(self):
        return self.value.enabled


class PHOMODContextMenu:
    """A flexible right-click context menu for PHOMOD widgets."""

    def __init__(self, root, groups=None):
        """
        Initialize a context menu with only relevant groups.

        :param root: The root Tk window.
        :param groups: A set of action groups to include (e.g., {"text_edit"}).
        """
        self.root = root
        self.parent = None
        self.menu = Menu(root, tearoff=0)
        self.is_open = False
        self.groups = groups or {"text_edit"}

        # Add relevant actions to the menu
        for action in ContextMenuAction:
            if action.group in self.groups:
                if action.is_separator:
                    self.menu.add_separator()
                else:
                    self.menu.add_command(
                        label=action.label,
                        command=self._get_command(action),
                        accelerator=action.accelerator,
                        state="normal" if action.is_enabled else "disabled"
                    )

        # Bind global events to close menu
        for event in ("<Button-1>", "<FocusOut>", "<Unmap>", "<Escape>"):
            self.root.bind(event, self.hide_menu, add=True)

        # windows support
        self._bind_accelerators()

    def _get_command(self, action):
        """Return the appropriate function for a given menu action."""
        commands = {
            ContextMenuAction.CUT: self.cut,
            ContextMenuAction.COPY: self.copy,
            ContextMenuAction.PASTE: self.paste,
            ContextMenuAction.DELETE: self.delete,
            ContextMenuAction.SELECT_ALL: self.select_all,
        }
        return commands.get(action, lambda: None)

    def _bind_accelerators(self):
        """Bind keyboard shortcuts manually for Windows support."""
        if self.root.tk.call("tk", "windowingsystem") == "win32":
            self.root.bind("<Control-x>", lambda e: self.cut())
            self.root.bind("<Control-c>", lambda e: self.copy())
            self.root.bind("<Control-v>", lambda e: self.paste())
            self.root.bind("<Control-a>", lambda e: self.select_all())

    def show_menu(self, event, widget):
        """Display the context menu at the cursor position."""
        if self.is_open:
            self.hide_menu()

        self.parent = widget
        app_logger.debug(f"Opening context menu for widget: {widget}")

        self.update_state()
        self.menu.post(event.x_root, event.y_root)

        self.is_open = True

    def hide_menu(self, event=None):
        """Close the context menu if it's open."""
        if self.is_open:
            self.menu.unpost()
            self.is_open = False

    def update_state(self):
        """Enable or disable menu options based on selection and clipboard state."""
        if not self.parent:
            app_logger.debug("update_state() called but self.parent is None. Skipping update.")
            return

        app_logger.debug(f"Updating menu state for widget: {self.parent}")

        # Selection state
        try:
            selection = self.parent.selection_get()
            if isinstance(self.parent, tk.Text):
                has_selection = bool(selection) and self.parent.index("sel.first") != self.parent.index("sel.last")
            else:
                has_selection = bool(selection) and self.parent.selection_present()
        except tk.TclError:
            has_selection = False

        app_logger.debug(f"Selection valid: {has_selection}")

        # Text presence
        has_text = bool(self.parent.get("1.0", tk.END).strip()) if isinstance(self.parent, tk.Text) else bool(self.parent.get())
        app_logger.debug(f"Widget contains text: {has_text}")

        # Clipboard state
        try:
            has_clipboard = bool(pyperclip.paste())
        except Exception as e:
            app_logger.error(f"Clipboard error: {e}")
            has_clipboard = False

        app_logger.debug(f"Clipboard contains text: {has_clipboard}")

        # Update menu state dynamically
        menu_states = {
            ContextMenuAction.CUT: "normal" if has_selection else "disabled",
            ContextMenuAction.COPY: "normal" if has_selection else "disabled",
            ContextMenuAction.DELETE: "normal" if has_selection else "disabled",
            ContextMenuAction.PASTE: "normal" if has_clipboard else "disabled",
            ContextMenuAction.SELECT_ALL: "normal" if has_text else "disabled",
        }

        for action, state in menu_states.items():
            self.menu.entryconfig(action.label, state=state)
            app_logger.debug(f"Menu item '{action.label}' set to {state}")

    def cut(self):
        """Cut selected text to clipboard."""
        self.copy()
        self.delete()

    def copy(self):
        """Copy selected text to clipboard."""
        try:
            pyperclip.copy(self.parent.selection_get())
        except tk.TclError:
            pass

    def paste(self):
        """Paste text from clipboard, stripping newlines for single-line entries."""
        try:
            text = pyperclip.paste()
            if isinstance(self.parent, ttk.Entry):
                text = text.replace("\r", "").replace("\n", "")
            self.parent.insert(tk.INSERT, text)
        except tk.TclError:
            pass

    def delete(self):
        """Delete selected text."""
        try:
            self.parent.delete("sel.first", "sel.last")
        except tk.TclError:
            pass

    def select_all(self):
        """Select all text in the widget."""
        try:
            if isinstance(self.parent, tk.Text):
                self.parent.tag_add("sel", "1.0", tk.END)
                self.parent.mark_set(tk.INSERT, "1.0")
            else:
                self.parent.select_range(0, tk.END)
                self.parent.icursor(tk.END)
        except tk.TclError:
            pass

# Example usage
if __name__ == "__main__":
    from phomod_widgets import PHOMODTextArea, PHOMODEntry

    root = tk.Tk()
    root.title("PHOMOD Context Menu Example")
    root.geometry("400x250")

    context_menu = PHOMODContextMenu(root)

    entry = PHOMODEntry(root, context_menu=context_menu)
    entry.pack(pady=5, padx=20, fill="x")

    text_area = PHOMODTextArea(root, context_menu=context_menu, height=5, width=40)
    text_area.pack(pady=5, padx=20, fill="both", expand=True)

    root.mainloop()
