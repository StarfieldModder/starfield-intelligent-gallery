r"""
sig_layer_title.py — Title / SIG Logo Cinematic Entrance
SIG Intro Engine Module 5
Typographic animation with kerning/scale easing and a final shimmer pass.
"""
from __future__ import annotations
import math
import random
from dataclasses import dataclass, field
from typing import List, Optional, Tuple

import numpy as np


# ---------------------------------------------------------------------------
# Easing
# ---------------------------------------------------------------------------

def ease_out_expo(t: float) -> float:
    return 1.0 if t >= 1.0 else 1.0 - 2.0 ** (-10.0 * t)

def ease_out_elastic(t: float, amplitude: float = 1.0, period: float = 0.3) -> float:
    if t == 0.0: return 0.0
    if t >= 1.0: return 1.0
    s = period / (2 * math.pi) * math.asin(1.0 / amplitude) if amplitude >= 1 else period / 4
    return amplitude * (2.0 ** (-10*t)) * math.sin((t - s) * 2*math.pi / period) + 1.0

def ease_in_out_cubic(t: float) -> float:
    return 4*t**3 if t < 0.5 else 1 - (-2*t+2)**3/2


# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------

@dataclass
class TitleConfig:
    title_text: str = "SIG"
    subtitle_text: str = "Strategic Intelligence Gateway"
    title_font_size: int = 96            # px (approximate at 1080p)
    subtitle_font_size: int = 28
    title_color: Tuple[int,int,int,int] = (0, 230, 255, 255)
    subtitle_color: Tuple[int,int,int,int] = (140, 220, 255, 200)
    glow_color: Tuple[int,int,int,int] = (0, 180, 255, 60)
    bg_color: Tuple[int,int,int,int] = (0, 0, 0, 0)  # transparent
    # Animation phases (normalised [0,1] within layer duration)
    char_stagger: float = 0.06       # delay between characters
    title_entry_start: float = 0.05
    title_entry_duration: float = 0.40
    subtitle_entry_start: float = 0.45
    subtitle_entry_duration: float = 0.30
    shimmer_start: float = 0.75
    # Scale overshoot on entry
    scale_overshoot: float = 1.20
    seed: Optional[int] = None


# ---------------------------------------------------------------------------
# Text rendering helpers (Pillow)
# ---------------------------------------------------------------------------

def _get_font(size: int):
    try:
        from PIL import ImageFont
        # Try common system fonts
        for name in [
            "DejaVuSans-Bold.ttf", "Arial Bold.ttf", "arialbd.ttf",
            "LiberationSans-Bold.ttf", "FreeSansBold.ttf",
        ]:
            try:
                return ImageFont.truetype(name, size)
            except Exception:
                pass
        return ImageFont.load_default()
    except Exception:
        return None


def _text_size(text: str, font) -> Tuple[int, int]:
    try:
        from PIL import Image, ImageDraw
        img = Image.new("RGBA", (1, 1))
        draw = ImageDraw.Draw(img)
        bbox = draw.textbbox((0, 0), text, font=font)
        return bbox[2] - bbox[0], bbox[3] - bbox[1]
    except Exception:
        return len(text) * 10, 16


def _draw_text_glow(draw, pos: Tuple[int,int], text: str, font,
                    glow_color: Tuple[int,int,int,int], passes: int = 4) -> None:
    x, y = pos
    for p in range(1, passes+1):
        spread = p * 2
        a = max(0, glow_color[3] - p * 12)
        gc = (glow_color[0], glow_color[1], glow_color[2], a)
        for dx, dy in [(-spread,0),(spread,0),(0,-spread),(0,spread),
                       (-spread,-spread),(spread,spread),(-spread,spread),(spread,-spread)]:
            draw.text((x+dx, y+dy), text, font=font, fill=gc)


