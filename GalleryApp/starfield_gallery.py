# ════════════════════════════════════════════════════════════
#   starfield_intelligent_gallery — v0.9.0 (Pre-release / Beta)
#
#   Author: Mark J. Latsha
#   Co-Author: Copilot (Microsoft)
#
#   Location: Brentwood, CA 94513
#   Contact: <your email here> | <your phone here>
#
#   Copyright © 2026
#
#   Description:
#       The starfield_intelligent_gallery is a modular, offline-first
#       desktop application designed to organize, view, filter,
#       and analyze Starfield screenshots with metadata support,
#       dynamic filtering, modal viewing, slideshow playback,
#       batch operations, and favorites management.
#
#   Modules Included:
#       • starfield_gallery.py (Launcher)
#       • starfield_metadata_inspector.py
#       • starfield_dynamic_filter.py
#       • starfield_modal_view.py
#       • starfield_hotkey_overlay.py
#       • starfield_filter_bar.py
#       • starfield_xmp_parser.py
#       • starfield_slideshow.py
#       • starfield_batch_ops.py
#       • starfield_holo_effects.py
#       • starfield_favorites.py
#
#   Notes:
#       Replace the placeholder contact information above with
#       your real email and phone number for your private copy.
#       Do NOT publish personal contact info publicly.
# ════════════════════════════════════════════════════════════

# =============================================================================
#  starfield_gallery.py  —  starfield_intelligent_gallery  —  Master Launcher
#  v0.9.0 (Pre-release / Beta)
# =============================================================================
#
#  REQUIRED COMPANION FILES (all go in the same GalleryApp\ folder):
#   starfield_metadata_inspector.py
#   starfield_dynamic_filter.py
#   starfield_modal_view.py
#   starfield_hotkey_overlay.py
#   starfield_filter_bar.py
#   starfield_xmp_parser.py
#   starfield_slideshow.py
#   starfield_batch_ops.py
#   starfield_holo_effects.py
#   starfield_favorites.py
#
#  INSTALL REQUIREMENTS:
#   pip install Pillow exifread keyboard
#   (keyboard module requires running as Administrator)
#
#  DEFAULT PHOTO PATH:
#   Documents\My Games\Starfield\Data\Textures\Photos
# =============================================================================

# ============================
# starfield_gallery.py
# Full Dream Build — Chunk 1
# ============================

import os
import sys
import json
import time
import threading
from dataclasses import dataclass, field
from typing import List, Optional, Dict, Tuple

import tkinter as tk
from tkinter import ttk, filedialog, messagebox

try:
    from PIL import Image, ImageTk
except ImportError:
    raise SystemExit(
        "This app requires Pillow.\n\nInstall with:\n    pip install pillow"
    )

# ---------- Constants ----------

APP_TITLE = "starfield_intelligent_gallery"
APP_VERSION = "1.0 Full Dream Build"

SUPPORTED_EXTENSIONS = {".png", ".jpg", ".jpeg", ".bmp", ".tga", ".webp"}

DEFAULT_SLIDESHOW_INTERVAL_SEC = 4.0
MIN_SLIDESHOW_INTERVAL_SEC = 1.0
MAX_SLIDESHOW_INTERVAL_SEC = 30.0
FAVORITES_FILENAME = "favorites.json"


THUMBNAIL_SIZE = (320, 180)
GRID_COLUMNS = 4

METADATA_FILE_SUFFIX = ".json"  # e.g., image.png.json

# Keyboard shortcuts (for reference)
#   Left / Right arrows : previous / next image
#   Space               : toggle slideshow
#   S                   : start slideshow
#   P                   : pause slideshow
#   +/-                 : adjust slideshow speed
#   F                   : toggle fullscreen
#   Esc                 : exit fullscreen / quit if not fullscreen


# ---------- Data classes ----------

@dataclass
class StarfieldImage:
    path: str
    thumbnail: Optional[ImageTk.PhotoImage] = None
    width: int = 0
    height: int = 0
    metadata: Dict[str, str] = field(default_factory=dict)
    is_favorite: bool = False

    def filename(self) -> str:
        return os.path.basename(self.path)

    def stem(self) -> str:
        name, _ = os.path.splitext(self.filename())
        return name

