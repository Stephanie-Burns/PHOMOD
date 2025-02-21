import tkinter as tk
from tkinter import ttk

class ScrollableFrameDemo(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("Scrollable Frame Demo")
        self.geometry("400x400")

        container = tk.Frame(self)
        container.pack(fill=tk.BOTH, expand=True)

        self.canvas = tk.Canvas(container, borderwidth=0, highlightthickness=0)
        self.vsb = tk.Scrollbar(container, orient="vertical", command=self.canvas.yview)
        self.canvas.configure(yscrollcommand=self.vsb.set)

        self.vsb.pack(side="right", fill="y")
        self.canvas.pack(side="left", fill=tk.BOTH, expand=True)

        self.inner_frame = tk.Frame(self.canvas)
        self.inner_window = self.canvas.create_window((0, 0), window=self.inner_frame, anchor="nw")

        self.inner_frame.bind("<Configure>", self._on_frame_configure)
        self.canvas.bind("<Configure>", self._on_canvas_configure)

        for i in range(5):
            lf = ttk.LabelFrame(self.inner_frame, text=f"Section {i+1}")
            lf.pack(fill="x", padx=10, pady=5, expand=True)
            for j in range(5):
                tk.Button(lf, text=f"Button {i*5+j+1}").pack(padx=5, pady=5, fill="x")

        # Bind mouse wheel events
        self.inner_frame.bind("<Enter>", lambda e: self._bind_mousewheel())
        self.inner_frame.bind("<Leave>", lambda e: self._unbind_mousewheel())

        self._bind_mousewheel()

    def _on_frame_configure(self, event):
        """Adjusts scroll region when the inner frame is resized."""
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def _on_canvas_configure(self, event):
        """Ensures the inner frame width matches the canvas width."""
        self.canvas.itemconfig(self.inner_window, width=event.width)

    def _bind_mousewheel(self):
        """Binds mouse wheel scrolling to the canvas and all widgets inside inner_frame."""
        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)  # Windows/macOS
        self.canvas.bind_all("<Button-4>", self._on_mousewheel)  # Linux (scroll up)
        self.canvas.bind_all("<Button-5>", self._on_mousewheel)  # Linux (scroll down)

        # Bind mouse wheel event to all child widgets inside the frame
        for widget in self.inner_frame.winfo_children():
            widget.bind("<Enter>", lambda e: self._bind_mousewheel())
            widget.bind("<Leave>", lambda e: self._unbind_mousewheel())

    def _unbind_mousewheel(self):
        """Disables mouse wheel scrolling when the mouse leaves the frame."""
        self.canvas.unbind_all("<MouseWheel>")
        self.canvas.unbind_all("<Button-4>")
        self.canvas.unbind_all("<Button-5>")

    def _on_mousewheel(self, event):
        """Handles the mouse wheel scrolling."""
        if event.num == 5 or event.delta < 0:  # Scroll down
            self.canvas.yview_scroll(1, "units")
        elif event.num == 4 or event.delta > 0:  # Scroll up
            self.canvas.yview_scroll(-1, "units")


if __name__ == "__main__":
    app = ScrollableFrameDemo()
    app.mainloop()
