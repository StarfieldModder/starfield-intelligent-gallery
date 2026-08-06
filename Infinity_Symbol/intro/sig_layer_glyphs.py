r"""
sig_layer_glyphs.py — Random Glyph Entrances
SIG Intro Engine Module 2
Loads vector glyph assets (SVG), randomises entry paths, staggers timing,
and handles collision avoidance.
"""
from __future__ import annotations
import math
import os
import random
import xml.etree.ElementTree as ET
from dataclasses import dataclass, field
from typing import List, Optional, Tuple

import numpy as np

# ---------------------------------------------------------------------------
# Easing
# ---------------------------------------------------------------------------

def ease_out_back(t: float, overshoot: float = 1.70158) -> float:
    c3 = overshoot + 1.0
    c1 = overshoot
    return 1.0 + c3 * (t - 1.0) ** 3 + c1 * (t - 1.0) ** 2

def ease_out_cubic(t: float) -> float:
    return 1.0 - (1.0 - t) ** 3

def ease_in_expo(t: float) -> float:
    return 0.0 if t == 0.0 else 2.0 ** (10.0 * t - 10.0)

# ---------------------------------------------------------------------------
# Entry path generators (normalised 0..1 space)
# ---------------------------------------------------------------------------

def path_linear(t: float, src: Tuple[float,float], dst: Tuple[float,float]) -> Tuple[float,float]:
    return (src[0] + (dst[0]-src[0])*t, src[1] + (dst[1]-src[1])*t)

def path_arc(t: float, src: Tuple[float,float], dst: Tuple[float,float],
             arc_height: float = 0.25) -> Tuple[float,float]:
    x = src[0] + (dst[0]-src[0])*t
    y = src[1] + (dst[1]-src[1])*t - arc_height * math.sin(math.pi * t)
    return (x, y)

def path_spiral(t: float, src: Tuple[float,float], dst: Tuple[float,float],
                turns: float = 1.0) -> Tuple[float,float]:
    angle = turns * 2.0 * math.pi * t
    r = (1.0 - t) * 0.35
    mx = (src[0]+dst[0])/2; my = (src[1]+dst[1])/2
    bx = src[0]+(dst[0]-src[0])*t; by = src[1]+(dst[1]-src[1])*t
    return (bx + r*math.cos(angle), by + r*math.sin(angle))

PATHS = {"linear": path_linear, "arc": path_arc, "spiral": path_spiral}

# ---------------------------------------------------------------------------
# Glyph data classes
# ---------------------------------------------------------------------------

@dataclass
class GlyphParams:
    svg_path: str               # path to SVG file
    final_pos: Tuple[float,float]   # normalised (x,y) centre
    scale: float = 1.0
    rotation_deg: float = 0.0
    color_tint: Tuple[int,int,int,int] = (0, 220, 255, 255)
    start_time: float = 0.0     # normalised [0,1]
    duration: float = 0.4
    entry_path: str = "arc"
    easing: str = "back"
    audio_trigger: Optional[str] = None  # event name string

@dataclass
class GlyphsLayerConfig:
    asset_dir: str = "assets/glyphs"
    num_glyphs: int = 6
    collision_margin: float = 0.08   # normalised units
    seed: Optional[int] = None

# ---------------------------------------------------------------------------
# Collision avoidance (simple rejection sampling)
# ---------------------------------------------------------------------------

def _no_collision(pos: Tuple[float,float], placed: List[Tuple[float,float]],
                  margin: float) -> bool:
    for p in placed:
        dx = pos[0]-p[0]; dy = pos[1]-p[1]
        if math.hypot(dx, dy) < margin:
            return False
    return True

def _random_pos(rng: random.Random, margin: float, placed: List[Tuple[float,float]],
                max_tries: int = 40) -> Tuple[float,float]:
    for _ in range(max_tries):
        pos = (rng.uniform(0.1, 0.9), rng.uniform(0.1, 0.9))
        if _no_collision(pos, placed, margin):
            return pos
    return (rng.uniform(0.1, 0.9), rng.uniform(0.1, 0.9))

# ---------------------------------------------------------------------------
# SVG rasterisation (Pillow-based, colour-tinted)
# ---------------------------------------------------------------------------

