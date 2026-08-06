r"""
sig_layer_hologrid.py — Hologram Grid Activation
SIG Intro Engine Module 3
Renders a holographic grid with scanlines, shimmer, and parallax depth.
CPU-based with numpy/Pillow; shader-like FX via multi-pass compositing.
"""
from __future__ import annotations
import math
import random
from dataclasses import dataclass
from typing import List, Optional, Tuple

import numpy as np


# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------

@dataclass
class HologridConfig:
    grid_color: Tuple[int,int,int,int] = (0, 200, 255, 160)
    shimmer_color: Tuple[int,int,int,int] = (180, 255, 255, 80)
    scanline_color: Tuple[int,int,int,int] = (0, 180, 255, 30)
    cell_size_frac: float = 0.06       # cell size as fraction of min(W,H)
    grid_layers: int = 3               # parallax depth layers
    scanline_speed: float = 0.4        # scanlines travel speed (0..1 per second)
    shimmer_rate: float = 8.0          # Hz
    activation_start: float = 0.05    # layer_t when grid starts appearing
    activation_duration: float = 0.55
    seed: Optional[int] = None


# ---------------------------------------------------------------------------
# Grid helpers
# ---------------------------------------------------------------------------

def _draw_grid(canvas: np.ndarray,
               cell_w: int, cell_h: int,
               offset_x: float, offset_y: float,
               color: Tuple[int,int,int,int],
               alpha_mult: float = 1.0) -> None:
    """Draw axis-aligned grid lines directly into RGBA numpy array."""
    H, W = canvas.shape[:2]
    r, g, b, a_base = color
    a = int(a_base * alpha_mult)
    if a <= 0:
        return

    # Vertical lines
    x = int(offset_x % cell_w) - cell_w
    while x < W:
        if 0 <= x < W:
            canvas[:, x, 0] = np.minimum(255, canvas[:, x, 0].astype(int) + r).astype(np.uint8)
            canvas[:, x, 1] = np.minimum(255, canvas[:, x, 1].astype(int) + g).astype(np.uint8)
            canvas[:, x, 2] = np.minimum(255, canvas[:, x, 2].astype(int) + b).astype(np.uint8)
            canvas[:, x, 3] = np.minimum(255, canvas[:, x, 3].astype(int) + a).astype(np.uint8)
        x += cell_w

    # Horizontal lines
    y = int(offset_y % cell_h) - cell_h
    while y < H:
        if 0 <= y < H:
            canvas[y, :, 0] = np.minimum(255, canvas[y, :, 0].astype(int) + r).astype(np.uint8)
            canvas[y, :, 1] = np.minimum(255, canvas[y, :, 1].astype(int) + g).astype(np.uint8)
            canvas[y, :, 2] = np.minimum(255, canvas[y, :, 2].astype(int) + b).astype(np.uint8)
            canvas[y, :, 3] = np.minimum(255, canvas[y, :, 3].astype(int) + a).astype(np.uint8)
        y += cell_h


def _draw_scanlines(canvas: np.ndarray,
                    color: Tuple[int,int,int,int],
                    scan_y: float,
                    beam_height: int = 6) -> None:
    """Draw a horizontal scanline beam sweeping down."""
    H, W = canvas.shape[:2]
    r, g, b, a_base = color
    y_center = int(scan_y * H) % H
    for dy in range(-beam_height, beam_height+1):
        y = (y_center + dy) % H
        falloff = 1.0 - abs(dy) / (beam_height + 1)
        a = int(a_base * falloff)
        canvas[y, :, 0] = np.minimum(255, canvas[y, :, 0].astype(int) + int(r*falloff)).astype(np.uint8)
        canvas[y, :, 1] = np.minimum(255, canvas[y, :, 1].astype(int) + int(g*falloff)).astype(np.uint8)
        canvas[y, :, 2] = np.minimum(255, canvas[y, :, 2].astype(int) + int(b*falloff)).astype(np.uint8)
        canvas[y, :, 3] = np.minimum(255, canvas[y, :, 3].astype(int) + a).astype(np.uint8)


