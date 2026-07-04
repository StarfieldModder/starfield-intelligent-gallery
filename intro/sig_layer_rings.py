r"""
sig_layer_rings.py — Concentric Rings Expansion
SIG Intro Engine Module 1
Renders animated concentric rings expanding from a focal point with
randomized parameters and easing curves.
"""
from __future__ import annotations
import math
import random
from dataclasses import dataclass, field
from typing import List, Optional, Tuple

import numpy as np

# ---------------------------------------------------------------------------
# Easing functions
# ---------------------------------------------------------------------------

def ease_out_cubic(t: float) -> float:
    """Cubic ease-out: fast start, slow finish."""
    return 1.0 - (1.0 - t) ** 3

def ease_in_out_sine(t: float) -> float:
    """Sine ease-in-out."""
    return -(math.cos(math.pi * t) - 1.0) / 2.0

def ease_out_expo(t: float) -> float:
    """Exponential ease-out."""
    if t >= 1.0:
        return 1.0
    return 1.0 - 2.0 ** (-10.0 * t)

EASINGS = {
    "cubic": ease_out_cubic,
    "sine": ease_in_out_sine,
    "expo": ease_out_expo,
}

# ---------------------------------------------------------------------------
# Data classes
# ---------------------------------------------------------------------------

@dataclass
class RingParams:
    """Parameters for a single ring."""
    max_radius: float          # px at full expansion
    color: Tuple[int, int, int, int]  # RGBA 0-255
    line_width: float          # px
    start_time: float          # normalised [0,1] within layer duration
    duration: float            # fraction of layer total duration
    easing: str = "cubic"
    glow: bool = False
    dash_pattern: Optional[Tuple[int, int]] = None  # on/off px

@dataclass
class RingsLayerConfig:
    """Full configuration for the rings layer."""
    num_rings: int = 7
    center: Tuple[float, float] = (0.5, 0.5)   # normalised
    palette: List[Tuple[int, int, int, int]] = field(default_factory=lambda: [
        (0, 220, 255, 200),
        (0, 180, 255, 160),
        (100, 240, 255, 120),
        (0, 255, 200, 180),
    ])
    min_radius_frac: float = 0.15
    max_radius_frac: float = 0.70
    min_line_width: float = 1.0
    max_line_width: float = 3.5
    seed: Optional[int] = None

# ---------------------------------------------------------------------------
# Ring generator
# ---------------------------------------------------------------------------

def generate_rings(cfg: RingsLayerConfig, rng: Optional[random.Random] = None) -> List[RingParams]:
    """Return a randomised list of RingParams based on cfg."""
    if rng is None:
        rng = random.Random(cfg.seed)
    rings: List[RingParams] = []
    easings = list(EASINGS.keys())
    for i in range(cfg.num_rings):
        frac = cfg.min_radius_frac + rng.random() * (cfg.max_radius_frac - cfg.min_radius_frac)
        start = rng.uniform(0.0, 0.5)
        dur = rng.uniform(0.35, 0.75)
        dur = min(dur, 1.0 - start)
        color = rng.choice(cfg.palette)
        alpha_jitter = rng.randint(-30, 30)
        color = (color[0], color[1], color[2], max(40, min(255, color[3] + alpha_jitter)))
        lw = rng.uniform(cfg.min_line_width, cfg.max_line_width)
        easing_key = rng.choice(easings)
        glow = rng.random() < 0.4
        dash = (rng.randint(6, 18), rng.randint(3, 8)) if rng.random() < 0.3 else None
        rings.append(RingParams(
            max_radius=frac,   # stored as fraction; caller multiplies by canvas dim
            color=color,
            line_width=lw,
            start_time=start,
            duration=dur,
            easing=easing_key,
            glow=glow,
            dash_pattern=dash,
        ))
    return rings

# ---------------------------------------------------------------------------
# Renderer (CPU / numpy+Pillow)
# ---------------------------------------------------------------------------

