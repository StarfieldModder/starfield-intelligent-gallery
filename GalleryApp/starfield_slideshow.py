# ════════════════════════════════════════════════════════════
#   FILE: starfield_slideshow.py
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
#       Provides slideshow playback functionality for the
#       Starfield Image Gallery. Supports timed transitions,
#       keyboard navigation, and modal integration.
# ════════════════════════════════════════════════════════════
#
# ═════════════════════════════════════════════════════# ============================================================
# starfield_slideshow.py - V 0.9.0
# STARFIELD IMAGE GALLERY — Phase 4 | Cinematic Slideshow Engine
# Full-screen fade/dissolve slideshow with Starfield aesthetic.
# Developed: May 2026 | Mark — Brentwood, CA
# ============================================================
# INSTALL:   pip install Pillow
# INTEGRATE: from starfield_slideshow import SlideshowWindow
#            SlideshowWindow(root, image_paths=my_list)
# ============================================================

import tkinter as tk
from tkinter import font as tkfont
from pathlib import Path
import threading, time, random, json

try:
    from PIL import Image, ImageTk, ImageEnhance, ImageFilter
    PIL_OK = True
except ImportError:
    PIL_OK = False

# ── Palette ───────────────────────────────────────────────
SF_BG       = "#0A0E1A"
SF_PANEL    = "#0D1526"
SF_BORDER   = "#1A3A5C"
SF_ACCENT   = "#00B4FF"
SF_ACCENT2  = "#00D4FF"
SF_TEXT     = "#C8D8E8"
SF_ORANGE   = "#FF6B00"
SF_GREEN    = "#00FF9C"
SF_AMBER    = "#FFB300"
SF_RED      = "#FF4444"
SF_DIM      = "#4A6080"

IMAGE_EXTS  = {".jpg",".jpeg",".png",".bmp",".gif",".tif",".tiff",".webp"}
SIDECAR_EXT = ".sfmeta.json"


