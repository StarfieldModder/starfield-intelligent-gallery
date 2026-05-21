# ════════════════════════════════════════════════════════════
#   FILE: starfield_favorites.py
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
#       Manages the favorites system for the gallery, including
#       saving, loading, and toggling favorite images using a
#       lightweight local data store.
# ════════════════════════════════════════════════════════════

# ============================================================
# starfield_favorites.py  — COMPLETE v0.9.0
# STARFIELD IMAGE GALLERY — Phase 4 | Persistent Favorites Engine
# Star ratings, favorites.json, quick-filter, grid overlay.
# Developed: May 2026 | Mark — Brentwood, CA
# ============================================================
# INSTALL:   pip install Pillow
# INTEGRATE:
#   from starfield_favorites import (
#       FavoritesManager, StarRatingWidget,
#       FavoritesThumbnail, FavoritesPanel
#   )
# ============================================================

import tkinter as tk
from tkinter import ttk, filedialog
from tkinter import font as tkfont
from pathlib import Path
import json, os, threading
from datetime import datetime

try:
    from PIL import Image, ImageTk, ImageDraw, ImageFont
    PIL_OK = True
except ImportError:
    PIL_OK = False

# ── Palette ──────────────────────────────────────────────
SF_BG           = "#0A0E1A"
SF_PANEL        = "#0D1526"
SF_PANEL_LIGHT  = "#0F2540"
SF_BORDER       = "#1A3A5C"
SF_ACCENT       = "#00B4FF"
SF_ACCENT2      = "#00D4FF"
SF_TEXT         = "#C8D8E8"
SF_ORANGE       = "#FF6B00"
SF_GREEN        = "#00FF9C"
SF_AMBER        = "#FFB300"
SF_RED          = "#FF4444"
SF_DIM          = "#4A6080"
SF_STAR_ON      = "#FFB300"   # filled star
SF_STAR_OFF     = "#2A3A50"   # empty star

IMAGE_EXTS      = {".jpg",".jpeg",".png",".bmp",".gif",".tif",".tiff",".webp"}
SIDECAR_EXT     = ".sfmeta.json"
FAVORITES_FILE  = "favorites.json"
THUMB_W, THUMB_H = 110, 82


def _sidecar_path(img_path: str) -> str:
    return str(Path(img_path).with_suffix("")) + SIDECAR_EXT

