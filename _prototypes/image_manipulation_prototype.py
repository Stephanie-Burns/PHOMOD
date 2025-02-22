import tkinter as tk
from tkinter import filedialog, ttk
from PIL import Image, ImageTk


class ImageViewerWidget(tk.Frame):
    """
    A portable image viewer widget that supports file picking.
    The widget now dynamically resizes while maintaining aspect ratio.
    """

    def __init__(self, parent, border=2, **kwargs):
        super().__init__(parent, **kwargs)
        self.image_path = None
        self.tk_image = None  # Store the image reference

        # Create a resizable container frame
        self.image_frame = ttk.Frame(self, relief="ridge", borderwidth=border)
        self.image_frame.pack(fill="both", expand=True)

        # Create a label that will display the image
        self.image_label = tk.Label(
            self.image_frame,
            text="Select Image",
            fg="white", bg="gray",
            font=("Arial", 14),
            relief="raised",
            borderwidth=border
        )
        self.image_label.pack(fill="both", expand=True)

        # Enable file picker on click
        self.image_label.bind("<Button-1>", self.select_file)

        # Handle resizing dynamically
        self.image_frame.bind("<Configure>", self.resize_image)

    def select_file(self, event=None):
        """Opens a file dialog to let the user pick an image file."""
        file_path = filedialog.askopenfilename(
            filetypes=[("Image Files", "*.png *.PNG *.jpg *.JPG *.jpeg *.JPEG *.bmp *.BMP *.gif *.GIF")]
        )
        if file_path:
            self.image_path = file_path  # Store selected file path
            self.resize_image()

    def resize_image(self, event=None):
        """Resizes the image to fit the container while maintaining aspect ratio."""
        if not self.image_path:
            return

        try:
            img = Image.open(self.image_path)
            max_width = self.image_frame.winfo_width()
            max_height = self.image_frame.winfo_height()

            if max_width > 1 and max_height > 1:  # Ensure valid dimensions
                img_width, img_height = img.size
                scale_factor = min(max_width / img_width, max_height / img_height)
                new_width = int(img_width * scale_factor)
                new_height = int(img_height * scale_factor)

                img = img.resize((new_width, new_height), Image.LANCZOS)
                self.tk_image = ImageTk.PhotoImage(img)
                self.image_label.config(image=self.tk_image, text="")
        except Exception as e:
            print(f"Error loading image: {e}")
