## **PHOMOD Context Menu Documentation**

### **Overview**
The **PHOMOD Context Menu** is a flexible and reusable right-click menu system for text widgets, providing essential text-editing operations like Cut, Copy, Paste, and Select All. It is designed to work with both `ttk.Entry` and `tk.Text` widgets while ensuring compatibility across operating systems.

---

## **1. Installation & Setup**

### **Requirements**
- Python 3.6+
- `tkinter` for GUI functionality
- `pyperclip` for clipboard management (ensure `xclip` or `xsel` is installed on Linux)

### **Integration**
To use the context menu in your project, import and initialize it within your Tkinter application:

```python
from phomod_context_menu import PHOMODContextMenu
from phomod_widgets import PHOMODTextArea, PHOMODEntry

root = tk.Tk()
context_menu = PHOMODContextMenu(root)

entry = PHOMODEntry(root, context_menu=context_menu)
entry.pack(pady=5, padx=20, fill="x")

text_area = PHOMODTextArea(root, context_menu=context_menu, height=5, width=40)
text_area.pack(pady=5, padx=20, fill="both", expand=True)

root.mainloop()
```

This automatically binds right-click actions to the entry and text widgets.

---

## **2. Core Concepts**

### **Context Menu Actions (`ContextMenuAction`)**
A structured Enum defining available menu options:

- `CUT` - Removes selected text and stores it in the clipboard
- `COPY` - Copies selected text to the clipboard
- `PASTE` - Inserts clipboard contents at the cursor position
- `DELETE` - Removes selected text without copying
- `SELECT_ALL` - Selects all text in the widget
- `SEPARATOR_TEXT` - Creates a separator in the menu
- `EMPTY_DISABLED` - Placeholder for future actions

Each action is a named tuple storing its label, keyboard shortcut, and grouping behavior.

---

### **PHOMODContextMenuMixin**
A mixin that attaches the context menu to compatible widgets. This allows multiple widgets to share the same context menu instance.

#### **Usage Example:**
```python
class PHOMODEntry(ttk.Entry, PHOMODContextMenuMixin):
    def __init__(self, parent, context_menu, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self._bind_context_menu(context_menu)
```

---

## **3. Class Reference**

### **`PHOMODContextMenu`**
#### **Purpose:**
Manages the right-click context menu and dynamically updates its state based on selection and clipboard contents.

#### **Initialization:**
```python
context_menu = PHOMODContextMenu(root)
```

#### **Methods:**
- `show_menu(event, widget)`: Displays the context menu at the cursor position.
- `hide_menu(event=None)`: Hides the menu when clicking elsewhere or losing focus.
- `update_state()`: Dynamically enables/disables menu items based on text selection and clipboard contents.
- `cut()`, `copy()`, `paste()`, `delete()`, `select_all()`: Perform respective text-editing actions.

---

### **4. Behavior & Special Cases**
| Case | Behavior |
|------|---------|
| **No text selected** | Cut, Copy, and Delete are disabled |
| **Empty clipboard** | Paste is disabled |
| **Right-clicking on a widget** | Opens the menu specific to that widget |
| **Closing the menu** | Clicking elsewhere, pressing Escape, or losing focus closes the menu |
| **Supports both `ttk.Entry` and `tk.Text`** | Detects the correct widget type and applies operations accordingly |

---

### **5. Example Usage**

#### **Basic Setup with `PHOMODEntry` and `PHOMODTextArea`**
```python
root = tk.Tk()
context_menu = PHOMODContextMenu(root)

entry = PHOMODEntry(root, context_menu=context_menu)
entry.pack(pady=5, padx=20, fill="x")

text_area = PHOMODTextArea(root, context_menu=context_menu, height=5, width=40)
text_area.pack(pady=5, padx=20, fill="both", expand=True)

root.mainloop()
```

This will ensure both widgets have right-click context menus enabled, making it easy for users to perform text operations without needing keyboard shortcuts.

---

### **6. Future Enhancements**
- **Customizable Actions**: Allow developers to add additional menu items dynamically.
- **Undo/Redo Support**: Add an undo/redo stack for enhanced usability.
- **Context-aware Menus**: Detects whether a widget is a password field, numeric entry, or multiline text area, and adjusts available options accordingly.

---

### **7. Troubleshooting**
#### **Clipboard actions not working on Linux?**
Make sure `xclip` or `xsel` is installed:
```bash
sudo apt install xclip  # Debian/Ubuntu
sudo pacman -S xclip    # Arch Linux
```

#### **Context menu doesn't appear?**
- Ensure the widget is correctly bound to the context menu.
- Debug logs can be enabled by configuring `FOMODLogger` to `DEBUG` level.

---

### **Final Notes**
The `PHOMODContextMenu` system is designed for **modular, reusable, and scalable** use across different Tkinter-based applications. Developers can easily integrate it into new projects while ensuring consistent and predictable behavior across platforms.
