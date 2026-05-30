# ════════════════════════════════════════════════════════════
#   FILE: starfield_holo_effects.py
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
#       Provides optional holographic-style visual effects for
#       UI elements and image transitions, inspired by the
#       Starfield aesthetic.
# ════════════════════════════════════════════════════════════

# ============================================================
# starfield_holo_effects.py  — COMPLETE v0.9.0
# starfield_intelligent_gallery — Phase 4 | Holo-Panel Visual Effects
# Pulsing glow borders, scanlines, corner brackets, hover glow.
# Developed: May 2026 | Mark — Brentwood, CA
# ============================================================
# INSTALL:   No extra packages — uses Tkinter Canvas only.
# INTEGRATE:
#   from starfield_holo_effects import (
#       HoloPanel, HoloButton, HoloBorder,
#       add_scanline_overlay, add_corner_brackets
#   )
# ============================================================

import tkinter as tk
from tkinter import font as tkfont
import math, colorsys, time

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


def _hex_to_rgb(hex_color: str):
    h = hex_color.lstrip("#")
    return tuple(int(h[i:i+2], 16) for i in (0, 2, 4))

def _rgb_to_hex(r, g, b):
    return f"#{int(r):02x}{int(g):02x}{int(b):02x}"

def _lerp_color(c1: str, c2: str, t: float) -> str:
    r1, g1, b1 = _hex_to_rgb(c1)
    r2, g2, b2 = _hex_to_rgb(c2)
    r = r1 + (r2 - r1) * t
    g = g1 + (g2 - g1) * t
    b = b1 + (b2 - b1) * t
    return _rgb_to_hex(r, g, b)


# ══════════════════════════════════════════════════════════
#  HOLO BORDER — pulsing glow rectangle on a Canvas
# ══════════════════════════════════════════════════════════

class HoloBorder:
    """
    Draws a multi-layer pulsing border glow on an existing Canvas.
    Call .start() to animate, .stop() to halt, .destroy() to clean up.

    Usage:
        canvas = tk.Canvas(...)
        border = HoloBorder(canvas, x1=5, y1=5, x2=295, y2=195,
                            color=SF_ACCENT, pulse=True)
        border.start()
    """

    LAYERS     = 4     # concentric rect rings
    PERIOD_MS  = 60    # animation tick
    PULSE_SEC  = 2.5   # full pulse cycle duration

    def __init__(self, canvas: tk.Canvas,
                 x1=0, y1=0, x2=200, y2=100,
                 color: str = SF_ACCENT,
                 pulse: bool = True,
                 corner_brackets: bool = True):
        self._canvas = canvas
        self._x1, self._y1, self._x2, self._y2 = x1, y1, x2, y2
        self._color   = color
        self._pulse   = pulse
        self._running = False
        self._job     = None
        self._rects   = []
        self._brackets= []
        self._t0      = time.time()
        self._phase   = 0.0

        # Create layer rects (outer → inner, progressively thinner)
        for i in range(self.LAYERS):
            pad  = i * 2
            rect = canvas.create_rectangle(
                x1 - pad, y1 - pad, x2 + pad, y2 + pad,
                outline=color, width=max(1, self.LAYERS - i),
                fill="")
            self._rects.append(rect)

        if corner_brackets:
            self._draw_corner_brackets()

    def _draw_corner_brackets(self):
        """Sci-fi corner decorations (L-shaped brackets)."""
        x1, y1, x2, y2 = self._x1, self._y1, self._x2, self._y2
        size  = 12
        thick = 2
        clr   = self._color
        c     = self._canvas

        def bracket(ax, ay, dx, dy):
            # Horizontal leg
            h = c.create_line(ax, ay, ax + dx * size, ay,
                               fill=clr, width=thick)
            # Vertical leg
            v = c.create_line(ax, ay, ax, ay + dy * size,
                               fill=clr, width=thick)
            self._brackets.extend([h, v])

        bracket(x1, y1,  1,  1)  # top-left
        bracket(x2, y1, -1,  1)  # top-right
        bracket(x1, y2,  1, -1)  # bottom-left
        bracket(x2, y2, -1, -1)  # bottom-right

    def start(self):
        self._running = True
        self._t0 = time.time()
        self._tick()

    def stop(self):
        self._running = False
        if self._job:
            try:
                self._canvas.after_cancel(self._job)
            except Exception:
                pass
            self._job = None

    def _tick(self):
        if not self._running:
            return
        elapsed   = time.time() - self._t0
        phase     = (elapsed % self.PULSE_SEC) / self.PULSE_SEC
        # Sine pulse: 0 → 1 → 0
        intensity = (math.sin(phase * 2 * math.pi - math.pi / 2) + 1) / 2

        dim_color  = _lerp_color(SF_BG, self._color, 0.15)
        glow_color = self._color

        for i, rect_id in enumerate(self._rects):
            # Inner rects brighter; outer dims with distance
            layer_t = intensity * (1.0 - i * 0.22)
            c = _lerp_color(dim_color, glow_color, max(0, layer_t))
            try:
                self._canvas.itemconfigure(rect_id, outline=c)
            except tk.TclError:
                return

        # Pulse bracket color too
        bracket_color = _lerp_color(SF_DIM, self._color,
                                     intensity * 0.8 + 0.2)
        for bid in self._brackets:
            try:
                self._canvas.itemconfigure(bid, fill=bracket_color)
            except tk.TclError:
                return

        if self._running:
            self._job = self._canvas.after(self.PERIOD_MS, self._tick)

    def destroy(self):
        self.stop()
        for r in self._rects:
            try: self._canvas.delete(r)
            except Exception: pass
        for b in self._brackets:
            try: self._canvas.delete(b)
            except Exception: pass
        self._rects.clear()
        self._brackets.clear()

    def set_color(self, color: str):
        self._color = color

    def set_pulse(self, enabled: bool):
        self._pulse = enabled
        if not enabled:
            # Lock to full brightness
            for r in self._rects:
                try:
                    self._canvas.itemconfigure(r, outline=self._color)
                except Exception: pass


