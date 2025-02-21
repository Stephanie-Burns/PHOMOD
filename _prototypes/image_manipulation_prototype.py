import tkinter as tk
from tkinter import filedialog, ttk
import os
from PIL import Image, ImageTk

class ImageViewerWidget(tk.Frame):
    """
    A portable image viewer widget that supports file picking.
    The widget is fixed in size and scales any loaded image to fit within that area.
    """
    def __init__(self, parent, width=350, height=250, border=2, **kwargs):
        super().__init__(parent, **kwargs)
        self.width = width
        self.height = height

        # Create a fixed-size container frame with a border.
        self.image_frame = ttk.Frame(self, width=self.width, height=self.height, relief="ridge", borderwidth=border)
        self.image_frame.pack(padx=5, pady=5)
        self.image_frame.pack_propagate(0)  # Prevent the frame from resizing to fit its contents

        # Create a label that will display the image.
        self.image_label = tk.Label(
            self.image_frame,
            text="Select Image",
            fg="white", bg="gray",
            font=("Arial", 14),
            relief="raised",  # Gives the label a 3D effect
            borderwidth=border  # Border thickness
        )
        self.image_label.pack(expand=True, fill="both")

        # Enable file picker on click
        self.image_label.bind("<Button-1>", self.select_file)

    def select_file(self, event=None):
        """Opens a file dialog to let the user pick an image file."""
        file_path = filedialog.askopenfilename(
            filetypes=[("Image Files", "*.png *.PNG *.jpg *.JPG *.jpeg *.JPEG *.bmp *.BMP *.gif *.GIF")]
        )
        if file_path:
            self.display_image(file_path)

    def display_image(self, file_path):
        """Loads the image, rescales it to fit the fixed container, and displays it."""
        try:
            img = Image.open(file_path)
            max_width, max_height = self.width, self.height
            img_width, img_height = img.size
            scale_factor = min(max_width / img_width, max_height / img_height)
            new_width = int(img_width * scale_factor)
            new_height = int(img_height * scale_factor)
            img = img.resize((new_width, new_height), Image.LANCZOS)
            self.tk_image = ImageTk.PhotoImage(img)
            self.image_label.config(image=self.tk_image, text="")
        except Exception as e:
            print(f"Error loading image: {e}")
