# ============================================================
# starfield_intelligent_gallery — Modal Image Viewer
# Author: Mark J. Latsha
# Location: Brentwood, CA 94513
# Email: Latsha2031@gmail.com
# Phone: 1-510-209-6474
#
# Description:
#   Displays a full-screen modal view of a selected image.
#   Updated version aligned with starfield_gallery.py.
# ============================================================

from PIL import Image, ImageTk
import tkinter as tk

class ModalView:
    """
    Displays a full-screen modal view of a selected image.
    """

    def __init__(self, root):
        self.root = root
        self.window = None

    def open(self, filepath):
        """
        Opens the modal viewer with the given image.
        """

        if self.window:
            self.window.destroy()

        self.window = tk.Toplevel(self.root)
        self.window.title("Image Viewer")
        self.window.geometry("1200x800")
        self.window.configure(bg="black")

        # --- Load image ---
        img = Image.open(filepath)
        img.thumbnail((1180, 780))
        tk_img = ImageTk.PhotoImage(img)

        label = tk.Label(self.window, image=tk_img, bg="black")
        label.image = tk_img
        label.pack(expand=True)

        # Close on click
        label.bind("<Button-1>", lambda e: self.window.destroy())