def _draw_ring_on_array(
    canvas: np.ndarray,
    cx: int, cy: int,
    radius: float,
    color: Tuple[int, int, int, int],
    line_width: float,
    glow: bool,
    dash_pattern: Optional[Tuple[int, int]],
) -> None:
    """
    Draw a single ring onto an RGBA numpy array (H, W, 4).
    Uses anti-aliased Bresenham-style rasterisation with optional glow.
    """
    try:
        from PIL import Image, ImageDraw
    except ImportError:
        return  # graceful degradation

    H, W = canvas.shape[:2]
    img = Image.fromarray(canvas, mode="RGBA")
    draw = ImageDraw.Draw(img, "RGBA")

    r = int(radius)
    if r < 2:
        return

    lw = max(1, int(line_width))
    r0 = r - lw // 2
    r1 = r + lw // 2 + lw % 2

    if glow:
        # Draw several translucent larger rings for glow effect
        for g_step in range(1, 4):
            g_r = r + g_step * 3
            g_alpha = max(0, color[3] // (g_step * 2 + 1))
            g_color = (color[0], color[1], color[2], g_alpha)
            box = [cx - g_r, cy - g_r, cx + g_r, cy + g_r]
            draw.ellipse(box, outline=g_color, width=1)

    if dash_pattern is None:
        box = [cx - r, cy - r, cx + r, cy + r]
        draw.ellipse(box, outline=color, width=lw)
    else:
        on, off = dash_pattern
        period = on + off
        circumference = 2 * math.pi * r
        num_dashes = max(1, int(circumference / period))
        angle_on = (on / period) * (2 * math.pi / num_dashes)
        angle_off = (off / period) * (2 * math.pi / num_dashes)
        theta = 0.0
        for _ in range(num_dashes):
            start_deg = math.degrees(theta)
            end_deg = math.degrees(theta + angle_on)
            draw.arc([cx - r, cy - r, cx + r, cy + r],
                     start=start_deg, end=end_deg, fill=color, width=lw)
            theta += angle_on + angle_off

    canvas[:] = np.array(img)


def render_rings_frame(
    canvas: np.ndarray,
    rings: List[RingParams],
    layer_t: float,           # normalised time [0,1] for this layer
    canvas_dim: int,          # reference dimension (min of W, H)
) -> np.ndarray:
    """
    Composite rings onto canvas for layer_t ∈ [0,1].
    Returns the modified canvas (RGBA H×W×4 uint8).
    """
    H, W = canvas.shape[:2]
    cx = int(W * 0.5)
    cy = int(H * 0.5)

    for ring in rings:
        if layer_t < ring.start_time:
            continue
        local_t = (layer_t - ring.start_time) / max(ring.duration, 1e-6)
        local_t = max(0.0, min(1.0, local_t))
        eased = EASINGS.get(ring.easing, ease_out_cubic)(local_t)
        radius_px = ring.max_radius * canvas_dim * eased
        # Fade alpha in during first 20% then hold
        if local_t < 0.2:
            alpha_mult = local_t / 0.2
        else:
            alpha_mult = 1.0
        color = (
            ring.color[0], ring.color[1], ring.color[2],
            int(ring.color[3] * alpha_mult)
        )
        _draw_ring_on_array(
            canvas, cx, cy, radius_px,
            color, ring.line_width, ring.glow, ring.dash_pattern
        )
    return canvas


# ---------------------------------------------------------------------------
# Convenience: generate a sequence of frames as numpy arrays
# ---------------------------------------------------------------------------

def generate_rings_frames(
    width: int, height: int,
    num_frames: int,
    cfg: Optional[RingsLayerConfig] = None,
    seed: Optional[int] = None,
) -> List[np.ndarray]:
    """Return list of RGBA numpy arrays, one per frame."""
    if cfg is None:
        cfg = RingsLayerConfig(seed=seed)
    rng = random.Random(cfg.seed if cfg.seed is not None else seed)
    rings = generate_rings(cfg, rng)
    canvas_dim = min(width, height)
    frames = []
    for i in range(num_frames):
        t = i / max(num_frames - 1, 1)
        canvas = np.zeros((height, width, 4), dtype=np.uint8)
        render_rings_frame(canvas, rings, t, canvas_dim)
        frames.append(canvas)
    return frames


# ---------------------------------------------------------------------------
# Self-test (run as __main__)
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    import sys
    print("sig_layer_rings: self-test")
    cfg = RingsLayerConfig(num_rings=5, seed=42)
    frames = generate_rings_frames(320, 240, 10, cfg=cfg)
    print(f"Generated {len(frames)} frames, shape={frames[0].shape}")
    print("OK")