class FavoriteManager:
    """
    Manages favorites.json in the current root folder.
    Ensures only valid, existing image paths are stored.
    """

    def __init__(self, root_folder: str):
        self.root_folder = os.path.abspath(root_folder)
        self.favorites: set[str] = set()
        self._load()

    def _favorites_path(self) -> str:
        return os.path.join(self.root_folder, FAVORITES_FILENAME)

    def _load(self) -> None:
        path = self._favorites_path()
        if not os.path.isfile(path):
            return
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
            items = data.get("favorites", [])
            for p in items:
                if isinstance(p, str) and os.path.isfile(p):
                    self.favorites.add(os.path.normpath(p))
        except Exception:
            # If favorites.json is bad, we ignore it rather than crash.
            self.favorites.clear()

    def save(self) -> None:
        path = self._favorites_path()
        data = {"favorites": sorted(self.favorites)}
        try:
            with open(path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)
        except Exception:
            # Never let favorites saving kill the app.
            pass

    def is_favorite(self, path: str) -> bool:
        return os.path.normpath(path) in self.favorites

    def add(self, path: str) -> None:
        path = os.path.normpath(path)
        if os.path.isfile(path):
            self.favorites.add(path)
            self.save()

    def remove(self, path: str) -> None:
        path = os.path.normpath(path)
        if path in self.favorites:
            self.favorites.remove(path)
            self.save()


@dataclass
class GalleryConfig:
    root_folder: str
    slideshow_interval_sec: float = DEFAULT_SLIDESHOW_INTERVAL_SEC
    fullscreen: bool = False


# ---------- Utility functions ----------

def is_image_file(path: str) -> bool:
    _, ext = os.path.splitext(path)
    return ext.lower() in SUPPORTED_EXTENSIONS

def discover_images(root_folder: str) -> List[str]:
    images: List[str] = []
    for dirpath, _, filenames in os.walk(root_folder):
        for name in filenames:
            full = os.path.join(dirpath, name)
            if is_image_file(full):
                images.append(os.path.normpath(full))
    images.sort()
    return images