# ══════════════════════════════════════════════════════════
#  SCANLINE OVERLAY
# ══════════════════════════════════════════════════════════

class ScanlineOverlay:
    """
    Draws horizontal scanlines on a Canvas for CRT/holo feel.
    Optionally animates a slow scroll for a live-screen effect.

    Usage:
        overlay = ScanlineOverlay(canvas, width=400, height=300)
        overlay.start()
    """

    SCROLL_MS = 80   # ms per scroll step
    LINE_GAP  = 4    # pixels between scanlines

    def __init__(self, canvas: tk.Canvas,
                 width: int, height: int,
                 color: str = "#000000",
                 stipple: str = "gray25",
                 animate_scroll: bool = False):
        self._canvas = canvas
        self._w      = width
        self._h      = height
        self._color  = color
        self._stipple= stipple
        self._scroll = animate_scroll
        self._lines  = []
        self._offset = 0
        self._job    = None
        self._running= False
        self._draw()

    def _draw(self):
        for lid in self._lines:
            try: self._canvas.delete(lid)
            except Exception: pass
        self._lines.clear()
        for y in range(-self.LINE_GAP + self._offset,
                        self._h + self.LINE_GAP,
                        self.LINE_GAP):
            lid = self._canvas.create_line(
                0, y, self._w, y,
                fill=self._color, stipple=self._stipple)
            self._lines.append(lid)

    def start(self):
        if self._scroll:
            self._running = True
            self._tick()

    def stop(self):
        self._running = False
        if self._job:
            try: self._canvas.after_cancel(self._job)
            except Exception: pass

    def _tick(self):
        if not self._running:
            return
        self._offset = (self._offset + 1) % self.LINE_GAP
        self._draw()
        self._job = self._canvas.after(self.SCROLL_MS, self._tick)

    def destroy(self):
        self.stop()
        for lid in self._lines:
            try: self._canvas.delete(lid)
            except Exception: pass
        self._lines.clear()


