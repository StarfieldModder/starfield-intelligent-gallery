# # ════════════════════════════════════════════════════════════
#   FILE: starfield_batch_ops.py
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
#       Implements batch operations for the gallery, including
#       bulk renaming, metadata extraction, and multi-image
#       processing workflows.
# ═══════════════════════════════════════════════════════════
# 
# # =====================================================
# starfield_batch_ops.py  — COMPLETE v0.9.0
# STARFIELD IMAGE GALLERY — Phase 4 | Batch Operations Panel
# Multi-select, batch tag, rename, export, favorite.
# Developed: May 2026 | Mark — Brentwood, CA
# ============================================================
# INSTALL:   pip install Pillow
# INTEGRATE: from starfield_batch_ops import BatchOpsPanel
#            panel = BatchOpsPanel(root, image_paths=my_list)
# ============================================================

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from tkinter import font as tkfont
from pathlib import Path
import json, shutil, os, re, threading
from datetime import datetime

try:
    from PIL import Image, ImageTk
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
SF_SEL          = "#0F3A6A"

IMAGE_EXTS      = {".jpg",".jpeg",".png",".bmp",".gif",".tif",".tiff",".webp"}
SIDECAR_EXT     = ".sfmeta.json"
SF_CATEGORIES   = ["Uncategorized","Planets","Ships","Characters",
                    "Landscapes","Stations","Fauna","Combat","Other"]
THUMB_SIZE      = (80, 60)


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
#  THUMBNAIL ITEM
# ══════════════════════════════════════════════════════════

class ThumbItem(tk.Frame):
    """Checkable thumbnail item in the grid."""

    def __init__(self, parent, img_path: str, index: int,
                 on_toggle, **kwargs):
        super().__init__(parent, bg=SF_PANEL, relief="flat",
                         highlightthickness=1,
                         highlightbackground=SF_BORDER, **kwargs)
        self._path   = img_path
        self._index  = index
        self._on_toggle = on_toggle
        self._selected  = False
        self._tk_img    = None

        self._var = tk.BooleanVar(value=False)

        self._canvas = tk.Canvas(self, width=THUMB_SIZE[0],
                                 height=THUMB_SIZE[1],
                                 bg=SF_BG, highlightthickness=0)
        self._canvas.pack(side="top", padx=4, pady=(4, 0))
        self._load_thumb()

        stem = Path(img_path).name
        if len(stem) > 12:
            stem = stem[:10] + "…"
        tk.Label(self, text=stem, bg=SF_PANEL, fg=SF_DIM,
                 font=("Consolas", 7)).pack()

        cb = tk.Checkbutton(self, variable=self._var,
                            bg=SF_PANEL, fg=SF_TEXT,
                            activebackground=SF_PANEL,
                            selectcolor=SF_PANEL_LIGHT,
                            command=self._on_check)
        cb.pack()

        self._canvas.bind("<Button-1>", self._on_click)

    def _load_thumb(self):
        if PIL_OK:
            try:
                img = Image.open(self._path)
                img.thumbnail(THUMB_SIZE, Image.LANCZOS)
                self._tk_img = ImageTk.PhotoImage(img)
                self._canvas.create_image(
                    THUMB_SIZE[0]//2, THUMB_SIZE[1]//2,
                    anchor="center", image=self._tk_img)
                return
            except Exception:
                pass
        self._canvas.create_rectangle(0, 0, *THUMB_SIZE,
                                       fill=SF_BG, outline="")
        self._canvas.create_text(THUMB_SIZE[0]//2, THUMB_SIZE[1]//2,
                                  text="IMG", fill=SF_DIM,
                                  font=("Consolas", 8))

    def _on_click(self, event):
        self._var.set(not self._var.get())
        self._on_check()

    def _on_check(self):
        self._selected = self._var.get()
        color = SF_SEL if self._selected else SF_BORDER
        self.configure(highlightbackground=color)
        self._on_toggle(self._index, self._selected)

    def set_selected(self, val: bool):
        self._var.set(val)
        self._selected = val
        color = SF_SEL if val else SF_BORDER
        self.configure(highlightbackground=color)

    @property
    def path(self): return self._path
    @property
    def selected(self): return self._selected


# ══════════════════════════════════════════════════════════
#  BATCH OPS PANEL
# ══════════════════════════════════════════════════════════