def load_metadata_for_image(image_path: str) -> Dict[str, str]:
    """
    Looks for a sidecar JSON file next to the image:
        image.png  -> image.png.json
    Returns a dict of metadata fields if found, else {}.
    """
    meta_path = image_path + METADATA_FILE_SUFFIX
    if not os.path.isfile(meta_path):
        return {}

    try:
        with open(meta_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        if isinstance(data, dict):
            # Ensure all values are strings for display
            return {str(k): str(v) for k, v in data.items()}
        return {}
    except Exception:
        return {}

def human_size(num_bytes: int) -> str:
    units = ["B", "KB", "MB", "GB", "TB"]
    size = float(num_bytes)
    for unit in units:
        if size < 1024.0:
            return f"{size:.1f} {unit}"
        size /= 1024.0
    return f"{size:.1f} PB"
# ============================
# Full Dream Build — Chunk 2
# UI construction
# ============================

class StarfieldGalleryApp:
    def __init__(self, root: tk.Tk, config: GalleryConfig):
        self.root = root
        self.config = config

        self.root.title(f"{APP_TITLE} — {APP_VERSION}")
        self.root.geometry("1400x900")

        # State
        self.images: List[StarfieldImage] = []
        self.current_index: int = 0
        self.slideshow_running: bool = False
        self.slideshow_thread: Optional[threading.Thread] = None
        self.slideshow_stop_event = threading.Event()

        self.fullscreen: bool = config.fullscreen

        # Caches
        self.thumbnail_cache: Dict[str, ImageTk.PhotoImage] = {}

        # Tk variables
        self.status_var = tk.StringVar(value="Ready.")
        self.slideshow_interval_var = tk.DoubleVar(
            value=self.config.slideshow_interval_sec
        )

        # Build UI
        self._build_layout()
        self._bind_shortcuts()

        # Load images
        self._load_images_from_folder(self.config.root_folder)

        # Initial selection
        if self.images:
            self._select_image(0)
        else:
            self._set_status("No images found. Use File → Open Folder to choose another.")

    # ---------- Layout ----------

    def _build_layout(self) -> None:
        self.root.rowconfigure(0, weight=1)
        self.root.columnconfigure(0, weight=1)

        # Main container
        self.main_frame = ttk.Frame(self.root)
        self.main_frame.grid(row=0, column=0, sticky="nsew")
        self.main_frame.rowconfigure(0, weight=1)
        self.main_frame.columnconfigure(0, weight=3)
        self.main_frame.columnconfigure(1, weight=2)

        # Left: grid of thumbnails
        self.grid_frame = ttk.Frame(self.main_frame, padding=8)
        self.grid_frame.grid(row=0, column=0, sticky="nsew")
        self.grid_frame.rowconfigure(0, weight=1)
        self.grid_frame.columnconfigure(0, weight=1)

        self.canvas = tk.Canvas(self.grid_frame, highlightthickness=0)
        self.canvas.grid(row=0, column=0, sticky="nsew")

        self.grid_scrollbar = ttk.Scrollbar(
            self.grid_frame, orient="vertical", command=self.canvas.yview
        )
        self.grid_scrollbar.grid(row=0, column=1, sticky="ns")

        self.canvas.configure(yscrollcommand=self.grid_scrollbar.set)

        self.grid_inner = ttk.Frame(self.canvas)
        self.canvas.create_window((0, 0), window=self.grid_inner, anchor="nw")

        self.grid_inner.bind("<Configure>", self._on_grid_configure)

        # Right: metadata + preview
        self.side_frame = ttk.Frame(self.main_frame, padding=8)
        self.side_frame.grid(row=0, column=1, sticky="nsew")
        self.side_frame.rowconfigure(1, weight=1)
        self.side_frame.columnconfigure(0, weight=1)

        # Top: preview
        self.preview_label = ttk.Label(self.side_frame, text="Preview", anchor="center")
        self.preview_label.grid(row=0, column=0, sticky="ew", pady=(0, 4))

        self.preview_canvas = tk.Canvas(
            self.side_frame, background="black", height=360
        )
        self.preview_canvas.grid(row=1, column=0, sticky="nsew")

        # Metadata panel
        self.metadata_frame = ttk.LabelFrame(self.side_frame, text="Metadata")
        self.metadata_frame.grid(row=2, column=0, sticky="nsew", pady=(8, 0))
        self.metadata_frame.rowconfigure(0, weight=1)
        self.metadata_frame.columnconfigure(0, weight=1)

        self.metadata_text = tk.Text(
            self.metadata_frame,
            wrap="word",
            height=12,
            state="disabled",
            font=("Consolas", 9),
        )
        self.metadata_text.grid(row=0, column=0, sticky="nsew")

        self.metadata_scrollbar = ttk.Scrollbar(
            self.metadata_frame, orient="vertical", command=self.metadata_text.yview
        )
        self.metadata_scrollbar.grid(row=0, column=1, sticky="ns")
        self.metadata_text.configure(yscrollcommand=self.metadata_scrollbar.set)

        # Bottom: controls + status
        self.bottom_frame = ttk.Frame(self.root, padding=(8, 4))
        self.bottom_frame.grid(row=1, column=0, sticky="ew")
        self.bottom_frame.columnconfigure(0, weight=1)
        self.bottom_frame.columnconfigure(1, weight=0)

        # Slideshow controls
        self.controls_frame = ttk.Frame(self.bottom_frame)
        self.controls_frame.grid(row=0, column=0, sticky="w")

        self.btn_prev = ttk.Button(
            self.controls_frame, text="⟨ Prev", command=self.show_previous_image
        )
        self.btn_prev.grid(row=0, column=0, padx=(0, 4))

        self.btn_next = ttk.Button(
            self.controls_frame, text="Next ⟩", command=self.show_next_image
        )
        self.btn_next.grid(row=0, column=1, padx=(0, 12))

        self.btn_slideshow = ttk.Button(
            self.controls_frame, text="Start Slideshow", command=self.toggle_slideshow
        )
        self.btn_slideshow.grid(row=0, column=2, padx=(0, 12))

        ttk.Label(self.controls_frame, text="Interval (sec):").grid(
            row=0, column=3, padx=(0, 4)
        )
        self.interval_spin = ttk.Spinbox(
            self.controls_frame,
            from_=MIN_SLIDESHOW_INTERVAL_SEC,
            to=MAX_SLIDESHOW_INTERVAL_SEC,
            increment=1.0,
            textvariable=self.slideshow_interval_var,
            width=5,
            command=self._on_interval_changed,
        )
        self.interval_spin.grid(row=0, column=4, padx=(0, 12))

        self.btn_fullscreen = ttk.Button(
            self.controls_frame, text="Toggle Fullscreen", command=self.toggle_fullscreen
        )
        self.btn_fullscreen.grid(row=0, column=5, padx=(0, 12))

        # Status bar
        self.status_label = ttk.Label(
            self.bottom_frame, textvariable=self.status_var, anchor="e"
        )
        self.status_label.grid(row=0, column=1, sticky="e")

        # Menu
        self._build_menu()

    def _build_menu(self) -> None:
        menubar = tk.Menu(self.root)

        file_menu = tk.Menu(menubar, tearoff=False)
        file_menu.add_command(label="Open Folder…", command=self._menu_open_folder)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.quit)
        menubar.add_cascade(label="File", menu=file_menu)

        view_menu = tk.Menu(menubar, tearoff=False)
        view_menu.add_command(
            label="Toggle Fullscreen (F)", command=self.toggle_fullscreen
        )
        menubar.add_cascade(label="View", menu=view_menu)

        slideshow_menu = tk.Menu(menubar, tearoff=False)
        slideshow_menu.add_command(
            label="Start Slideshow (S)", command=self.start_slideshow
        )
        slideshow_menu.add_command(
            label="Pause Slideshow (P)", command=self.pause_slideshow
        )
        menubar.add_cascade(label="Slideshow", menu=slideshow_menu)

        help_menu = tk.Menu(menubar, tearoff=False)
        help_menu.add_command(label="About", command=self._menu_about)
        menubar.add_cascade(label="Help", menu=help_menu)

        self.root.config(menu=menubar)

    # ---------- Shortcuts ----------

    def _bind_shortcuts(self) -> None:
        self.root.bind("<Left>", lambda e: self.show_previous_image())
        self.root.bind("<Right>", lambda e: self.show_next_image())
        self.root.bind("<space>", lambda e: self.toggle_slideshow())
        self.root.bind("<s>", lambda e: self.start_slideshow())
        self.root.bind("<p>", lambda e: self.pause_slideshow())
        self.root.bind("<plus>", lambda e: self._adjust_interval(-1))
        self.root.bind("<minus>", lambda e: self._adjust_interval(+1))
        self.root.bind("<KeyPress-=>", lambda e: self._adjust_interval(-1))  # '+' on US
        self.root.bind("<KeyPress-_>", lambda e: self._adjust_interval(+1))  # '_' on US
        self.root.bind("<f>", lambda e: self.toggle_fullscreen())
        self.root.bind("<Escape>", lambda e: self._on_escape())

    # ---------- Status ----------

    def _set_status(self, text: str) -> None:
        self.status_var.set(text)
        self.status_label.update_idletasks()
