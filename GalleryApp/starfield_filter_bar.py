# ============================================================
# starfield_intelligent_gallery — Filter Bar UI
# Author: Mark J. Latsha
# Location: Brentwood, CA 94513
# Email: Latsha2031@gmail.com
# Phone: 1-510-209-6474
#
# Description:
#   Provides search + favorites toggle UI.
#   Updates the DynamicFilter engine in real time.
#   Updated version aligned with starfield_gallery.py.
# ============================================================

import tkinter as tk

class FilterBar:
    """
    A simple UI bar for search + favorites toggle.
    """

    def __init__(self, root, filter_engine, on_change):
        self.root = root
        self.filter_engine = filter_engine
        self.on_change = on_change

        frame = tk.Frame(root, bg="#222222")
        frame.pack(fill="x")

        # --- Search box ---
        tk.Label(frame, text="Search:", fg="white", bg="#222222").pack(side="left", padx=5)
        self.search_entry = tk.Entry(frame, width=30)
        self.search_entry.pack(side="left", padx=5)
        self.search_entry.bind("<KeyRelease>", self._update)

        # --- Favorites toggle ---
        self.fav_var = tk.IntVar()
        fav_check = tk.Checkbutton(
            frame,
            text="Favorites Only",
            variable=self.fav_var,
            command=self._update,
            fg="white",
            bg="#222222",
            selectcolor="#333333"
        )
        fav_check.pack(side="left", padx=10)

    def _update(self, event=None):
        """
        Pushes UI changes into the filter engine.
        """
        self.filter_engine.search_text = self.search_entry.get()
        self.filter_engine.only_favorites = bool(self.fav_var.get())
        self.on_change()