# ══════════════════════════════════════════════════════════
#  HOLO BUTTON — glows on hover
# ══════════════════════════════════════════════════════════

class HoloButton(tk.Canvas):
    """
    Canvas-based button with glow-on-hover and optional pulse.

    Usage:
        btn = HoloButton(parent, text="Launch", command=my_func,
                         color=SF_ACCENT)
        btn.pack()
    """

    HOVER_MS    = 30
    HOVER_STEPS = 8

    def __init__(self, parent, text: str = "BUTTON",
                 command=None,
                 width: int = 140, height: int = 34,
                 color: str = SF_ACCENT,
                 bg_color: str = SF_PANEL,
                 font_size: int = 9,
                 **kwargs):
        super().__init__(parent, width=width, height=height,
                         bg=bg_color, highlightthickness=0, **kwargs)
        self._text     = text
        self._command  = command
        self._color    = color
        self._bg_color = bg_color
        self._w        = width
        self._h        = height
        self._hovering = False
        self._hover_t  = 0.0
        self._hover_job= None

        self._font = tkfont.Font(family="Consolas",
                                  size=font_size, weight="bold")

        # Draw base state
        self._bg_rect = self.create_rectangle(
            2, 2, width - 2, height - 2,
            fill=bg_color, outline=color, width=1)
        self._label   = self.create_text(
            width // 2, height // 2,
            text=text, fill=color,
            font=self._font)

        self.bind("<Enter>",    self._on_enter)
        self.bind("<Leave>",    self._on_leave)
        self.bind("<Button-1>", self._on_click)

    def _on_enter(self, event):
        self._hovering = True
        self._animate_hover(1)

    def _on_leave(self, event):
        self._hovering = False
        self._animate_hover(-1)

    def _on_click(self, event):
        if self._command:
            self._command()

    def _animate_hover(self, direction: int):
        if self._hover_job:
            self.after_cancel(self._hover_job)
        step = 1 / self.HOVER_STEPS
        self._hover_t = max(0.0, min(1.0,
                             self._hover_t + direction * step))

        t        = self._hover_t
        fg_color = _lerp_color(self._color, SF_BG, t * 0.1)
        bg_glow  = _lerp_color(self._bg_color, self._color, t * 0.25)
        border   = _lerp_color(self._color, SF_ACCENT2, t)

        try:
            self.itemconfigure(self._bg_rect,
                               fill=bg_glow, outline=border,
                               width=1 + int(t * 2))
            self.itemconfigure(self._label, fill=fg_color)
        except tk.TclError:
            return

        if (direction == 1 and self._hover_t < 1.0) or \
           (direction == -1 and self._hover_t > 0.0):
            self._hover_job = self.after(
                self.HOVER_MS,
                lambda: self._animate_hover(direction))

    def configure_text(self, text: str):
        self._text = text
        try:
            self.itemconfigure(self._label, text=text)
        except Exception:
            pass


# ══════════════════════════════════════════════════════════
#  HOLO PANEL — tk.Frame with built-in animated border
# ══════════════════════════════════════════════════════════