# ============================
# Full Dream Build — Chunk 3
# Grid, events, metadata, slideshow
# ============================

    # ---------- Image loading ----------

    def _load_images_from_folder(self, folder: str) -> None:
        folder = os.path.abspath(folder)
        if not os.path.isdir(folder):
            messagebox.showerror("Folder not found", f"Folder does not exist:\n{folder}")
            return

        self._set_status(f"Scanning for images in: {folder}")
        paths = discover_images(folder)

        # Initialize favorites for this folder

        self.images.clear()
        self.thumbnail_cache.clear()
        self.favorite_manager = FavoriteManager(folder)

        for p in paths:
            meta = load_metadata_for_image(p)
            is_fav = (
                self.favorite_manager.is_favorite(p)
                if self.favorite_manager is not None
                else False
            )
            self.images.append(
                StarfieldImage(path=p, metadata=meta, is_favorite=is_fav)
            )

        self._build_grid()
        self._set_status(f"Loaded {len(self.images)} images from {folder}")


    # ---------- Grid of thumbnails ----------

    def _build_grid(self) -> None:
        # Clear existing widgets
        for child in self.grid_inner.winfo_children():
            child.destroy()

        if not self.images:
            ttk.Label(self.grid_inner, text="No images found.").grid(
                row=0, column=0, padx=8, pady=8
            )
            return

        for idx, img in enumerate(self.images):
            row = idx // GRID_COLUMNS
            col = idx % GRID_COLUMNS

            thumb = self._get_thumbnail(img.path)
            img.thumbnail = thumb

            btn = ttk.Button(
                self.grid_inner,
                image=thumb,
                command=lambda i=idx: self._select_image(i),
            )
            btn.grid(row=row, column=col, padx=4, pady=4, sticky="nsew")

            # Optional: filename label under each thumbnail
            lbl = ttk.Label(self.grid_inner, text=img.stem(), anchor="center")
            lbl.grid(row=row + 1, column=col, padx=4, pady=(0, 8))

        # Make columns expand evenly
        for c in range(GRID_COLUMNS):
            self.grid_inner.columnconfigure(c, weight=1)

        self.grid_inner.update_idletasks()
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def _on_grid_configure(self, event) -> None:
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def _get_thumbnail(self, path: str) -> ImageTk.PhotoImage:
        if path in self.thumbnail_cache:
            return self.thumbnail_cache[path]

        try:
            img = Image.open(path)
            img.thumbnail(THUMBNAIL_SIZE, Image.LANCZOS)
            thumb = ImageTk.PhotoImage(img)
            self.thumbnail_cache[path] = thumb
            return thumb
        except Exception:
            # Fallback: simple placeholder
            placeholder = Image.new("RGB", THUMBNAIL_SIZE, color=(40, 40, 40))
            thumb = ImageTk.PhotoImage(placeholder)
            self.thumbnail_cache[path] = thumb
            return thumb

    # ---------- Selection & preview ----------

    def _select_image(self, index: int) -> None:
        if not self.images:
            return
        index = max(0, min(index, len(self.images) - 1))
        self.current_index = index
        img = self.images[index]

        self._update_preview(img)
        self._update_metadata_panel(img)

        self._set_status(
            f"{index + 1}/{len(self.images)} — {img.filename()}"
        )

    def _update_preview(self, img: StarfieldImage) -> None:
        try:
            pil = Image.open(img.path)
            img.width, img.height = pil.size

            # Fit into preview_canvas
            canvas_w = self.preview_canvas.winfo_width() or 800
            canvas_h = self.preview_canvas.winfo_height() or 360

            scale = min(canvas_w / img.width, canvas_h / img.height, 1.0)
            new_w = int(img.width * scale)
            new_h = int(img.height * scale)

            pil_resized = pil.resize((new_w, new_h), Image.LANCZOS)
            self.preview_image_tk = ImageTk.PhotoImage(pil_resized)

            self.preview_canvas.delete("all")
            x = (canvas_w - new_w) // 2
            y = (canvas_h - new_h) // 2
            self.preview_canvas.create_image(x, y, anchor="nw", image=self.preview_image_tk)
        except Exception as e:
            self.preview_canvas.delete("all")
            self.preview_canvas.create_text(
                10,
                10,
                anchor="nw",
                text=f"Error loading image:\n{e}",
                fill="white",
            )

    def _update_metadata_panel(self, img: StarfieldImage) -> None:
        self.metadata_text.configure(state="normal")
        self.metadata_text.delete("1.0", "end")

        # Basic file info
        try:
            stat = os.stat(img.path)
            size_str = human_size(stat.st_size)
        except Exception:
            size_str = "Unknown"

        lines = [
            f"File: {img.filename()}",
            f"Path: {img.path}",
            f"Size: {size_str}",
            f"Resolution: {img.width} x {img.height}",
            "",
        ]

        if img.metadata:
            lines.append("Metadata:")
            for k, v in sorted(img.metadata.items()):
                lines.append(f"  {k}: {v}")
        else:
            lines.append("No sidecar metadata found.")

        self.metadata_text.insert("1.0", "\n".join(lines))
        self.metadata_text.configure(state="disabled")

    # ---------- Navigation ----------

    def show_next_image(self) -> None:
        if not self.images:
            return
        new_index = (self.current_index + 1) % len(self.images)
        self._select_image(new_index)

    def show_previous_image(self) -> None:
        if not self.images:
            return
        new_index = (self.current_index - 1) % len(self.images)
        self._select_image(new_index)

    # ---------- Slideshow ----------

    def _on_interval_changed(self) -> None:
        try:
            val = float(self.slideshow_interval_var.get())
        except Exception:
            val = DEFAULT_SLIDESHOW_INTERVAL_SEC
        val = max(MIN_SLIDESHOW_INTERVAL_SEC, min(MAX_SLIDESHOW_INTERVAL_SEC, val))
        self.slideshow_interval_var.set(val)
        self.config.slideshow_interval_sec = val
        self._set_status(f"Slideshow interval set to {val:.1f} sec")

    def _adjust_interval(self, delta: int) -> None:
        val = float(self.slideshow_interval_var.get())
        val += delta
        val = max(MIN_SLIDESHOW_INTERVAL_SEC, min(MAX_SLIDESHOW_INTERVAL_SEC, val))
        self.slideshow_interval_var.set(val)
        self._on_interval_changed()

    def start_slideshow(self) -> None:
        if self.slideshow_running or not self.images:
            return
        self.slideshow_running = True
        self.slideshow_stop_event.clear()
        self.btn_slideshow.configure(text="Pause Slideshow")
        self._set_status("Slideshow started.")
        self.slideshow_thread = threading.Thread(
            target=self._slideshow_loop, daemon=True
        )
        self.slideshow_thread.start()

    def pause_slideshow(self) -> None:
        if not self.slideshow_running:
            return
        self.slideshow_running = False
        self.slideshow_stop_event.set()
        self.btn_slideshow.configure(text="Start Slideshow")
        self._set_status("Slideshow paused.")

    def toggle_slideshow(self) -> None:
        if self.slideshow_running:
            self.pause_slideshow()
        else:
            self.start_slideshow()

    def _slideshow_loop(self) -> None:
        while not self.slideshow_stop_event.is_set():
            interval = float(self.slideshow_interval_var.get())
            time.sleep(interval)
            if self.slideshow_stop_event.is_set():
                break
            # Move to next image on the main thread
            self.root.after(0, self.show_next_image)

    # ---------- Fullscreen & escape ----------

    def toggle_fullscreen(self) -> None:
        self.fullscreen = not self.fullscreen
        self.root.attributes("-fullscreen", self.fullscreen)
        if self.fullscreen:
            self._set_status("Entered fullscreen (Esc to exit).")
        else:
            self._set_status("Exited fullscreen.")

    def _on_escape(self) -> None:
        if self.fullscreen:
            self.toggle_fullscreen()
        else:
            self.root.quit()

    # ---------- Menus ----------

    def _menu_open_folder(self) -> None:
        folder = filedialog.askdirectory(
            title="Select Starfield screenshots folder",
            initialdir=self.config.root_folder or os.getcwd(),
        )
        if not folder:
            return
        self.config.root_folder = folder
        self._load_images_from_folder(folder)
        if self.images:
            self._select_image(0)

    def _menu_about(self) -> None:
        messagebox.showinfo(
            "About",
            f"{APP_TITLE}\n"
            f"Version: {APP_VERSION}\n\n"
            "Starfield-inspired image gallery with slideshow,\n"
            "metadata sidecar support, and keyboard shortcuts.\n\n"
            "Controls:\n"
            "  Left / Right : Previous / Next image\n"
            "  Space        : Toggle slideshow\n"
            "  S / P        : Start / Pause slideshow\n"
            "  +/-          : Adjust slideshow speed\n"
            "  F            : Toggle fullscreen\n"
            "  Esc          : Exit fullscreen / Quit",
        )
