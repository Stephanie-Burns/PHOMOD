Below is an updated version of your API documentation in Markdown. It includes details on the new configuration options (including the spacing between the icon and the title, as well as the title and the accelerator) along with usage examples and explanations of each part of the API. You can include this documentation in your project to help other developers—and your future self—understand and use the context menu effectively.

---

# Context Menu API Documentation

## Overview

The Context Menu API provides an advanced, animated context menu for Tkinter applications. It supports multiple animation styles (fade, slide, bounce), keyboard navigation, accelerator (shortcut) bindings, and automatic closing when clicking outside or when focus is lost. The API is implemented using two main classes:

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

## Configuration

The behavior and appearance of the context menu are controlled by a configuration class (`ContextMenuConfig`). This class is implemented as a dataclass and includes detailed docstrings for each attribute, which helps with IDE auto-completion and documentation generation.

### Example Configuration Class

```python
from dataclasses import dataclass, field
from typing import List

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
```

You can create a configuration instance and customize it as needed:

```python
config = ContextMenuConfig(
    menu_padding=12,
    item_spacing=8,
    title_accelerator_spacing=10,
    icon_title_spacing=8,
    border_color="#444444",
    highlight_color="#EEEEEE",
    separator_color="#CCCCCC",
    default_animation="slide",
    fade_duration=25,
    slide_distance=40,
    bounce_heights=[0, -6, -12, -6, 0],
    shadow_effect=True
)
```

## Using the ContextMenu

### Creating and Attaching a Context Menu

1. **Instantiate a ContextMenuManager:**
   
   In your main application, create an instance of `ContextMenuManager` by passing it the parent widget (typically your `tk.Tk` instance) along with the configuration object.

   ```python
   cm = ContextMenuManager(root, config)
   ```

2. **Define Menu Items:**

   Menu items are defined using tuples (or you can update them to use a dataclass for even clearer type hints). Each item follows this format:

   ```python
   (label, command, icon_path, unused_placeholder, shortcut)
   ```

   - **`label`**: The text to display (use `"---"` for a separator).
   - **`command`**: A function to execute when the item is selected.
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

   Use the `attach` method of `ContextMenuManager` to bind the context menu to a widget. The menu will be triggered via right-click, the Menu key, or Shift+F10.

   ```python
   button = ttk.Button(root, text="Right Click or Press Menu Key")
   button.pack(pady=50, padx=50)
   cm.attach(button, menu_items)
   ```

### Animation Styles

The context menu supports three animation types:
- **Fade**: The menu gradually changes its opacity from 0 to 1 (or vice versa when hiding).
- **Slide**: The menu slides in from a horizontal offset.
- **Bounce**: The menu appears with a vertical “bounce” effect.

You can select an animation type via a UI control (such as a combobox) and update the menu’s `animation_type` property.

```python
animation_var = tk.StringVar(value="fade")
animation_options = ["fade", "slide", "bounce"]
animation_menu = ttk.Combobox(root, textvariable=animation_var,
                              values=animation_options, state="readonly")
animation_menu.pack()

def update_animation():
    new_animation = animation_var.get()
    cm.menu.animation_type = new_animation

apply_animation_button = ttk.Button(root, text="Apply Animation", command=update_animation)
apply_animation_button.pack(pady=10)
```

### Accelerator (Shortcut) Bindings

- Specify a shortcut string (e.g., `"<Control-c>"`) when defining menu items.
- The API automatically binds these shortcuts using `bind_all` so that pressing the key combination triggers the associated command and closes the menu.
- To disable or re-enable accelerator bindings at runtime:

  ```python
  cm.menu.disable_shortcut_bindings()
  cm.menu.enable_shortcut_bindings()
  ```

### Keyboard Navigation

- **Up/Down arrows**: Navigate through menu items.
- **Return (Enter)**: Activate the currently highlighted item.
- **Escape**: Closes the menu.
- The menu automatically closes if focus is lost or if a click occurs outside its area.

## Customization and Theming

The context menu can be extensively customized via the configuration class:

- **Styling Options:**
  - **`menu_padding`**: Controls the padding inside the menu.
  - **`item_spacing`**: Adjusts the spacing between menu items.
  - **`title_accelerator_spacing`**: Adjusts the horizontal spacing between the title and the shortcut.
  - **`icon_title_spacing`**: Adjusts the horizontal spacing between the icon and the title.
  - **`border_color`**, **`highlight_color`**, and **`separator_color`**: Control the appearance of borders, hover backgrounds, and separators.
  
- **Animation Settings:**
  - **`default_animation`**: The default animation style.
  - **`fade_duration`**, **`slide_distance`**, and **`bounce_heights`**: Adjust the parameters for the fade, slide, and bounce animations.
  
- **Shadow Effect:**
  - **`shadow_effect`**: Enables a subtle drop shadow for added visual depth.

### Theming with ttk.Style

The `_init_styles` method within the `ContextMenu` class sets up styles for the menu container and its items based on the current theme. This method can be modified if you wish to customize the look further or use a different theme than the default `"clam"`.

## Debugging

- Debug messages are managed via a global `DEBUG` flag.
- To enable or disable debug output, set `DEBUG = True` or `False` at the top of the module.
- Debug output includes:
  - Which animation branch is running.
  - The current alpha value during fade animations.
  - Step counts for slide and bounce animations.
  - Binding information for accelerator keys and outside click handling.

## Code Structure Summary

- **`ContextMenu`**:  
  - **Initialization**: Sets up the Toplevel window, styling, and keyboard bindings.  
  - **Animation Methods**: Methods like `_fade_in`, `_fade_out`, `_slide_in`, and `_bounce_in` control how the menu appears and disappears.  
  - **Outside Click and Focus Handling**: Methods (`_bind_outside_click`, `_on_click_outside`, `_check_focus`) ensure the menu closes appropriately.  
  - **Menu Population and Navigation**: Methods (`_populate_menu`, `_navigate_up`, `_navigate_down`, `_select_item`) create menu items and support keyboard navigation.  
  - **Accelerator Bindings**: Methods (`_bind_shortcuts` and `_unbind_shortcuts`) manage global keyboard shortcuts.

- **`ContextMenuManager`**:  
  - Simplifies attaching the context menu to widgets and handling multiple triggers (mouse and keyboard).

## Example Usage

Below is a simple example showing how to initialize a Tkinter application, create a button to trigger the context menu, attach the menu with items, and provide UI controls to change animation and theme settings.

```python
import tkinter as tk
from tkinter import ttk

# Assume the ContextMenu, ContextMenuManager, and ContextMenuConfig classes are imported

def copy_function():
    print("Copying...")

def paste_function():
    print("Pasting...")

def theme_toggle():
    new_theme = "alt" if ttk.Style().theme_use() == "clam" else "clam"
    ttk.Style().theme_use(new_theme)
    cm.menu._init_styles()
    print("Theme toggled.")

# Define menu items
menu_items = [
    ("Copy", copy_function, "global.png", None, "<Control-c>"),
    ("Paste", paste_function, "paste.png", None, "<Control-v>"),
    ("---", None, None, None, None),
    ("Exit", root.quit, "exit.png", None, "<Alt-F4>"),
]

# Initialize main Tkinter window
root = tk.Tk()
root.geometry("400x300")
root.title("Advanced Context Menu Demo")
style = ttk.Style()
style.theme_use("clam")

# Create configuration instance and the context menu manager
config = ContextMenuConfig()
cm = ContextMenuManager(root, config)

# Create a button to trigger the context menu
button = ttk.Button(root, text="Right Click or Press Menu Key")
button.pack(pady=50, padx=50)
cm.attach(button, menu_items)

# Animation selection UI
animation_var = tk.StringVar(value="fade")
animation_options = ["fade", "slide", "bounce"]
animation_menu = ttk.Combobox(root, textvariable=animation_var,
                              values=animation_options, state="readonly")
animation_menu.pack()

def update_animation():
    new_animation = animation_var.get()
    cm.menu.animation_type = new_animation

apply_animation_button = ttk.Button(root, text="Apply Animation", command=update_animation)
apply_animation_button.pack(pady=10)

# Theme toggle button
theme_button = ttk.Button(root, text="Toggle Theme", command=theme_toggle)
theme_button.pack(pady=20)

root.mainloop()
```

---