def _load_sidecar(image_path: str) -> dict:
    sp = str(Path(image_path).with_suffix("")) + SIDECAR_EXT
    if Path(sp).exists():
        try:
            with open(sp, encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return {}


def _collect_images(source) -> list:
    """Accept folder path, list of paths, or single path."""
    if isinstance(source, (list, tuple)):
        return [str(p) for p in source
                if Path(str(p)).suffix.lower() in IMAGE_EXTS]
    p = Path(str(source))
    if p.is_dir():
        return sorted(str(f) for f in p.iterdir()
                      if f.is_file() and f.suffix.lower() in IMAGE_EXTS)
    if p.is_file() and p.suffix.lower() in IMAGE_EXTS:
        return [str(p)]
    return []


# ══════════════════════════════════════════════════════════
#  CINEMATIC SLIDESHOW WINDOW
# ══════════════════════════════════════════════════════════

class SlideshowWindow(tk.Toplevel):
    """
    Full-screen cinematic slideshow.

    Controls:
      ←/→        Previous / Next
      SPACE       Pause / resume + toggle info overlay
      S           Toggle shuffle
      F           Toggle favorites-only mode
      ESC         Exit slideshow
      +/-         Increase / decrease slide interval

    Usage:
        from starfield_slideshow import SlideshowWindow
        ss = SlideshowWindow(root, image_paths=my_list, interval=5.0)
    """

    FADE_STEPS   = 20
    FADE_MS      = 25
    MIN_INTERVAL = 2.0
    MAX_INTERVAL = 30.0

    def __init__(self, master,
                 image_paths=None,
                 folder: str = None,
                 interval: float = 5.0,
                 shuffle: bool = False,
                 favorites_only: bool = False):
        super().__init__(master)
        self.title("Starfield Slideshow")
        self.configure(bg=SF_BG)
        self.attributes("-fullscreen", True)
        self.focus_set()

        self._interval    = interval
        self._shuffle     = shuffle
        self._fav_only    = favorites_only
        self._paused      = False
        self._show_info   = True
        self._current     = 0
        self._fade_job    = None
        self._auto_job    = None
        self._tk_img_a    = None
        self._tk_img_b    = None
        self._pil_img_b   = None
        self._transitioning = False

        self._font_title  = tkfont.Font(family="Consolas", size=14, weight="bold")
        self._font_body   = tkfont.Font(family="Consolas", size=10)
        self._font_nano   = tkfont.Font(family="Consolas", size=8)
        self._font_hud    = tkfont.Font(family="Consolas", size=9)

        src = image_paths or folder
        self._all_images  = _collect_images(src) if src else []
        self._build_playlist()

        self._canvas = tk.Canvas(self, bg=SF_BG, highlightthickness=0)
        self._canvas.pack(fill="both", expand=True)

        self._canvas_id_a  = self._canvas.create_image(0, 0, anchor="nw")
        self._canvas_id_b  = self._canvas.create_image(0, 0, anchor="nw",
                                                        state="hidden")
        self._info_bg_id   = None
        self._info_items   = []
        self._hud_items    = []

        self._draw_scanlines()
        self._draw_hud()

        self.bind("<Escape>",       lambda e: self.destroy())
        self.bind("<Left>",         lambda e: self._nav(-1))
        self.bind("<Right>",        lambda e: self._nav(1))
        self.bind("<space>",        lambda e: self._toggle_pause())
        self.bind("s",              lambda e: self._toggle_shuffle())
        self.bind("S",              lambda e: self._toggle_shuffle())
        self.bind("f",              lambda e: self._toggle_fav_only())
        self.bind("F",              lambda e: self._toggle_fav_only())
        self.bind("<plus>",         lambda e: self._change_interval(1))
        self.bind("<minus>",        lambda e: self._change_interval(-1))
        self.bind("<KP_Add>",       lambda e: self._change_interval(1))
        self.bind("<KP_Subtract>",  lambda e: self._change_interval(-1))
        self.bind("<Configure>",    self._on_resize)

        if self._playlist:
            self._show_frame(0, transition=False)
            self._schedule_auto()

    def _build_playlist(self):
        images = self._all_images[:]
        if self._fav_only:
            images = [p for p in images
                      if _load_sidecar(p).get("sf_favorite") or
                         _load_sidecar(p).get("sf_rating", 0)]
        if self._shuffle:
            random.shuffle(images)
        self._playlist = images
        if self._current >= len(self._playlist):
            self._current = 0

    def _nav(self, delta: int):
        if not self._playlist:
            return
        self._cancel_auto()
        self._current = (self._current + delta) % len(self._playlist)
        self._show_frame(self._current, transition=True)
        if not self._paused:
            self._schedule_auto()

    def _schedule_auto(self):
        self._cancel_auto()
        if not self._paused and self._playlist:
            self._auto_job = self.after(
                int(self._interval * 1000), self._auto_advance)

    def _cancel_auto(self):
        if self._auto_job:
            self.after_cancel(self._auto_job)
            self._auto_job = None

    def _auto_advance(self):
        if not self._playlist:
            return
        self._current = (self._current + 1) % len(self._playlist)
        self._show_frame(self._current, transition=True)
        self._schedule_auto()

    def _show_frame(self, index: int, transition: bool = True):
        if not self._playlist:
            return
        path = self._playlist[index]
        if PIL_OK:
            try:
                img = Image.open(path)
                w   = self.winfo_width()  or self.winfo_screenwidth()
                h   = self.winfo_height() or self.winfo_screenheight()
                if w < 10: w = self.winfo_screenwidth()
                if h < 10: h = self.winfo_screenheight()
                img.thumbnail((w, h), Image.LANCZOS)
                ox = (w - img.width)  // 2
                oy = (h - img.height) // 2
                if transition and self._tk_img_a:
                    self._pil_img_b = img
                    self._tk_img_b = ImageTk.PhotoImage(img)
                    self._canvas.itemconfigure(self._canvas_id_b,
                                               image=self._tk_img_b,
                                               state="normal")
                    self._canvas.coords(self._canvas_id_b, ox, oy)
                    self._canvas.tag_lower(self._canvas_id_b,
                                           self._canvas_id_a)
                    self._fade_out(step=0, ox=ox, oy=oy, img=img)
                else:
                    self._tk_img_a = ImageTk.PhotoImage(img)
                    self._canvas.itemconfigure(self._canvas_id_a,
                                               image=self._tk_img_a)
                    self._canvas.coords(self._canvas_id_a, ox, oy)
            except Exception:
                pass
        self._update_info(path)
        self._update_hud()

    def _fade_out(self, step, ox, oy, img):
        if step < self.FADE_STEPS:
            self._fade_job = self.after(
                self.FADE_MS,
                lambda: self._fade_out(step + 1, ox, oy, img))
        else:
            self._tk_img_a = self._tk_img_b
            self._canvas.itemconfigure(self._canvas_id_a,
                                       image=self._tk_img_a)
            self._canvas.coords(self._canvas_id_a, ox, oy)
            self._canvas.itemconfigure(self._canvas_id_b, state="hidden")
            self._canvas.tag_raise(self._canvas_id_a)

    def _update_info(self, path: str):
        for item_id in self._info_items:
            self._canvas.delete(item_id)
        self._info_items.clear()
        if not self._show_info:
            return

        meta  = _load_sidecar(path)
        stem  = Path(path).name
        cat   = meta.get("sf_category", "—")
        filt  = meta.get("sf_filter",   "—")
        planet= meta.get("sf_planet",   "—")
        ship  = meta.get("sf_ship",     "—")
        char_ = meta.get("sf_character","—")
        notes = meta.get("sf_notes",    "")
        date_ = meta.get("sf_date",     "—")
        fav   = "★" if meta.get("sf_favorite") else "☆"
        rating= "★" * int(meta.get("sf_rating", 0))

        lines = [
            f"  {fav} {stem}",
            f"  Category : {cat}",
            f"  Filter   : {filt}",
            f"  Planet   : {planet}",
            f"  Ship     : {ship}",
            f"  Crew     : {char_}",
            f"  Date     : {date_}",
        ]
        if notes:
            lines.append(f"  Notes    : {notes[:60]}")
        if rating:
            lines.append(f"  Rating   : {rating}")

        w  = self.winfo_width() or self.winfo_screenwidth()
        h  = self.winfo_height() or self.winfo_screenheight()
        bx = 24; by = h - 30 - len(lines) * 18
        bw = 340; bh = len(lines) * 18 + 12

        bg_id = self._canvas.create_rectangle(
            bx - 6, by - 6, bx + bw, by + bh,
            fill=SF_PANEL, outline=SF_BORDER, width=1)
        self._info_items.append(bg_id)

        for i, line in enumerate(lines):
            color = SF_ACCENT if i == 0 else SF_TEXT
            tid = self._canvas.create_text(
                bx, by + i * 18,
                text=line, anchor="nw",
                fill=color,
                font=self._font_body)
            self._info_items.append(tid)

    def _draw_hud(self):
        for h in self._hud_items:
            self._canvas.delete(h)
        self._hud_items.clear()

    def _update_hud(self):
        for h in self._hud_items:
            self._canvas.delete(h)
        self._hud_items.clear()

        w  = self.winfo_width() or self.winfo_screenwidth()
        h  = self.winfo_height() or self.winfo_screenheight()
        total = len(self._playlist)
        idx   = self._current + 1 if self._playlist else 0

        pause_str = "⏸ PAUSED" if self._paused else "▶ PLAYING"
        shuf_str  = "⇄ ON" if self._shuffle else "⇄ OFF"
        fav_str   = "★ FAV" if self._fav_only else ""
        hud_text  = (f"  {pause_str}   {idx}/{total}   "
                     f"⏱ {self._interval:.0f}s   {shuf_str}  {fav_str}"
                     "   [SPC] Pause/Info  [←→] Nav  [S] Shuffle  "
                     "[F] Fav  [+/-] Speed  [ESC] Exit")

        bar_id = self._canvas.create_rectangle(
            0, h - 22, w, h,
            fill=SF_PANEL, outline="")
        line_id = self._canvas.create_line(
            0, h - 22, w, h - 22,
            fill=SF_BORDER)
        text_id = self._canvas.create_text(
            0, h - 11,
            text=hud_text, anchor="w",
            fill=SF_DIM, font=self._font_hud)
        self._hud_items.extend([bar_id, line_id, text_id])
        if total:
            bar_w   = int(w * (self._current + 1) / total)
            prog_id = self._canvas.create_rectangle(
                0, h - 3, bar_w, h,
                fill=SF_ACCENT, outline="")
            self._hud_items.append(prog_id)

    def _draw_scanlines(self):
        w = self.winfo_screenwidth()
        h = self.winfo_screenheight()
        for y in range(0, h, 4):
            self._canvas.create_line(
                0, y, w, y, fill="#000000", stipple="gray25")

    def _toggle_pause(self):
        self._paused = not self._paused
        self._show_info = not self._show_info
        if self._paused:
            self._cancel_auto()
        else:
            self._schedule_auto()
        if self._playlist:
            self._update_info(self._playlist[self._current])
        self._update_hud()

    def _toggle_shuffle(self):
        self._shuffle = not self._shuffle
        pos = self._playlist[self._current] if self._playlist else None
        self._build_playlist()
        if pos and pos in self._playlist:
            self._current = self._playlist.index(pos)
        self._update_hud()

    def _toggle_fav_only(self):
        self._fav_only = not self._fav_only
        pos = self._playlist[self._current] if self._playlist else None
        self._build_playlist()
        self._current = 0
        if pos and pos in self._playlist:
            self._current = self._playlist.index(pos)
        self._update_hud()

    def _change_interval(self, delta: int):
        self._interval = max(self.MIN_INTERVAL,
                             min(self.MAX_INTERVAL,
                                 self._interval + delta))
        self._update_hud()
        if not self._paused:
            self._schedule_auto()

    def _on_resize(self, event):
        if self._playlist:
            self._show_frame(self._current, transition=False)

    def destroy(self):
        self._cancel_auto()
        if self._fade_job:
            self.after_cancel(self._fade_job)
        super().destroy()


# ══════════════════════════════════════════════════════════
#  STANDALONE DEMO
# ══════════════════════════════════════════════════════════

if __name__ == "__main__":
    import sys
    from tkinter import filedialog

    root = tk.Tk()
    root.withdraw()

    folder = None
    if len(sys.argv) > 1:
        folder = sys.argv[1]
    else:
        folder = filedialog.askdirectory(
            title="Select Starfield screenshots folder")

    if not folder:
        print("No folder selected.")
        root.destroy()
        sys.exit()

    root.deiconify()
    root.title("Starfield Slideshow — Loading...")
    root.configure(bg=SF_BG)
    root.geometry("400x200")

    ss = SlideshowWindow(root, folder=folder, interval=5.0, shuffle=False)
    ss.protocol("WM_DELETE_WINDOW", root.destroy)
    root.mainloop()