def _load_sidecar(img_path: str) -> dict:
    sp = _sidecar_path(img_path)
    if Path(sp).exists():
        try:
            with open(sp, encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return {}

def _save_sidecar(img_path: str, data: dict):
    sp = _sidecar_path(img_path)
    with open(sp, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


# ══════════════════════════════════════════════════════════
#  FAVORITES MANAGER — core persistence engine
# ══════════════════════════════════════════════════════════

class FavoritesManager:
    """
    Manages favorites and star ratings.
    Persists to favorites.json AND merges with sidecar files.

    Usage:
        fm = FavoritesManager(base_dir="/path/to/photos")
        fm.set_favorite("shot001.png", True)
        fm.set_rating("shot001.png", 4)
        favorites = fm.get_all_favorites()
    """

    def __init__(self, base_dir: str = None):
        self._base   = base_dir or str(Path.home() / "Documents" /
                                        "My Games" / "Starfield" /
                                        "Data" / "Textures" / "Photos")
        self._fav_file = str(Path(self._base) / FAVORITES_FILE)
        self._data   = {}   # abs_path → {"favorite": bool, "rating": int, "ts": str}
        self._lock   = threading.Lock()
        self._load()
        self._callbacks = []   # notify listeners on change

    # ── Persistence ──────────────────────────────────────

    def _load(self):
        if Path(self._fav_file).exists():
            try:
                with open(self._fav_file, encoding="utf-8") as f:
                    self._data = json.load(f)
            except Exception:
                self._data = {}

    def _save(self):
        try:
            Path(self._fav_file).parent.mkdir(parents=True, exist_ok=True)
            with open(self._fav_file, "w", encoding="utf-8") as f:
                json.dump(self._data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"[FavoritesManager] Save error: {e}")

    def _notify(self):
        for cb in self._callbacks:
            try:
                cb()
            except Exception:
                pass

    def add_change_listener(self, callback):
        """Register a callback(). Called after any data change."""
        self._callbacks.append(callback)

    # ── Setters ──────────────────────────────────────────

    def set_favorite(self, img_path: str, value: bool):
        key = str(Path(img_path).resolve())
        with self._lock:
            entry = self._data.setdefault(key, {})
            entry["favorite"] = value
            entry["ts"]       = datetime.now().isoformat()
        self._mirror_sidecar(img_path)
        self._save()
        self._notify()

    def set_rating(self, img_path: str, rating: int):
        """Rating 0–5. 0 = unrated."""
        rating = max(0, min(5, int(rating)))
        key    = str(Path(img_path).resolve())
        with self._lock:
            entry = self._data.setdefault(key, {})
            entry["rating"] = rating
            entry["ts"]     = datetime.now().isoformat()
            if rating > 0:
                entry.setdefault("favorite", False)
        self._mirror_sidecar(img_path)
        self._save()
        self._notify()

    def toggle_favorite(self, img_path: str) -> bool:
        current = self.get_favorite(img_path)
        self.set_favorite(img_path, not current)
        return not current

    # ── Getters ──────────────────────────────────────────

    def get_favorite(self, img_path: str) -> bool:
        key = str(Path(img_path).resolve())
        with self._lock:
            return self._data.get(key, {}).get("favorite", False)

    def get_rating(self, img_path: str) -> int:
        key = str(Path(img_path).resolve())
        with self._lock:
            return self._data.get(key, {}).get("rating", 0)

    def get_entry(self, img_path: str) -> dict:
        key = str(Path(img_path).resolve())
        with self._lock:
            return dict(self._data.get(key, {}))

    def get_all_favorites(self) -> list:
        """Return list of abs paths that are favorited."""
        with self._lock:
            return [k for k, v in self._data.items()
                    if v.get("favorite")]

    def get_by_min_rating(self, min_rating: int) -> list:
        """Return list of abs paths with rating >= min_rating."""
        with self._lock:
            return [k for k, v in self._data.items()
                    if v.get("rating", 0) >= min_rating]

    def remove(self, img_path: str):
        key = str(Path(img_path).resolve())
        with self._lock:
            self._data.pop(key, None)
        self._save()
        self._notify()

    def clear_all(self):
        with self._lock:
            self._data.clear()
        self._save()
        self._notify()

    # ── Filter ───────────────────────────────────────────

    def filter_paths(self, paths: list,
                     fav_only: bool = False,
                     min_rating: int = 0) -> list:
        """Return subset of paths matching filter criteria."""
        result = []
        for p in paths:
            entry = self.get_entry(p)
            if fav_only and not entry.get("favorite"):
                continue
            if min_rating and entry.get("rating", 0) < min_rating:
                continue
            result.append(p)
        return result

    # ── Sidecar mirror ───────────────────────────────────

    def _mirror_sidecar(self, img_path: str):
        """Keep sidecar in sync with favorites data."""
        entry = self.get_entry(img_path)
        if not entry:
            return
        meta = _load_sidecar(img_path)
        if "favorite" in entry:
            meta["sf_favorite"] = entry["favorite"]
        if "rating" in entry:
            meta["sf_rating"] = entry["rating"]
        try:
            _save_sidecar(img_path, meta)
        except Exception:
            pass

    # ── Import from sidecars ─────────────────────────────

    def import_from_sidecars(self, folder: str):
        """
        Scan folder for sidecar files and import
        sf_favorite / sf_rating into the manager.
        """
        folder = Path(folder)
        count  = 0
        for sc in folder.rglob("*" + SIDECAR_EXT):
            try:
                with open(sc, encoding="utf-8") as f:
                    meta = json.load(f)
            except Exception:
                continue
            stem = sc.stem.replace(SIDECAR_EXT.lstrip("."), "")
            for ext in IMAGE_EXTS:
                img = sc.parent / (stem + ext)
                if img.exists():
                    key = str(img.resolve())
                    with self._lock:
                        entry = self._data.setdefault(key, {})
                        if "sf_favorite" in meta:
                            entry["favorite"] = meta["sf_favorite"]
                        if "sf_rating" in meta:
                            entry["rating"] = meta["sf_rating"]
                    count += 1
                    break
        self._save()
        return count


# ══════════════════════════════════════════════════════════
#  STAR RATING WIDGET — 1-5 clickable stars
# ══════════════════════════════════════════════════════════

class StarRatingWidget(tk.Frame):
    """
    Five clickable star symbols for 1-5 rating.

    Usage:
        sr = StarRatingWidget(parent, rating=3,
                              on_change=my_callback)
        sr.pack()
    """

    STAR_ON  = "★"
    STAR_OFF = "☆"

    def __init__(self, parent,
                 rating: int = 0,
                 on_change=None,
                 size: int = 14,
                 **kwargs):
        kwargs.setdefault("bg", SF_PANEL)
        super().__init__(parent, **kwargs)
        self._rating    = rating
        self._on_change = on_change
        self._stars     = []
        self._hover_r   = 0

        for i in range(1, 6):
            lbl = tk.Label(self, text=self.STAR_ON,
                           bg=self.cget("bg"),
                           fg=SF_STAR_ON if i <= rating else SF_STAR_OFF,
                           font=("Consolas", size),
                           cursor="hand2")
            lbl.pack(side="left", padx=0)
            lbl.bind("<Button-1>",
                     lambda e, r=i: self._set_rating(r))
            lbl.bind("<Enter>",
                     lambda e, r=i: self._hover(r))
            lbl.bind("<Leave>",
                     lambda e: self._hover(0))
            self._stars.append(lbl)

    def _hover(self, r: int):
        self._hover_r = r
        for i, lbl in enumerate(self._stars, 1):
            if r and i <= r:
                lbl.configure(fg=SF_ACCENT2)
            else:
                lbl.configure(
                    fg=SF_STAR_ON if i <= self._rating else SF_STAR_OFF)

    def _set_rating(self, r: int):
        # Click same star again → unrate
        if r == self._rating:
            r = 0
        self._rating = r
        self._hover(0)
        if self._on_change:
            self._on_change(r)

    def get_rating(self) -> int:
        return self._rating

    def set_rating(self, r: int):
        self._rating = max(0, min(5, r))
        self._hover(0)


# ══════════════════════════════════════════════════════════
#  FAVORITES THUMBNAIL — thumbnail with star overlay
# ══════════════════════════════════════════════════════════

class FavoritesThumbnail(tk.Frame):
    """
    Image thumbnail with star-overlay badge and favorite toggle.
    Integrates with FavoritesManager.

    Usage:
        thumb = FavoritesThumbnail(parent, img_path, manager=fm)
        thumb.pack()
    """

    def __init__(self, parent, img_path: str,
                 manager: FavoritesManager,
                 on_click=None, **kwargs):
        kwargs.setdefault("bg", SF_PANEL)
        super().__init__(parent, highlightthickness=1,
                         highlightbackground=SF_BORDER, **kwargs)
        self._path    = img_path
        self._manager = manager
        self._on_click= on_click
        self._tk_img  = None

        self._build()
        self._refresh_overlay()
        manager.add_change_listener(self._refresh_overlay)

    def _build(self):
        # Thumbnail canvas
        self._canvas = tk.Canvas(self, width=THUMB_W, height=THUMB_H,
                                  bg=SF_BG, highlightthickness=0)
        self._canvas.pack(side="top", padx=3, pady=(3, 0))
        self._load_thumb()

        # Favorite toggle button
        ctrl = tk.Frame(self, bg=SF_PANEL)
        ctrl.pack(fill="x", padx=3)

        self._fav_btn = tk.Label(ctrl, text="☆",
                                  bg=SF_PANEL, fg=SF_STAR_OFF,
                                  font=("Consolas", 12),
                                  cursor="hand2")
        self._fav_btn.pack(side="left")
        self._fav_btn.bind("<Button-1>", self._toggle_fav)

        # Mini star rating (3 stars for compact display)
        self._rating_frame = tk.Frame(ctrl, bg=SF_PANEL)
        self._rating_frame.pack(side="right")
        self._mini_stars = []
        for i in range(1, 4):
            lbl = tk.Label(self._rating_frame, text="★",
                           bg=SF_PANEL, fg=SF_STAR_OFF,
                           font=("Consolas", 8),
                           cursor="hand2")
            lbl.pack(side="left")
            lbl.bind("<Button-1>",
                     lambda e, r=i: self._set_mini_rating(r))
            self._mini_stars.append(lbl)

        # File label
        stem = Path(self._path).name
        if len(stem) > 14:
            stem = stem[:12] + "…"
        tk.Label(self, text=stem, bg=SF_PANEL, fg=SF_DIM,
                 font=("Consolas", 7)).pack(pady=(0, 3))

        self._canvas.bind("<Button-1>", self._on_click)

    def _load_thumb(self):
        if PIL_OK:
            try:
                img = Image.open(self._path)
                img.thumbnail((THUMB_W, THUMB_H), Image.LANCZOS)
                self._tk_img = ImageTk.PhotoImage(img)
                self._canvas.create_image(
                    THUMB_W//2, THUMB_H//2,
                    anchor="center", image=self._tk_img)
                return
            except Exception:
                pass
        self._canvas.create_rectangle(0, 0, THUMB_W, THUMB_H,
                                       fill=SF_BG)
        self._canvas.create_text(THUMB_W//2, THUMB_H//2,
                                  text="IMG", fill=SF_DIM,
                                  font=("Consolas", 8))

    def _refresh_overlay(self):
        is_fav = self._manager.get_favorite(self._path)
        rating  = self._manager.get_rating(self._path)

        # Favorite button
        self._fav_btn.configure(
            text="★" if is_fav else "☆",
            fg=SF_AMBER if is_fav else SF_STAR_OFF)

        # Frame highlight
        self.configure(
            highlightbackground=SF_AMBER if is_fav else SF_BORDER)

        # Mini stars (show rating out of 3 for compact display)
        for i, lbl in enumerate(self._mini_stars, 1):
            lbl.configure(
                fg=SF_STAR_ON if i <= rating else SF_STAR_OFF)

        # Badge on canvas
        self._canvas.delete("badge")
        if rating >= 4:
            self._canvas.create_text(
                THUMB_W - 4, 4, text="★★",
                anchor="ne", fill=SF_AMBER,
                font=("Consolas", 9, "bold"),
                tags="badge")
        elif is_fav:
            self._canvas.create_text(
                THUMB_W - 4, 4, text="♥",
                anchor="ne", fill=SF_AMBER,
                font=("Consolas", 9, "bold"),
                tags="badge")

    def _toggle_fav(self, event=None):
        self._manager.toggle_favorite(self._path)

    def _set_mini_rating(self, r: int):
        current = self._manager.get_rating(self._path)
        self._manager.set_rating(self._path, 0 if r == current else r)

    def _on_click(self, event=None):
        if self._on_click:
            self._on_click(self._path)


# ══════════════════════════════════════════════════════════
#  FAVORITES PANEL — full browser panel
# ══════════════════════════════════════════════════════════

class FavoritesPanel(tk.Toplevel):
    """
    Full favorites browser: grid of thumbnails with filter controls.

    Usage:
        from starfield_favorites import FavoritesManager, FavoritesPanel
        fm    = FavoritesManager(base_dir="/path/to/photos")
        panel = FavoritesPanel(root, manager=fm, image_paths=my_list)
    """

    def __init__(self, master,
                 manager: FavoritesManager = None,
                 image_paths: list = None,
                 folder: str = None):
        super().__init__(master)
        self.title("★  STARFIELD — Favorites Engine")
        self.configure(bg=SF_BG)
        self.geometry("920x640")

        self._manager = manager or FavoritesManager()
        self._all_paths  = []
        self._filt_paths = []
        self._thumbs     = []

        self._f_title  = tkfont.Font(family="Consolas", size=13, weight="bold")
        self._f_header = tkfont.Font(family="Consolas", size=10, weight="bold")
        self._f_body   = tkfont.Font(family="Consolas", size=9)
        self._f_nano   = tkfont.Font(family="Consolas", size=8)

        self._build_ui()

        src = image_paths or folder
        if src:
            self.load_images(src)

        self._manager.add_change_listener(self._on_data_change)

    # ── UI ────────────────────────────────────────────────

    def _build_ui(self):
        # Title bar
        tb = tk.Frame(self, bg=SF_PANEL, height=44)
        tb.pack(fill="x", side="top")
        tk.Label(tb, text="★  FAVORITES ENGINE",
                 bg=SF_PANEL, fg=SF_AMBER,
                 font=self._f_title).pack(side="left", padx=14, pady=8)
        self._status_var = tk.StringVar(value="No images loaded.")
        tk.Label(tb, textvariable=self._status_var,
                 bg=SF_PANEL, fg=SF_DIM,
                 font=self._f_body).pack(side="right", padx=14)

        # Filter toolbar
        ft = tk.Frame(self, bg=SF_PANEL_LIGHT)
        ft.pack(fill="x", pady=1)

        self._fav_only  = tk.BooleanVar(value=False)
        tk.Checkbutton(ft, text="★ Favorites Only",
                       variable=self._fav_only,
                       bg=SF_PANEL_LIGHT, fg=SF_AMBER,
                       activebackground=SF_PANEL_LIGHT,
                       selectcolor=SF_PANEL,
                       font=self._f_body,
                       command=self._apply_filter).pack(
            side="left", padx=10, pady=4)

        tk.Label(ft, text="Min Rating:",
                 bg=SF_PANEL_LIGHT, fg=SF_TEXT,
                 font=self._f_body).pack(side="left")

        self._min_rating = tk.IntVar(value=0)
        for r in range(0, 6):
            lbl = "Any" if r == 0 else "★" * r
            tk.Radiobutton(ft, text=lbl,
                           variable=self._min_rating,
                           value=r,
                           bg=SF_PANEL_LIGHT,
                           fg=SF_TEXT if r == 0 else SF_AMBER,
                           activebackground=SF_PANEL_LIGHT,
                           selectcolor=SF_PANEL,
                           font=self._f_nano,
                           command=self._apply_filter
                           ).pack(side="left", padx=4)

        tk.Button(ft, text="📁 Load Folder",
                  command=self._load_folder,
                  bg=SF_PANEL_LIGHT, fg=SF_TEXT,
                  font=self._f_body, relief="flat",
                  padx=8).pack(side="right", padx=8, pady=4)

        # Stats bar
        stats = tk.Frame(self, bg=SF_BG)
        stats.pack(fill="x", pady=2)
        self._stats_label = tk.Label(
            stats, text="", bg=SF_BG, fg=SF_DIM,
            font=self._f_nano)
        self._stats_label.pack(side="left", padx=14)

        # Grid area
        grid_container = tk.Frame(self, bg=SF_BG)
        grid_container.pack(fill="both", expand=True)

        self._grid_canvas = tk.Canvas(grid_container, bg=SF_BG,
                                       highlightthickness=0)
        vscroll = tk.Scrollbar(grid_container, orient="vertical",
                               command=self._grid_canvas.yview)
        self._grid_canvas.configure(yscrollcommand=vscroll.set)
        vscroll.pack(side="right", fill="y")
        self._grid_canvas.pack(side="left", fill="both", expand=True)

        self._grid_inner = tk.Frame(self._grid_canvas, bg=SF_BG)
        self._grid_win   = self._grid_canvas.create_window(
            (0, 0), window=self._grid_inner, anchor="nw")
        self._grid_inner.bind("<Configure>", self._on_grid_resize)
        self._grid_canvas.bind("<Configure>", self._on_canvas_resize)

        # Bottom action bar
        bot = tk.Frame(self, bg=SF_PANEL)
        bot.pack(fill="x", side="bottom")

        for text, cmd, color in [
            ("★ Mark ALL Visible as Favorite",
             lambda: self._batch_fav(True), SF_AMBER),
            ("☆ Remove ALL Visible Favorites",
             lambda: self._batch_fav(False), SF_DIM),
            ("Export Favorites…",
             self._export_favorites, SF_GREEN),
        ]:
            tk.Button(bot, text=text, command=cmd,
                      bg=SF_PANEL, fg=color,
                      font=self._f_body, relief="flat",
                      padx=10).pack(side="left", padx=4, pady=6)

    # ── Image Loading ─────────────────────────────────────

    def load_images(self, source):
        if isinstance(source, (list, tuple)):
            paths = [str(p) for p in source
                     if Path(str(p)).suffix.lower() in IMAGE_EXTS]
        else:
            p = Path(str(source))
            if p.is_dir():
                paths = sorted(str(f) for f in p.iterdir()
                               if f.is_file() and
                               f.suffix.lower() in IMAGE_EXTS)
            elif p.is_file():
                paths = [str(p)]
            else:
                paths = []
        self._all_paths = paths
        self._manager.import_from_sidecars(
            str(Path(paths[0]).parent) if paths else ".")
        self._apply_filter()

    def _load_folder(self):
        folder = filedialog.askdirectory(
            title="Select Starfield screenshots folder")
        if folder:
            self.load_images(folder)

    # ── Grid ─────────────────────────────────────────────

    def _render_grid(self):
        for w in self._grid_inner.winfo_children():
            w.destroy()
        self._thumbs.clear()
        cols = max(1, (self._grid_canvas.winfo_width() or 800) //
                   (THUMB_W + 20))
        for i, path in enumerate(self._filt_paths):
            thumb = FavoritesThumbnail(
                self._grid_inner, path,
                manager=self._manager)
            row = i // cols
            col = i % cols
            thumb.grid(row=row, column=col, padx=6, pady=6)
            self._thumbs.append(thumb)
        self._update_stats()

    def _on_grid_resize(self, event):
        self._grid_canvas.configure(
            scrollregion=self._grid_canvas.bbox("all"))

    def _on_canvas_resize(self, event):
        self._grid_canvas.itemconfigure(
            self._grid_win, width=event.width)
        self._render_grid()

    # ── Filter ────────────────────────────────────────────

    def _apply_filter(self):
        self._filt_paths = self._manager.filter_paths(
            self._all_paths,
            fav_only=self._fav_only.get(),
            min_rating=self._min_rating.get())
        self._render_grid()

    def _on_data_change(self):
        self._apply_filter()

    # ── Stats ────────────────────────────────────────────

    def _update_stats(self):
        total  = len(self._all_paths)
        shown  = len(self._filt_paths)
        n_fav  = len(self._manager.get_all_favorites())
        r4plus = len(self._manager.get_by_min_rating(4))
        self._status_var.set(
            f"{total} total  |  {shown} shown")
        self._stats_label.configure(
            text=f"★ {n_fav} favorited   ★★★★ {r4plus} rated 4+")

    # ── Batch ops ────────────────────────────────────────

    def _batch_fav(self, value: bool):
        for path in self._filt_paths:
            self._manager.set_favorite(path, value)

    def _export_favorites(self):
        paths = self._manager.get_all_favorites()
        if not paths:
            from tkinter import messagebox
            messagebox.showinfo("No Favorites",
                                "No favorites to export.")
            return
        dest = filedialog.askdirectory(
            title="Export favorites to folder")
        if not dest:
            return
        import shutil
        count = 0
        for p in paths:
            if Path(p).exists():
                shutil.copy2(p, Path(dest) / Path(p).name)
                sc = _sidecar_path(p)
                if Path(sc).exists():
                    shutil.copy2(sc, Path(dest) / Path(sc).name)
                count += 1
        from tkinter import messagebox
        messagebox.showinfo("Export Complete",
                            f"Exported {count} image(s) to:\n{dest}")


# ══════════════════════════════════════════════════════════
#  STANDALONE DEMO
# ══════════════════════════════════════════════════════════

if __name__ == "__main__":
    import sys
    from tkinter import filedialog

    root = tk.Tk()
    root.title("Starfield Favorites — Demo")
    root.configure(bg=SF_BG)
    root.withdraw()

    folder = None
    if len(sys.argv) > 1:
        folder = sys.argv[1]
    else:
        folder = filedialog.askdirectory(
            title="Select Starfield screenshots folder")

    if not folder:
        folder = None

    root.deiconify()
    root.geometry("300x120")

    fm    = FavoritesManager(base_dir=folder or str(Path.home()))
    panel = FavoritesPanel(root, manager=fm, folder=folder)
    panel.protocol("WM_DELETE_WINDOW", root.destroy)

    # Demo: standalone star rating widget
    demo_win = tk.Toplevel(root)
    demo_win.title("StarRatingWidget Demo")
    demo_win.configure(bg=SF_BG)
    demo_win.geometry("260x80")
    tk.Label(demo_win, text="Rate this screenshot:",
             bg=SF_BG, fg=SF_TEXT,
             font=("Consolas", 10)).pack(pady=8)
    sr = StarRatingWidget(
        demo_win, rating=3,
        on_change=lambda r: print(f"Rating set: {r} star(s)"),
        size=18, bg=SF_BG)
    sr.pack()

    root.mainloop()