# ============================
# Full Dream Build — Chunk 4
# Launchers + entry point
# ============================

def parse_args(argv: List[str]) -> GalleryConfig:
    """
    Very lightweight argument handling:
      python starfield_gallery.py [root_folder] [--fullscreen] [--interval=SECONDS]
    """
    root_folder = os.getcwd()
    fullscreen = False
    interval = DEFAULT_SLIDESHOW_INTERVAL_SEC

    for arg in argv[1:]:
        if arg == "--fullscreen":
            fullscreen = True
        elif arg.startswith("--interval="):
            try:
                interval = float(arg.split("=", 1)[1])
            except Exception:
                interval = DEFAULT_SLIDESHOW_INTERVAL_SEC
        else:
            # First non-flag argument is treated as folder
            root_folder = arg

    return GalleryConfig(
        root_folder=root_folder,
        slideshow_interval_sec=interval,
        fullscreen=fullscreen,
    )


def main(argv: Optional[List[str]] = None) -> int:
    if argv is None:
        argv = sys.argv

    config = parse_args(argv)

    root = tk.Tk()
    app = StarfieldGalleryApp(root, config)

    try:
        root.mainloop()
    finally:
        # Ensure slideshow thread stops
        app.slideshow_stop_event.set()

    return 0


if __name__ == "__main__":
    raise SystemExit(main())