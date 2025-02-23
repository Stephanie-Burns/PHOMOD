import tkinter as tk
from tkinter import ttk
import logging

# Logging Setup
app_logger = logging.getLogger('ScrollDebug')
app_logger.setLevel(logging.DEBUG)
handler = logging.StreamHandler()
handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
app_logger.addHandler(handler)


class ScrollableFrame(tk.Frame):
    """A frame with a vertical scrollbar that scrolls its content."""
    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)

        # Create canvas and scrollbar
        self.canvas = tk.Canvas(self, borderwidth=0, highlightthickness=0, bg="white")
        self.vsb = tk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        self.canvas.configure(yscrollcommand=self.vsb.set)

        self.vsb.pack(side="right", fill="y")
        self.canvas.pack(side="left", fill=tk.BOTH, expand=True)

        # Create inner frame
        self.inner_frame = tk.Frame(self.canvas, bg="lightgray")
        self.inner_window = self.canvas.create_window((0, 0), window=self.inner_frame, anchor="nw")

        # Bind configuration events
        self.inner_frame.bind("<Configure>", self._on_frame_configure)
        self.canvas.bind("<Configure>", self._on_canvas_configure)

        # Bind mouse wheel events to the canvas (global binding)
        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)
        self.canvas.bind_all("<Button-4>", self._on_mousewheel)  # Linux scroll up
        self.canvas.bind_all("<Button-5>", self._on_mousewheel)  # Linux scroll down

    def _on_frame_configure(self, event=None):
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def _on_canvas_configure(self, event):
        self.canvas.itemconfigure(self.inner_window, width=event.width)

    def _on_mousewheel(self, event):
        # For Windows, event.delta is usually a multiple of 120; for Linux, use event.num.
        delta = event.delta
        if delta == 0:
            if event.num == 4:
                delta = 120
            elif event.num == 5:
                delta = -120
        # Normalize to +1 or -1.
        norm = -1 if delta < 0 else 1
        app_logger.debug(f"Canvas scrolling: norm delta = {norm}")
        # Invert the direction by scrolling the opposite.
        self.canvas.yview_scroll(-norm, "units")
        return "break"


class ScrollRedirectMixin:
    """Mixin that redirects mouse wheel events to the nearest scrollable parent's canvas."""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Unbind default scroll behavior at the class level to prevent interference.
        self.unbind_class(self.winfo_class(), "<MouseWheel>")
        self.unbind_class(self.winfo_class(), "<Button-4>")
        self.unbind_class(self.winfo_class(), "<Button-5>")
        # Bind our own handler
        self.bind("<MouseWheel>", self._redirect_mouse_wheel, add="+")
        self.bind("<Button-4>", self._redirect_mouse_wheel, add="+")  # Linux
        self.bind("<Button-5>", self._redirect_mouse_wheel, add="+")

    def _redirect_mouse_wheel(self, event):
        app_logger.debug(f"Scroll event on {self}: num={event.num}, delta={event.delta}")
        # Use a fallback if delta is 0 (Linux might do that)
        delta = event.delta
        if delta == 0:
            if event.num == 4:
                delta = 120
            elif event.num == 5:
                delta = -120
        norm = 1 if delta < 0 else -1

        parent_canvas = self._find_scrollable_parent()
        if parent_canvas:
            app_logger.debug(f"Redirecting scroll to parent canvas: {parent_canvas} by {norm} units")
            parent_canvas.yview_scroll(norm, "units")
            return "break"
        else:
            app_logger.warning(f"No scrollable parent found for {self}")
        return None

    def _find_scrollable_parent(self):
        parent = self.master
        while parent:
            if hasattr(parent, "canvas"):
                return parent.canvas
            parent = parent.master
        return None


class CustomEntry(ttk.Entry, ScrollRedirectMixin):
    """An entry widget that does not scroll itself but redirects scroll events."""
    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)


class CustomComboBox(ttk.Combobox, ScrollRedirectMixin):
    """A combobox that does not change selection on scroll, redirecting scroll events to the parent."""
    def __init__(self, parent, values, *args, **kwargs):
        super().__init__(parent, values=values, state="readonly", *args, **kwargs)
        # Unbind any residual class-level scrolling:
        self.unbind_class("TCombobox", "<MouseWheel>")
        self.bind("<MouseWheel>", self._redirect_mouse_wheel, add="+")
        self.bind("<Button-4>", self._redirect_mouse_wheel, add="+")
        self.bind("<Button-5>", self._redirect_mouse_wheel, add="+")

    # Optionally, override click behavior if needed:
    def _open_dropdown(self, event):
        # Let the dropdown open normally.
        self.event_generate("<Down>")


# ------------------------------ Main Test Window ------------------------------
if __name__ == "__main__":
    root = tk.Tk()
    root.title("Scrollable Frame Test with Scroll Redirect")

    # Create a PanedWindow with resizable panels
    paned_window = ttk.PanedWindow(root, orient=tk.HORIZONTAL)
    paned_window.pack(fill=tk.BOTH, expand=True)

    left_panel = tk.Frame(paned_window, bg="gray", width=150)
    left_label = ttk.Label(left_panel, text="Resizable Panel", background="gray", padding=5)
    left_label.pack(padx=10, pady=10)

    right_panel = tk.Frame(paned_window, bg="white")
    scrollable_frame = ScrollableFrame(right_panel)
    scrollable_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

    # Add test widgets inside the scrollable frame
    for i in range(20):
        CustomEntry(scrollable_frame.inner_frame).pack(pady=3, padx=5, fill=tk.X)
        CustomComboBox(scrollable_frame.inner_frame, values=["Option 1", "Option 2", "Option 3"]).pack(pady=3, padx=5, fill=tk.X)

    paned_window.add(left_panel, weight=1)
    paned_window.add(right_panel, weight=3)

    root.geometry("600x400")
    root.mainloop()