class HoloPanel(tk.Frame):
    """
    A tk.Frame with an animated HoloBorder Canvas overlay.
    Drop-in replacement for tk.Frame in any layout.

    Usage:
        panel = HoloPanel(root, width=300, height=200,
                          border_color=SF_ACCENT, pulse=True)
        panel.pack()
        # Add children to panel.inner
        tk.Label(panel.inner, text="Hello").pack()
    """

    PAD = 6   # pixels from frame edge to inner border

    def __init__(self, master,
                 width: int = 300,
                 height: int = 200,
                 border_color: str = SF_ACCENT,
                 bg_color: str = SF_PANEL,
                 pulse: bool = True,
                 corner_brackets: bool = True,
                 scanlines: bool = False,
                 **kwargs):
        kwargs.setdefault("bg", bg_color)
        super().__init__(master, width=width, height=height, **kwargs)
        self._border_color = border_color
        self._bg_color     = bg_color
        self._pulse        = pulse
        self._w            = width
        self._h            = height

        # Canvas for border drawing
        self._canvas = tk.Canvas(self, width=width, height=height,
                                  bg=bg_color, highlightthickness=0)
        self._canvas.place(x=0, y=0)

        # Inner frame for child widgets (raised above canvas)
        p = self.PAD + 4
        self.inner = tk.Frame(self, bg=bg_color)
        self.inner.place(x=p, y=p, width=width - p*2,
                          height=height - p*2)

        # Border effect
        bp = self.PAD
        self._holo_border = HoloBorder(
            self._canvas,
            x1=bp, y1=bp, x2=width - bp, y2=height - bp,
            color=border_color,
            pulse=pulse,
            corner_brackets=corner_brackets)

        # Optional scanlines
        self._scanlines = None
        if scanlines:
            self._scanlines = ScanlineOverlay(
                self._canvas, width, height)

        self.bind("<Destroy>", self._on_destroy)

    def start(self):
        """Start animations."""
        self._holo_border.start()
        if self._scanlines:
            self._scanlines.start()

    def stop(self):
        """Stop animations."""
        self._holo_border.stop()
        if self._scanlines:
            self._scanlines.stop()

    def set_border_color(self, color: str):
        self._border_color = color
        self._holo_border.set_color(color)

    def _on_destroy(self, event):
        self._holo_border.destroy()
        if self._scanlines:
            self._scanlines.destroy()


# ══════════════════════════════════════════════════════════
#  CONVENIENCE WRAPPERS
# ══════════════════════════════════════════════════════════

def add_scanline_overlay(canvas: tk.Canvas,
                          width: int, height: int,
                          animate: bool = False) -> ScanlineOverlay:
    """Add scanline effect to any existing Canvas."""
    overlay = ScanlineOverlay(canvas, width, height,
                               animate_scroll=animate)
    if animate:
        overlay.start()
    return overlay


def add_corner_brackets(canvas: tk.Canvas,
                         x1, y1, x2, y2,
                         color: str = SF_ACCENT,
                         size: int = 14,
                         thickness: int = 2) -> list:
    """Draw sci-fi corner bracket decorations on a Canvas. Returns item IDs."""
    items = []
    def bracket(ax, ay, dx, dy):
        h = canvas.create_line(ax, ay, ax + dx * size, ay,
                                fill=color, width=thickness)
        v = canvas.create_line(ax, ay, ax, ay + dy * size,
                                fill=color, width=thickness)
        items.extend([h, v])
    bracket(x1, y1,  1,  1)
    bracket(x2, y1, -1,  1)
    bracket(x1, y2,  1, -1)
    bracket(x2, y2, -1, -1)
    return items


def pulse_widget_border(widget: tk.Widget,
                         color: str = SF_ACCENT,
                         duration_ms: int = 400,
                         steps: int = 10):
    """
    One-shot pulse flash of a widget's highlightbackground.
    Good for 'success' or 'error' feedback.
    """
    orig = widget.cget("highlightbackground")
    step_ms = duration_ms // (steps * 2)

    def fade_in(i=0):
        if i > steps:
            fade_out(0)
            return
        c = _lerp_color(orig, color, i / steps)
        try:
            widget.configure(highlightbackground=c,
                              highlightthickness=2)
            widget.after(step_ms, lambda: fade_in(i + 1))
        except Exception:
            pass

    def fade_out(i=0):
        if i > steps:
            try:
                widget.configure(highlightbackground=orig,
                                  highlightthickness=0)
            except Exception:
                pass
            return
        c = _lerp_color(color, orig, i / steps)
        try:
            widget.configure(highlightbackground=c)
            widget.after(step_ms, lambda: fade_out(i + 1))
        except Exception:
            pass

    fade_in()