def _add_shimmer(canvas: np.ndarray,
                 color: Tuple[int,int,int,int],
                 t: float, shimmer_rate: float,
                 rng: random.Random) -> None:
    """Random pixel sparkle/shimmer overlay."""
    H, W = canvas.shape[:2]
    phase = math.sin(2 * math.pi * shimmer_rate * t)
    intensity = max(0.0, phase)
    if intensity < 0.05:
        return
    num_sparks = int(intensity * 120)
    r, g, b, a_base = color
    for _ in range(num_sparks):
        px = rng.randint(0, W-1)
        py = rng.randint(0, H-1)
        spark_a = int(a_base * intensity * rng.random())
        canvas[py, px, 0] = min(255, int(canvas[py, px, 0]) + r)
        canvas[py, px, 1] = min(255, int(canvas[py, px, 1]) + g)
        canvas[py, px, 2] = min(255, int(canvas[py, px, 2]) + b)
        canvas[py, px, 3] = min(255, int(canvas[py, px, 3]) + spark_a)


# ---------------------------------------------------------------------------
# Main render
# ---------------------------------------------------------------------------

def render_hologrid_frame(
    canvas: np.ndarray,
    cfg: HologridConfig,
    layer_t: float,
    wall_time: float = 0.0,   # real elapsed seconds (for animation)
    rng: Optional[random.Random] = None,
) -> np.ndarray:
    """Render hologram grid onto RGBA canvas for this frame."""
    if rng is None:
        rng = random.Random(cfg.seed)
    H, W = canvas.shape[:2]
    ref = min(W, H)

    # Activation envelope
    if layer_t < cfg.activation_start:
        return canvas
    act_t = (layer_t - cfg.activation_start) / max(cfg.activation_duration, 1e-6)
    act_t = min(1.0, act_t)
    # Ease in
    act_alpha = 1.0 - (1.0 - act_t) ** 2

    base_cell = max(4, int(cfg.cell_size_frac * ref))

    for layer_idx in range(cfg.grid_layers):
        # Each depth layer has slightly different cell size & offset
        depth_frac = (layer_idx + 1) / cfg.grid_layers
        cell_w = max(4, int(base_cell * (0.7 + 0.6 * depth_frac)))
        cell_h = cell_w
        # Parallax: deeper layers drift more slowly
        drift_x = wall_time * 8.0 * depth_frac
        drift_y = wall_time * 4.0 * depth_frac
        layer_alpha = act_alpha * (0.4 + 0.6 * depth_frac)
        # Dim deeper layers
        lc = cfg.grid_color
        dimmed = (lc[0], lc[1], lc[2], int(lc[3] * (0.3 + 0.7 * depth_frac)))
        _draw_grid(canvas, cell_w, cell_h, drift_x, drift_y, dimmed, layer_alpha)

    # Scanlines
    scan_y = (wall_time * cfg.scanline_speed) % 1.0
    _draw_scanlines(canvas, cfg.scanline_color, scan_y, beam_height=max(3, H//40))

    # Shimmer
    _add_shimmer(canvas, cfg.shimmer_color, wall_time, cfg.shimmer_rate, rng)

    return canvas


def generate_hologrid_frames(
    width: int, height: int,
    num_frames: int,
    fps: float = 24.0,
    cfg: Optional[HologridConfig] = None,
    seed: Optional[int] = None,
) -> List[np.ndarray]:
    if cfg is None:
        cfg = HologridConfig(seed=seed)
    rng = random.Random(cfg.seed if cfg.seed is not None else seed)
    frames = []
    for i in range(num_frames):
        t = i / max(num_frames-1, 1)
        wt = i / fps
        canvas = np.zeros((height, width, 4), dtype=np.uint8)
        render_hologrid_frame(canvas, cfg, t, wt, rng)
        frames.append(canvas)
    return frames


if __name__ == "__main__":
    print("sig_layer_hologrid: self-test")
    cfg = HologridConfig(seed=99)
    frames = generate_hologrid_frames(320, 240, 10, cfg=cfg)
    print(f"Generated {len(frames)} frames, shape={frames[0].shape} — OK")