class BatchOpsPanel(tk.Toplevel):
    """
    Multi-select batch operations window.

    Usage:
        from starfield_batch_ops import BatchOpsPanel
        BatchOpsPanel(root, image_paths=my_list)
    """

    def __init__(self, master, image_paths=None, folder: str = None):
        super().__init__(master)
        self.title("⚡  STARFIELD — Batch Operations")
        self.configure(bg=SF_BG)
        self.geometry("980x680")

        self._all_paths   = []
        self._thumbs      = []
        self._selected    = {}

        self._f_title  = tkfont.Font(family="Consolas", size=13, weight="bold")
        self._f_header = tkfont.Font(family="Consolas", size=10, weight="bold")
        self._f_body   = tkfont.Font(family="Consolas", size=9)
        self._f_nano   = tkfont.Font(family="Consolas", size=8)

        self._build_ui()

        src = image_paths or folder
        if src:
            self.load_images(src)

    def _build_ui(self):
        tb = tk.Frame(self, bg=SF_PANEL, height=44)
        tb.pack(fill="x", side="top")
        tk.Label(tb, text="⚡  BATCH OPERATIONS",
                 bg=SF_PANEL, fg=SF_ACCENT,
                 font=self._f_title).pack(side="left", padx=14, pady=8)
        self._status_var = tk.StringVar(value="No images loaded.")
        tk.Label(tb, textvariable=self._status_var,
                 bg=SF_PANEL, fg=SF_DIM,
                 font=self._f_body).pack(side="right", padx=14)

        sel_bar = tk.Frame(self, bg=SF_PANEL_LIGHT)
        sel_bar.pack(fill="x", side="top", pady=1)
        for text, cmd in [
            ("✔ Select All",   self._select_all),
            ("☐ Clear All",    self._clear_all),
            ("⇄ Invert",       self._invert),
            ("📁 Load Folder", self._load_folder),
        ]:
            tk.Button(sel_bar, text=text, command=cmd,
                      bg=SF_PANEL_LIGHT, fg=SF_TEXT,
                      activebackground=SF_BORDER,
                      font=self._f_body, relief="flat",
                      padx=10).pack(side="left", padx=2, pady=4)

        self._sel_label = tk.Label(sel_bar, text="0 selected",
                                    bg=SF_PANEL_LIGHT, fg=SF_AMBER,
                                    font=self._f_body)
        self._sel_label.pack(side="right", padx=14)

        main = tk.Frame(self, bg=SF_BG)
        main.pack(fill="both", expand=True)

        grid_frame = tk.Frame(main, bg=SF_BG)
        grid_frame.pack(side="left", fill="both", expand=True)

        canvas_frame = tk.Frame(grid_frame, bg=SF_BG)
        canvas_frame.pack(fill="both", expand=True)

        self._grid_canvas = tk.Canvas(canvas_frame, bg=SF_BG,
                                       highlightthickness=0)
        vscroll = tk.Scrollbar(canvas_frame, orient="vertical",
                               command=self._grid_canvas.yview)
        self._grid_canvas.configure(yscrollcommand=vscroll.set)
        vscroll.pack(side="right", fill="y")
        self._grid_canvas.pack(side="left", fill="both", expand=True)

        self._grid_inner = tk.Frame(self._grid_canvas, bg=SF_BG)
        self._grid_win   = self._grid_canvas.create_window(
            (0, 0), window=self._grid_inner, anchor="nw")
        self._grid_inner.bind("<Configure>", self._on_grid_resize)
        self._grid_canvas.bind("<Configure>", self._on_canvas_resize)

        ops = tk.Frame(main, bg=SF_PANEL, width=290)
        ops.pack(side="right", fill="y")
        ops.pack_propagate(False)
        self._build_ops_panel(ops)

        log_frame = tk.Frame(self, bg=SF_PANEL, height=90)
        log_frame.pack(fill="x", side="bottom")
        log_frame.pack_propagate(False)
        tk.Label(log_frame, text="Operation Log",
                 bg=SF_PANEL, fg=SF_DIM,
                 font=self._f_nano).pack(anchor="w", padx=6)
        self._log_text = tk.Text(log_frame, bg=SF_BG, fg=SF_DIM,
                                  font=self._f_nano, height=4,
                                  state="disabled", relief="flat")
        self._log_text.pack(fill="both", expand=True, padx=4, pady=(0,4))

    def _build_ops_panel(self, parent):
        def section(text):
            f = tk.Frame(parent, bg=SF_PANEL)
            f.pack(fill="x", padx=8, pady=(10, 2))
            tk.Frame(f, bg=SF_BORDER, height=1).pack(fill="x")
            tk.Label(f, text=text, bg=SF_PANEL, fg=SF_ACCENT,
                     font=self._f_header).pack(anchor="w")
            return parent

        section("▸ Batch Category Tag")
        cat_row = tk.Frame(parent, bg=SF_PANEL)
        cat_row.pack(fill="x", padx=8, pady=2)
        self._cat_var = tk.StringVar(value="Uncategorized")
        cat_menu = tk.OptionMenu(cat_row, self._cat_var, *SF_CATEGORIES)
        cat_menu.configure(bg=SF_PANEL_LIGHT, fg=SF_TEXT,
                           activebackground=SF_BORDER,
                           font=self._f_body, relief="flat", width=18)
        cat_menu["menu"].configure(bg=SF_PANEL_LIGHT, fg=SF_TEXT,
                                    font=self._f_body)
        cat_menu.pack(side="left")
        tk.Button(cat_row, text="Apply",
                  command=self._batch_category,
                  bg=SF_ACCENT, fg=SF_BG,
                  font=self._f_body, relief="flat").pack(side="right")

        section("▸ Batch Rename")
        rn_frame = tk.Frame(parent, bg=SF_PANEL)
        rn_frame.pack(fill="x", padx=8, pady=2)

        tk.Label(rn_frame, text="Prefix:", bg=SF_PANEL, fg=SF_TEXT,
                 font=self._f_body).grid(row=0, column=0, sticky="w")
        self._pfx_var = tk.StringVar(value="SF_")
        tk.Entry(rn_frame, textvariable=self._pfx_var, width=12,
                 bg=SF_PANEL_LIGHT, fg=SF_TEXT,
                 insertbackground=SF_ACCENT,
                 font=self._f_body).grid(row=0, column=1, padx=4, pady=2)

        tk.Label(rn_frame, text="Start #:", bg=SF_PANEL, fg=SF_TEXT,
                 font=self._f_body).grid(row=1, column=0, sticky="w")
        self._start_var = tk.StringVar(value="1")
        tk.Entry(rn_frame, textvariable=self._start_var, width=6,
                 bg=SF_PANEL_LIGHT, fg=SF_TEXT,
                 insertbackground=SF_ACCENT,
                 font=self._f_body).grid(row=1, column=1, padx=4, pady=2,
                                         sticky="w")

        self._date_in_name = tk.BooleanVar(value=False)
        tk.Checkbutton(rn_frame, text="Include date",
                       variable=self._date_in_name,
                       bg=SF_PANEL, fg=SF_TEXT,
                       activebackground=SF_PANEL,
                       selectcolor=SF_PANEL_LIGHT,
                       font=self._f_body).grid(row=2, column=0,
                                                columnspan=2, sticky="w")
        tk.Button(rn_frame, text="Rename Selected",
                  command=self._batch_rename,
                  bg=SF_ORANGE, fg=SF_BG,
                  font=self._f_body, relief="flat").grid(
            row=3, column=0, columnspan=2, pady=4, sticky="ew")

        section("▸ Batch Export")
        ex_frame = tk.Frame(parent, bg=SF_PANEL)
        ex_frame.pack(fill="x", padx=8, pady=2)

        self._copy_sidecars = tk.BooleanVar(value=True)
        tk.Checkbutton(ex_frame, text="Copy sidecars (.sfmeta.json)",
                       variable=self._copy_sidecars,
                       bg=SF_PANEL, fg=SF_TEXT,
                       activebackground=SF_PANEL,
                       selectcolor=SF_PANEL_LIGHT,
                       font=self._f_body).pack(anchor="w")
        self._flatten_export = tk.BooleanVar(value=True)
        tk.Checkbutton(ex_frame, text="Flatten into one folder",
                       variable=self._flatten_export,
                       bg=SF_PANEL, fg=SF_TEXT,
                       activebackground=SF_PANEL,
                       selectcolor=SF_PANEL_LIGHT,
                       font=self._f_body).pack(anchor="w")
        tk.Button(ex_frame, text="Export to Folder…",
                  command=self._batch_export,
                  bg=SF_GREEN, fg=SF_BG,
                  font=self._f_body, relief="flat").pack(fill="x", pady=4)

        section("▸ Batch Favorites")
        fav_frame = tk.Frame(parent, bg=SF_PANEL)
        fav_frame.pack(fill="x", padx=8, pady=2)
        tk.Button(fav_frame, text="★  Mark as Favorites",
                  command=lambda: self._batch_favorite(True),
                  bg=SF_AMBER, fg=SF_BG,
                  font=self._f_body, relief="flat").pack(fill="x", pady=2)
        tk.Button(fav_frame, text="☆  Remove from Favorites",
                  command=lambda: self._batch_favorite(False),
                  bg=SF_PANEL_LIGHT, fg=SF_TEXT,
                  font=self._f_body, relief="flat").pack(fill="x", pady=2)

        section("▸ Batch Notes / Tag")
        notes_frame = tk.Frame(parent, bg=SF_PANEL)
        notes_frame.pack(fill="x", padx=8, pady=2)
        tk.Label(notes_frame, text="Append note:",
                 bg=SF_PANEL, fg=SF_TEXT,
                 font=self._f_body).pack(anchor="w")
        self._note_var = tk.StringVar()
        tk.Entry(notes_frame, textvariable=self._note_var,
                 bg=SF_PANEL_LIGHT, fg=SF_TEXT,
                 insertbackground=SF_ACCENT,
                 font=self._f_body).pack(fill="x", pady=2)
        tk.Button(notes_frame, text="Apply Note",
                  command=self._batch_note,
                  bg=SF_PANEL_LIGHT, fg=SF_ACCENT,
                  font=self._f_body, relief="flat").pack(fill="x", pady=2)

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
        self._selected  = {}
        self._render_grid()
        self._update_status()

    def _load_folder(self):
        folder = filedialog.askdirectory(
            title="Select Starfield screenshots folder")
        if folder:
            self.load_images(folder)

    def _render_grid(self):
        for w in self._grid_inner.winfo_children():
            w.destroy()
        self._thumbs.clear()
        cols = max(1, (self._grid_canvas.winfo_width() or 700) // 108)
        for i, path in enumerate(self._all_paths):
            item = ThumbItem(self._grid_inner, path, i,
                             on_toggle=self._on_toggle)
            row = i // cols
            col = i % cols
            item.grid(row=row, column=col, padx=4, pady=4)
            self._thumbs.append(item)

    def _on_grid_resize(self, event):
        self._grid_canvas.configure(
            scrollregion=self._grid_canvas.bbox("all"))

    def _on_canvas_resize(self, event):
        self._grid_canvas.itemconfigure(
            self._grid_win, width=event.width)
        self._render_grid()

    def _on_toggle(self, index: int, selected: bool):
        self._selected[index] = selected
        self._update_status()

    def _select_all(self):
        for t in self._thumbs:
            t.set_selected(True)
            self._selected[t._index] = True
        self._update_status()

    def _clear_all(self):
        for t in self._thumbs:
            t.set_selected(False)
            self._selected[t._index] = False
        self._update_status()

    def _invert(self):
        for t in self._thumbs:
            val = not t.selected
            t.set_selected(val)
            self._selected[t._index] = val
        self._update_status()

    def _selected_paths(self):
        return [self._all_paths[i]
                for i, v in self._selected.items() if v
                and i < len(self._all_paths)]

    def _update_status(self):
        n     = sum(1 for v in self._selected.values() if v)
        total = len(self._all_paths)
        self._status_var.set(f"{total} images loaded")
        self._sel_label.configure(text=f"{n} selected")

    def _batch_category(self):
        paths = self._selected_paths()
        if not paths:
            self._log("No images selected.")
            return
        cat = self._cat_var.get()
        for p in paths:
            meta = _load_sidecar(p)
            meta["sf_category"] = cat
            _save_sidecar(p, meta)
        self._log(f"Category '{cat}' applied to {len(paths)} image(s).")

    def _batch_rename(self):
        paths = self._selected_paths()
        if not paths:
            self._log("No images selected.")
            return
        pfx    = self._pfx_var.get().strip()
        try:
            start  = int(self._start_var.get())
        except ValueError:
            start = 1
        use_date = self._date_in_name.get()
        renamed  = 0
        errors   = 0
        for i, old_path in enumerate(paths, start):
            p   = Path(old_path)
            ext = p.suffix.lower()
            date_part = ""
            if use_date:
                date_part = datetime.now().strftime("_%Y%m%d")
            new_name = f"{pfx}{i:04d}{date_part}{ext}"
            new_path = p.parent / new_name
            old_sc   = _sidecar_path(old_path)
            new_sc   = str(new_path.with_suffix("")) + SIDECAR_EXT
            try:
                p.rename(new_path)
                if Path(old_sc).exists():
                    Path(old_sc).rename(new_sc)
                idx = self._all_paths.index(old_path)
                self._all_paths[idx] = str(new_path)
                renamed += 1
            except Exception as e:
                self._log(f"Error renaming {p.name}: {e}")
                errors += 1
        self._log(f"Renamed {renamed} file(s). Errors: {errors}.")