# ══════════════════════════════════════════════════════════
#  STANDALONE DEMO
# ══════════════════════════════════════════════════════════

if __name__ == "__main__":
    root = tk.Tk()
    root.title("⬡  Starfield Holo Effects — Demo")
    root.configure(bg=SF_BG)
    root.geometry("760x540")

    f_title = tkfont.Font(family="Consolas", size=13, weight="bold")
    f_body  = tkfont.Font(family="Consolas", size=9)

    # Title
    tk.Label(root, text="⬡  HOLO EFFECTS SHOWCASE",
             bg=SF_BG, fg=SF_ACCENT, font=f_title).pack(pady=(14, 6))

    # ── Row of HoloPanels ──
    row = tk.Frame(root, bg=SF_BG)
    row.pack(pady=10)

    panels = []
    configs = [
        ("CYAN PULSE",   SF_ACCENT,  SF_PANEL,       True,  False),
        ("ORANGE ALERT", SF_ORANGE,  "#150B00",       True,  False),
        ("GREEN SCAN",   SF_GREEN,   "#001510",       True,  True),
        ("AMBER STATIC", SF_AMBER,   "#15110A",       False, True),
    ]
    for label, color, bg, pulse, scan in configs:
        p = HoloPanel(row, width=160, height=130,
                      border_color=color, bg_color=bg,
                      pulse=pulse, scanlines=scan)
        p.pack(side="left", padx=10)
        tk.Label(p.inner, text=label, bg=bg, fg=color,
                 font=f_body).pack(pady=8)
        tk.Label(p.inner, text="status: OK",
                 bg=bg, fg=SF_DIM, font=f_body).pack()
        p.start()
        panels.append(p)

    # ── HoloButtons row ──
    btn_row = tk.Frame(root, bg=SF_BG)
    btn_row.pack(pady=16)
    tk.Label(btn_row, text="HOLO BUTTONS  (hover to glow)",
             bg=SF_BG, fg=SF_DIM, font=f_body).pack()
    btns_row2 = tk.Frame(root, bg=SF_BG)
    btns_row2.pack()
    for label, color in [
        ("▶  LAUNCH",  SF_ACCENT),
        ("★  FAVORITE", SF_AMBER),
        ("⚡  BATCH",  SF_ORANGE),
        ("✖  CLOSE",  SF_RED),
    ]:
        HoloButton(btns_row2, text=label, color=color,
                   width=150, height=36,
                   command=lambda l=label: print(f"Clicked: {l}")
                   ).pack(side="left", padx=8)

    # ── Corner brackets demo ──
    demo_canvas = tk.Canvas(root, width=380, height=110,
                             bg=SF_PANEL, highlightthickness=0)
    demo_canvas.pack(pady=10)
    demo_canvas.create_text(190, 30, text="add_corner_brackets()",
                              fill=SF_DIM, font=f_body)
    demo_canvas.create_text(190, 55, text="Scan-line + corner demo",
                              fill=SF_TEXT, font=f_body)
    add_corner_brackets(demo_canvas, 10, 10, 370, 100,
                         color=SF_ACCENT2, size=16)
    add_scanline_overlay(demo_canvas, 380, 110, animate=False)

    # ── pulse_widget_border demo ──
    demo_btn_frame = tk.Frame(root, bg=SF_BG)
    demo_btn_frame.pack(pady=6)

    demo_entry = tk.Entry(demo_btn_frame, width=22,
                           bg=SF_PANEL, fg=SF_TEXT,
                           font=f_body, highlightthickness=1,
                           highlightbackground=SF_BORDER)
    demo_entry.insert(0, " Click 'Flash' to pulse")
    demo_entry.pack(side="left", padx=6)
    tk.Button(demo_btn_frame, text="Flash Border",
              bg=SF_ACCENT, fg=SF_BG, font=f_body,
              relief="flat",
              command=lambda: pulse_widget_border(
                  demo_entry, SF_ACCENT)).pack(side="left")

    root.mainloop()