def _rasterise_svg(svg_path: str, size: int,
                   tint: Tuple[int,int,int,int]) -> Optional[np.ndarray]:
    """Return RGBA numpy array of rendered SVG at given size, or None on error."""
    try:
        # Try cairosvg first (optional high-quality)
        import cairosvg
        png_bytes = cairosvg.svg2png(url=svg_path, output_width=size, output_height=size)
        from PIL import Image
        import io
        img = Image.open(io.BytesIO(png_bytes)).convert("RGBA")
    except Exception:
        # Fallback: draw a placeholder shape
        try:
            from PIL import Image, ImageDraw
            img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
            draw = ImageDraw.Draw(img)
            pts = [(size//2, 4), (size-4, size-4), (4, size-4)]
            draw.polygon(pts, fill=tint)
        except Exception:
            return None
    # Apply tint: blend SVG alpha with tint colour
    arr = np.array(img, dtype=np.float32)
    alpha = arr[:,:,3:4] / 255.0
    tint_arr = np.array([[[tint[0], tint[1], tint[2], 255]]], dtype=np.float32)
    arr[:,:,:3] = arr[:,:,:3] * (1.0-0.7) + tint_arr[:,:,:3] * 0.7
    arr[:,:,3] = (alpha[:,:,0] * tint[3]).astype(np.float32)
    return np.clip(arr, 0, 255).astype(np.uint8)

# ---------------------------------------------------------------------------
# Compositing helper
# ---------------------------------------------------------------------------

def _composite_over(dst: np.ndarray, src: np.ndarray, x: int, y: int) -> None:
    """Alpha-composite src (RGBA) over dst at pixel (x,y) top-left."""
    H, W = dst.shape[:2]
    sh, sw = src.shape[:2]
    # Clip
    x0d = max(x, 0); y0d = max(y, 0)
    x1d = min(x+sw, W); y1d = min(y+sh, H)
    x0s = x0d-x; y0s = y0d-y
    x1s = x0s+(x1d-x0d); y1s = y0s+(y1d-y0d)
    if x1d<=x0d or y1d<=y0d:
        return
    s = src[y0s:y1s, x0s:x1s].astype(np.float32)
    d = dst[y0d:y1d, x0d:x1d].astype(np.float32)
    sa = s[:,:,3:4]/255.0
    da = d[:,:,3:4]/255.0
    out_a = sa + da*(1.0-sa)
    out_rgb = (s[:,:,:3]*sa + d[:,:,:3]*da*(1.0-sa)) / np.maximum(out_a, 1e-6)
    result = np.concatenate([out_rgb, out_a*255.0], axis=2)
    dst[y0d:y1d, x0d:x1d] = np.clip(result, 0, 255).astype(np.uint8)

# ---------------------------------------------------------------------------
# Main layer functions
# ---------------------------------------------------------------------------

def discover_svgs(asset_dir: str) -> List[str]:
    """Return all .svg files in asset_dir."""
    if not os.path.isdir(asset_dir):
        return []
    return sorted(
        os.path.join(asset_dir, f)
        for f in os.listdir(asset_dir)
        if f.lower().endswith(".svg")
    )

def generate_glyphs(cfg: GlyphsLayerConfig,
                    rng: Optional[random.Random] = None) -> List[GlyphParams]:
    if rng is None:
        rng = random.Random(cfg.seed)
    svgs = discover_svgs(cfg.asset_dir)
    placed: List[Tuple[float,float]] = []
    glyphs: List[GlyphParams] = []
    palette = [
        (0, 220, 255, 230), (0, 180, 230, 200),
        (100, 255, 220, 210), (180, 120, 255, 200),
        (255, 200, 60, 200), (60, 255, 160, 220),
    ]
    easings = ["back", "cubic"]
    audio_events = ["click", "spark", "whoosh", None, None]
    for i in range(cfg.num_glyphs):
        pos = _random_pos(rng, cfg.collision_margin, placed)
        placed.append(pos)
        svg = svgs[i % len(svgs)] if svgs else ""
        color = rng.choice(palette)
        start = rng.uniform(0.0, 0.55)
        dur = rng.uniform(0.25, 0.45)
        entry = rng.choice(list(PATHS.keys()))
        easing = rng.choice(easings)
        audio = rng.choice(audio_events)
        glyphs.append(GlyphParams(
            svg_path=svg,
            final_pos=pos,
            scale=rng.uniform(0.6, 1.4),
            rotation_deg=rng.uniform(-25, 25),
            color_tint=color,
            start_time=start,
            duration=dur,
            entry_path=entry,
            easing=easing,
            audio_trigger=audio,
        ))
    return glyphs


def render_glyphs_frame(
    canvas: np.ndarray,
    glyphs: List[GlyphParams],
    layer_t: float,
    glyph_size: int = 48,
) -> np.ndarray:
    H, W = canvas.shape[:2]
    for g in glyphs:
        if layer_t < g.start_time:
            continue
        local_t = (layer_t - g.start_time) / max(g.duration, 1e-6)
        local_t = min(local_t, 1.0)
        fn = {"back": ease_out_back, "cubic": ease_out_cubic,
              "expo": ease_in_expo}.get(g.easing, ease_out_cubic)
        eased = fn(local_t)
        # Source position: approach from a random edge
        src = (0.5, -0.2)  # top-centre default
        path_fn = PATHS.get(g.entry_path, path_linear)
        px, py = path_fn(eased, src, g.final_pos)
        px_px = int(px * W - glyph_size // 2)
        py_px = int(py * H - glyph_size // 2)
        alpha_mult = min(1.0, local_t / 0.15)
        sz = max(8, int(glyph_size * g.scale))
        glyph_arr = _rasterise_svg(g.svg_path, sz, g.color_tint)
        if glyph_arr is None:
            continue
        # Fade-in
        glyph_arr = glyph_arr.copy().astype(np.float32)
        glyph_arr[:,:,3] *= alpha_mult
        glyph_arr = np.clip(glyph_arr, 0, 255).astype(np.uint8)
        _composite_over(canvas, glyph_arr, px_px, py_px)
    return canvas


def generate_glyphs_frames(
    width: int, height: int,
    num_frames: int,
    cfg: Optional[GlyphsLayerConfig] = None,
    seed: Optional[int] = None,
) -> List[np.ndarray]:
    if cfg is None:
        cfg = GlyphsLayerConfig(seed=seed)
    rng = random.Random(cfg.seed if cfg.seed is not None else seed)
    glyphs = generate_glyphs(cfg, rng)
    frames = []
    for i in range(num_frames):
        t = i / max(num_frames-1, 1)
        canvas = np.zeros((height, width, 4), dtype=np.uint8)
        render_glyphs_frame(canvas, glyphs, t)
        frames.append(canvas)
    return frames


if __name__ == "__main__":
    print("sig_layer_glyphs: self-test")
    cfg = GlyphsLayerConfig(num_glyphs=3, seed=7)
    frames = generate_glyphs_frames(320, 240, 8, cfg=cfg)
    print(f"Generated {len(frames)} frames OK")

