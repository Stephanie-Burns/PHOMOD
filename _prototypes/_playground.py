import tkinter as tk
from tkinter import ttk, Menu, filedialog
import logging
import pyperclip

# Enable detailed logging
logging.basicConfig(level=logging.DEBUG)
app_logger = logging.getLogger("PHOMODLogger")


class ContextMenuAction:
    def __init__(self, label, command, accelerator=None, separator=False):
        self.label = label
        self.command = command
        self.accelerator = accelerator
        self.separator = separator


class UniversalActions:
    """Reusable actions with proper debugging and fixes."""

    @staticmethod
    def cut(target_widget):
        app_logger.debug("Executing Cut Action")
        selection = UniversalActions.get_selection_range(target_widget)  # Save selection
        UniversalActions.copy(target_widget)
        UniversalActions.delete(target_widget, selection)

    @staticmethod
    def copy(target_widget):
        app_logger.debug("Executing Copy Action")
        try:
            text = target_widget.selection_get()
            pyperclip.copy(text)
            app_logger.debug(f"Copied text: {text}")
        except tk.TclError:
            app_logger.warning("Copy failed - No selection")

    @staticmethod
    def paste(target_widget):
        """Paste clipboard text and strip newlines for Entry widgets."""
        try:
            text = pyperclip.paste()
            app_logger.debug(f"Pasting text: {text}")
            if isinstance(target_widget, ttk.Entry):
                text = text.replace("\r", "").replace("\n", "")
            target_widget.insert(tk.INSERT, text)
        except tk.TclError:
            app_logger.warning("Paste failed - Could not insert text")

    @staticmethod
    def delete(target_widget, selection=None):
        """Deletes selected text, restoring selection if needed."""
        app_logger.debug("Executing Delete Action")
        try:
            if selection:
                target_widget.mark_set("insert", selection[0])  # Restore cursor
            target_widget.delete("sel.first", "sel.last")
        except tk.TclError:
            app_logger.warning("Delete failed - No selection")

    @staticmethod
    def select_all(target_widget):
        """Selects all text if available."""
        if UniversalActions.has_text(target_widget):
            app_logger.debug("Executing Select All Action")
            if isinstance(target_widget, tk.Text):
                target_widget.tag_add("sel", "1.0", tk.END)
                target_widget.mark_set(tk.INSERT, "1.0")
            else:
                target_widget.select_range(0, tk.END)
                target_widget.icursor(tk.END)

    @staticmethod
    def has_text(widget):
        """Check if the widget contains text."""
        try:
            text = widget.get("1.0", tk.END).strip() if isinstance(widget, tk.Text) else widget.get()
            has_text = bool(text)
            app_logger.debug(f"Checking text presence: {has_text}")
            return has_text
        except tk.TclError:
            return False

    @staticmethod
    def has_selection(widget):
        """Check if the widget has selected text."""
        try:
            selection = widget.selection_get()
            has_selection = bool(selection)
            app_logger.debug(f"Checking selection presence: {has_selection}")
            return has_selection
        except tk.TclError:
            return False

    @staticmethod
    def get_selection_range(widget):
        """Get the first and last index of the current selection."""
        try:
            return widget.index("sel.first"), widget.index("sel.last")
        except tk.TclError:
            return None


class ContextMenu:
    """A dynamic context menu that updates before display."""

    active_menu = None  # Track the currently open menu

    def __init__(self, root, target_widget, actions):
        self.root = root
        self.target_widget = target_widget
        self.menu = Menu(root, tearoff=0)
        self.actions = actions

        for action in self.actions:
            if action.separator:
                self.menu.add_separator()
            else:
                self.menu.add_command(
                    label=action.label,
                    command=lambda a=action: a.command(target_widget),
                    accelerator=action.accelerator
                )

        self.target_widget.bind("<Button-3>", self.show_menu)
        self.target_widget.bind("<Control-Button-1>", self.show_menu)  # macOS support

        # Global bindings to close menu
        root.bind("<Button-1>", self.hide_menu, add=True)
        root.bind("<FocusOut>", self.hide_menu, add=True)
        root.bind("<Escape>", self.hide_menu, add=True)

    def show_menu(self, event):
        """Show the menu and update state before posting."""
        if ContextMenu.active_menu:
            ContextMenu.active_menu.unpost()

        app_logger.debug(f"Opening context menu for {self.target_widget}")

        # 🔥 Ensure first action updates correctly
        self.update_state(force=True)

        self.menu.post(event.x_root, event.y_root)
        ContextMenu.active_menu = self.menu

    def hide_menu(self, event=None):
        """Hide the menu when clicking elsewhere."""
        if ContextMenu.active_menu:
            ContextMenu.active_menu.unpost()
            ContextMenu.active_menu = None

    def update_state(self, force=False):
        """Enable or disable actions dynamically."""
        app_logger.debug("Updating menu state...")

        for action in self.actions:
            if not action.separator:
                state = "normal"
                if action.label in ["Cut", "Copy", "Delete"]:
                    state = "normal" if UniversalActions.has_selection(self.target_widget) else "disabled"
                elif action.label == "Paste":
                    state = "normal" if pyperclip.paste() else "disabled"
                elif action.label == "Select All":
                    state = "normal" if UniversalActions.has_text(self.target_widget) else "disabled"

                self.menu.entryconfig(action.label, state=state)
                app_logger.debug(f"Set '{action.label}' to {state}")

        # 🔥 Ensure the first action updates correctly by forcing a redraw
        if force:
            self.menu.update_idletasks()


# Define Menus
def create_text_context_menu(root, target_widget):
    actions = [
        ContextMenuAction("Cut", UniversalActions.cut, "Ctrl+X"),
        ContextMenuAction("Copy", UniversalActions.copy, "Ctrl+C"),
        ContextMenuAction("Paste", UniversalActions.paste, "Ctrl+V"),
        ContextMenuAction("Delete", UniversalActions.delete),
        ContextMenuAction(None, None, separator=True),
        ContextMenuAction("Select All", UniversalActions.select_all, "Ctrl+A"),
    ]
    return ContextMenu(root, target_widget, actions)


# Hook into GUI
if __name__ == "__main__":
    root = tk.Tk()
    root.title("PHOMOD Context Menu Debug Mode")

    text_area = tk.Text(root, height=5, width=40)
    text_area.pack(pady=5, padx=20, fill="both", expand=True)

    create_text_context_menu(root, text_area)

    root.mainloop()