def _shimmer_pass(canvas: np.ndarray, t: float, shimmer_start: float,
                  rng: random.Random) -> None:
    """Add horizontal shimmer/glint sweep across bright pixels."""
    if t < shimmer_start:
        return
    phase = (t - shimmer_start) / (1.0 - shimmer_start + 1e-6)
    sweep_x = int(phase * canvas.shape[1])
    H, W = canvas.shape[:2]
    half = max(1, W // 12)
    x0 = max(0, sweep_x - half); x1 = min(W, sweep_x + half)
    if x1 <= x0:
        return
    # Brightness ramp
    ramp = np.abs(np.linspace(-1, 1, x1-x0))
    ramp = 1.0 - ramp
    ramp = ramp[np.newaxis, :, np.newaxis]
    # Only brighten pixels that already have alpha > 50
    mask = canvas[:, x0:x1, 3] > 50
    boost = (ramp * 80 * mask[:, :, np.newaxis]).astype(np.uint8)
    for c in range(3):
        canvas[:, x0:x1, c] = np.minimum(255,
            canvas[:, x0:x1, c].astype(int) + boost[:, :, 0]).astype(np.uint8)


# ---------------------------------------------------------------------------
# Per-character animation
# ---------------------------------------------------------------------------

def _render_char_animated(
    text: str,
    char_index: int,
    local_t: float,
    canvas: np.ndarray,
    base_x: int, base_y: int,
    char_width: int, font,
    color: Tuple[int,int,int,int],
    glow_color: Tuple[int,int,int,int],
    scale_overshoot: float,
    easing_fn,
) -> None:
    """Render a single character with scale + alpha animation."""
    try:
        from PIL import Image, ImageDraw
    except ImportError:
        return

    local_t = max(0.0, min(1.0, local_t))
    eased = easing_fn(local_t)

    # Scale: starts at scale_overshoot, settles to 1.0
    scale = scale_overshoot - (scale_overshoot - 1.0) * eased
    alpha = int(color[3] * min(1.0, local_t / 0.2))
    if alpha <= 0:
        return

    H, W = canvas.shape[:2]
    char = text[char_index] if char_index < len(text) else " "
    tw, th = _text_size(char, font)
    fsz = max(8, int(font.size * scale)) if hasattr(font, 'size') else 16
    scaled_font = _get_font(fsz)
    if scaled_font is None:
        return

    tw2, th2 = _text_size(char, scaled_font)
    px = base_x + char_index * char_width + (char_width - tw2) // 2
    py = base_y - (th2 - th) // 2  # keep baseline

    # Draw to small offscreen, composite
    pad = 20
    off_w = tw2 + pad*2; off_h = th2 + pad*2
    off = Image.new("RGBA", (off_w, off_h), (0,0,0,0))
    d = ImageDraw.Draw(off)
    c_alpha = (color[0], color[1], color[2], alpha)
    _draw_text_glow(d, (pad, pad), char, scaled_font, glow_color)
    d.text((pad, pad), char, font=scaled_font, fill=c_alpha)

    arr = np.array(off)
    # Composite onto canvas
    dx = px - pad; dy = py - pad
    _comp(canvas, arr, dx, dy)


def _comp(dst: np.ndarray, src: np.ndarray, x: int, y: int) -> None:
    H, W = dst.shape[:2]; sh, sw = src.shape[:2]
    x0d = max(x,0); y0d = max(y,0)
    x1d = min(x+sw,W); y1d = min(y+sh,H)
    x0s = x0d-x; y0s = y0d-y
    x1s = x0s+(x1d-x0d); y1s = y0s+(y1d-y0d)
    if x1d<=x0d or y1d<=y0d: return
    s = src[y0s:y1s,x0s:x1s].astype(np.float32)
    d = dst[y0d:y1d,x0d:x1d].astype(np.float32)
    sa = s[:,:,3:4]/255.0; da = d[:,:,3:4]/255.0
    oa = sa + da*(1-sa)
    oc = (s[:,:,:3]*sa + d[:,:,:3]*da*(1-sa)) / np.maximum(oa,1e-6)
    dst[y0d:y1d,x0d:x1d] = np.concatenate([oc.clip(0,255), (oa*255).clip(0,255)], axis=2).astype(np.uint8)


# ---------------------------------------------------------------------------
# Main render
# ---------------------------------------------------------------------------

def render_title_frame(
    canvas: np.ndarray,
    cfg: TitleConfig,
    layer_t: float,
    rng: Optional[random.Random] = None,
) -> np.ndarray:
    if rng is None:
        rng = random.Random(cfg.seed)
    H, W = canvas.shape[:2]
    try:
        from PIL import Image, ImageDraw
    except ImportError:
        return canvas

    # Scale font sizes to canvas
    scale = min(W / 1920, H / 1080)
    t_size = max(12, int(cfg.title_font_size * scale))
    s_size = max(8, int(cfg.subtitle_font_size * scale))
    t_font = _get_font(t_size)
    s_font = _get_font(s_size)
    if t_font is None or s_font is None:
        return canvas

    # Title chars
    title = cfg.title_text
    num_chars = len(title)
    tw, th = _text_size(title, t_font)
    char_w = tw // max(1, num_chars)
    t_base_x = (W - tw) // 2
    t_base_y = int(H * 0.42) - th // 2

    for i, ch in enumerate(title):
        char_start = cfg.title_entry_start + i * cfg.char_stagger
        char_dur = cfg.title_entry_duration
        if layer_t < char_start:
            continue
        local_t = (layer_t - char_start) / max(char_dur, 1e-6)
        _render_char_animated(
            title, i, local_t, canvas,
            t_base_x, t_base_y, char_w,
            t_font, cfg.title_color, cfg.glow_color,
            cfg.scale_overshoot, ease_out_elastic,
        )

    # Subtitle (fade in as a whole)
    if layer_t >= cfg.subtitle_entry_start:
        sub_t = (layer_t - cfg.subtitle_entry_start) / max(cfg.subtitle_entry_duration, 1e-6)
        sub_t = min(1.0, sub_t)
        eased_sub = ease_out_expo(sub_t)
        alpha_sub = int(cfg.subtitle_color[3] * min(1.0, sub_t / 0.3))
        if alpha_sub > 0:
            sw2, sh2 = _text_size(cfg.subtitle_text, s_font)
            sx = (W - sw2) // 2
            sy = int(H * 0.42) + th // 2 + int(10 * scale)
            img = Image.fromarray(canvas, "RGBA")
            draw = ImageDraw.Draw(img, "RGBA")
            sc = cfg.subtitle_color
            _draw_text_glow(draw, (sx, sy), cfg.subtitle_text, s_font,
                            cfg.glow_color, passes=2)
            draw.text((sx, sy), cfg.subtitle_text, font=s_font,
                      fill=(sc[0], sc[1], sc[2], alpha_sub))
            canvas[:] = np.array(img)

    # Shimmer
    _shimmer_pass(canvas, layer_t, cfg.shimmer_start, rng)
    return canvas


def generate_title_frames(
    width: int, height: int,
    num_frames: int,
    cfg: Optional[TitleConfig] = None,
    seed: Optional[int] = None,
) -> List[np.ndarray]:
    if cfg is None:
        cfg = TitleConfig(seed=seed)
    rng = random.Random(cfg.seed if cfg.seed is not None else seed)
    frames = []
    for i in range(num_frames):
        t = i / max(num_frames-1, 1)
        canvas = np.zeros((height, width, 4), dtype=np.uint8)
        render_title_frame(canvas, cfg, t, rng)
        frames.append(canvas)
    return frames


if __name__ == "__main__":
    print("sig_layer_title: self-test")
    frames = generate_title_frames(320, 240, 10, seed=77)
    print(f"Generated {len(frames)} frames OK")

