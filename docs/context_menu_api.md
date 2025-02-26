Below is a sample API documentation in Markdown format that explains how to use the context menu code, its features, and customization options. You can include this in your project’s documentation so that you (and others) will remember how to work with it later.

---

# Context Menu API Documentation

## Overview

The Context Menu API provides an advanced, animated context menu for Tkinter applications. It supports multiple animation styles (fade, slide, bounce), keyboard navigation, accelerator (shortcut) bindings, and automatic closing when clicking outside or losing focus. The API is implemented through two main classes:

- **`ContextMenu`**: A subclass of `tk.Toplevel` that handles the display, animation, and behavior of the menu.
- **`ContextMenuManager`**: A helper class to attach the context menu to a widget and manage its triggering (e.g., via right-click or keyboard).

## Setup and Requirements

- **Python version**: Tested with Python 3.x.
- **Dependencies**:
  - Tkinter (standard library)
  - Pillow (PIL) for image handling  
    Install via pip if needed:
    ```bash
    pip install Pillow
    ```
- **Style/Themes**: Uses `ttk.Style` for theming. The default theme in the sample code is `"clam"`, but you can adjust this as needed.

## Using the ContextMenu

### Creating and Attaching a Context Menu

1. **Instantiate a ContextMenuManager:**
   
   In your main application, create an instance of `ContextMenuManager` and pass it the parent (usually your main `tk.Tk` instance).

   ```python
   cm = ContextMenuManager(root)
   ```

2. **Define Menu Items:**

   Menu items should be provided as a list of tuples. Each tuple has the following format:
   
   ```python
   (label, command, icon_path, unused_placeholder, shortcut)
   ```
   
   - **`label`**: The text to display (use `"---"` for a separator).
   - **`command`**: A function to be executed when the item is selected.
   - **`icon_path`**: Path to an icon image file (optional; a placeholder icon is used if not found).
   - **`unused_placeholder`**: Currently unused (reserved for potential future extensions such as submenus).
   - **`shortcut`**: A keyboard accelerator (e.g., `"<Control-c>"`).

   Example:
   
   ```python
   menu_items = [
       ("Copy", copy_function, "global.png", None, "<Control-c>"),
       ("Paste", paste_function, "paste.png", None, "<Control-v>"),
       ("---", None, None, None, None),  # Separator
       ("Exit", root.quit, "exit.png", None, "<Alt-F4>"),
   ]
   ```

3. **Attach the Menu to a Widget:**

   Use the `attach` method of your `ContextMenuManager` to bind the context menu to a widget (e.g., a button). The menu will be triggered by right-click, the Menu key, or Shift+F10.
   
   ```python
   button = ttk.Button(root, text="Right Click or Press Menu Key")
   button.pack(pady=50, padx=50)
   cm.attach(button, menu_items)
   ```

### Animation Styles

The context menu supports three animation types:
- **Fade**: The menu gradually changes its opacity from 0 to 1 (or vice versa on hide).
- **Slide**: The menu slides in from a horizontal offset (default: 50 pixels from the left).
- **Bounce**: The menu appears with a vertical “bounce” effect.

You can select the animation type via a combobox (or any other UI control) and update the menu's `animation_type` property. For example:

```python
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
```

### Accelerator (Shortcut) Bindings

- When you set up your menu items, specify a shortcut string (e.g., `"<Control-c>"`).
- The API automatically binds these shortcuts using `bind_all` so that when you press the key combination, the associated command is executed and the menu is closed.
- To disable or enable accelerator bindings at runtime, use:
  
  ```python
  cm.menu.disable_shortcut_bindings()
  cm.menu.enable_shortcut_bindings()
  ```

### Keyboard Navigation

- **Up/Down arrows**: Navigate between menu items.
- **Return (Enter)**: Activate the currently highlighted item.
- **Escape**: Closes the menu.
- **Focus management**: The menu automatically closes when it loses focus or when a click occurs outside its area.

## Customization and Theming

- **Styles**: The `_init_styles` method sets up the style for the menu frame and buttons based on your current theme. You can modify these styles or use a different theme.
- **Icons**: The API uses Pillow (PIL) to load icons. If an icon fails to load, a transparent placeholder is used.
- **Geometry and Animation Parameters**: Animation routines (fade, slide, bounce) have adjustable parameters (e.g., alpha increments, step counts, delays). Modify these within the respective methods (`_fade_in`, `_slide_in`, `_bounce_in`) if needed.

## Debugging

- Debug messages are controlled by a global `DEBUG` flag.
- To enable or disable debug output, set `DEBUG = True` or `False` at the top of the module.
- Debug output includes information about:
  - Which animation branch is running.
  - The current alpha value for fade animations.
  - Step count for slide and bounce animations.
  - Binding of accelerators and outside click handling.

## Code Structure Summary

- **`ContextMenu`**:  
  - **Initialization**: Sets up the Toplevel window, styling, and keyboard bindings.  
  - **Animation Methods**: `_fade_in`, `_fade_out`, `_slide_in`, `_bounce_in` – control how the menu appears and hides.  
  - **Outside Click and Focus Handling**: Methods like `_bind_outside_click`, `_on_click_outside`, and `_check_focus` ensure the menu closes when clicking elsewhere.  
  - **Menu Population and Navigation**: `_populate_menu`, `_navigate_up`, `_navigate_down`, `_select_item` – create the menu items and support keyboard navigation.  
  - **Accelerator Bindings**: `_bind_shortcuts` and `_unbind_shortcuts` set up global accelerator keys.

- **`ContextMenuManager`**:  
  - Simplifies the process of attaching the context menu to a widget and handling different triggers (mouse or keyboard).

## Example Usage

The sample code provided in the main block (`if __name__ == "__main__":`) shows how to initialize a Tkinter application, create a button to trigger the context menu, attach the menu with items, and provide UI controls to change the animation type and theme.

---
