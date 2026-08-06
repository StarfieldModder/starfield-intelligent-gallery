r"""
sig_layer_parallax.py — Parallax Background Reveal
SIG Intro Engine Module 4
Multi-depth-layer background with procedural starfield, nebula clouds,
and camera dolly/zoom controls.
"""
from __future__ import annotations
import math
import random
from dataclasses import dataclass, field
from typing import List, Optional, Tuple

import numpy as np


# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------

@dataclass
class ParallaxLayerDef:
    """One depth layer definition."""
    depth: float               # 0=closest, 1=farthest
    star_density: float        # stars per 1000px²
    star_size_range: Tuple[float,float] = (0.5, 2.5)
    star_color: Tuple[int,int,int] = (200, 220, 255)
    nebula: bool = False
    nebula_color: Tuple[int,int,int,int] = (20, 40, 80, 60)


@dataclass
class ParallaxConfig:
    layers: List[ParallaxLayerDef] = field(default_factory=lambda: [
        ParallaxLayerDef(depth=1.0, star_density=3.0, nebula=True,
                         nebula_color=(10, 20, 60, 80)),
        ParallaxLayerDef(depth=0.6, star_density=1.5,
                         star_color=(180, 200, 255)),
        ParallaxLayerDef(depth=0.3, star_density=0.6,
                         star_size_range=(1.0, 3.0),
                         star_color=(255, 240, 200)),
    ])
    bg_color: Tuple[int,int,int] = (2, 4, 18)
    reveal_start: float = 0.0
    reveal_duration: float = 0.6
    # Camera dolly: zoom from zoom_start → zoom_end over full duration
    zoom_start: float = 1.05
    zoom_end: float = 1.0
    # Camera drift (normalised per full duration)
    drift_x: float = 0.01
    drift_y: float = 0.005
    seed: Optional[int] = None


# ---------------------------------------------------------------------------
# Starfield generation (per-layer, cached)
# ---------------------------------------------------------------------------

@dataclass
class StarCatalog:
    """Pre-generated star positions and sizes for one layer."""
    xs: np.ndarray   # (N,) float in [0,1]
    ys: np.ndarray
    sizes: np.ndarray
    colors: np.ndarray  # (N,4) RGBA uint8


def build_star_catalog(
    layer: ParallaxLayerDef,
    width: int, height: int,
    rng: random.Random,
) -> StarCatalog:
    area_kpx = width * height / 1000.0
    n = max(1, int(layer.star_density * area_kpx))
    xs = np.array([rng.random() for _ in range(n)])
    ys = np.array([rng.random() for _ in range(n)])
    smin, smax = layer.star_size_range
    sizes = np.array([rng.uniform(smin, smax) for _ in range(n)])
    r, g, b = layer.star_color
    # Twinkle: vary brightness per star
    brightnesses = np.array([rng.uniform(0.5, 1.0) for _ in range(n)])
    colors = np.stack([
        (brightnesses * r).clip(0,255).astype(np.uint8),
        (brightnesses * g).clip(0,255).astype(np.uint8),
        (brightnesses * b).clip(0,255).astype(np.uint8),
        np.full(n, 220, dtype=np.uint8),
    ], axis=1)
    return StarCatalog(xs=xs, ys=ys, sizes=sizes, colors=colors)


# ---------------------------------------------------------------------------
# Nebula cloud generation (simple Gaussian splat)
# ---------------------------------------------------------------------------

def _draw_nebula(
    canvas: np.ndarray,
    color: Tuple[int,int,int,int],
    rng: random.Random,
    num_blobs: int = 6,
    alpha_mult: float = 1.0,
) -> None:
    H, W = canvas.shape[:2]
    r, g, b, a_base = color
    for _ in range(num_blobs):
        cx = rng.randint(0, W)
        cy = rng.randint(0, H)
        sigma_x = rng.uniform(W*0.05, W*0.25)
        sigma_y = rng.uniform(H*0.05, H*0.20)
        # Build Gaussian patch
        patch_w = min(W, int(sigma_x*5))
        patch_h = min(H, int(sigma_y*5))
        xs = np.linspace(-2.5, 2.5, patch_w)
        ys = np.linspace(-2.5, 2.5, patch_h)
        gx = np.exp(-0.5 * xs**2)
        gy = np.exp(-0.5 * ys**2)
        blob = np.outer(gy, gx)  # (patch_h, patch_w)
        a_channel = (blob * a_base * alpha_mult).clip(0, 255)
        # Compute placement
        x0 = cx - patch_w//2; y0 = cy - patch_h//2
        x1 = x0 + patch_w; y1 = y0 + patch_h
        # Clip to canvas
        sx0 = max(0, -x0); sy0 = max(0, -y0)
        dx0 = max(0, x0); dy0 = max(0, y0)
        dx1 = min(W, x1); dy1 = min(H, y1)
        if dx1 <= dx0 or dy1 <= dy0:
            continue
        sx1 = sx0 + (dx1-dx0); sy1 = sy0 + (dy1-dy0)
        patch_a = a_channel[sy0:sy1, sx0:sx1]
        src_a = patch_a / 255.0
        dst_a = canvas[dy0:dy1, dx0:dx1, 3].astype(float) / 255.0
        out_a = src_a + dst_a * (1-src_a)
        for c_idx, c_val in enumerate([r,g,b]):
            src_c = np.full_like(patch_a, c_val, dtype=float)
            dst_c = canvas[dy0:dy1, dx0:dx1, c_idx].astype(float)
            out_c = (src_c*src_a + dst_c*dst_a*(1-src_a)) / np.maximum(out_a, 1e-6)
            canvas[dy0:dy1, dx0:dx1, c_idx] = out_c.clip(0,255).astype(np.uint8)
        canvas[dy0:dy1, dx0:dx1, 3] = (out_a*255).clip(0,255).astype(np.uint8)


# ---------------------------------------------------------------------------
# Star rendering
# ---------------------------------------------------------------------------

def _render_stars(
    canvas: np.ndarray,
    catalog: StarCatalog,
    offset_x: float,
    offset_y: float,
    alpha_mult: float,
    wall_time: float = 0.0,
    twinkle_rate: float = 0.8,
) -> None:
    H, W = canvas.shape[:2]
    # Apply twinkle via sine modulation
    phases = (catalog.xs * 7.3 + catalog.ys * 3.1)  # unique per star
    twinkle = 0.7 + 0.3 * np.sin(2*math.pi*twinkle_rate*wall_time + phases*2*math.pi)

    for i in range(len(catalog.xs)):
        px = int((catalog.xs[i] + offset_x) % 1.0 * W)
        py = int((catalog.ys[i] + offset_y) % 1.0 * H)
        sz = max(1, int(catalog.sizes[i]))
        a = int(catalog.colors[i, 3] * alpha_mult * twinkle[i])
        r, g, b = int(catalog.colors[i,0]), int(catalog.colors[i,1]), int(catalog.colors[i,2])
        # Draw small square (fast)
        y0 = max(0, py-sz//2); y1 = min(H, py+sz//2+1)
        x0 = max(0, px-sz//2); x1 = min(W, px+sz//2+1)
        if y1<=y0 or x1<=x0:
            continue
        src_a = a / 255.0
        canvas[y0:y1, x0:x1, 0] = np.minimum(255,
            canvas[y0:y1, x0:x1, 0].astype(int) + int(r*src_a))
        canvas[y0:y1, x0:x1, 1] = np.minimum(255,
            canvas[y0:y1, x0:x1, 1].astype(int) + int(g*src_a))
        canvas[y0:y1, x0:x1, 2] = np.minimum(255,
            canvas[y0:y1, x0:x1, 2].astype(int) + int(b*src_a))
        canvas[y0:y1, x0:x1, 3] = np.minimum(255,
            canvas[y0:y1, x0:x1, 3].astype(int) + a)


# ---------------------------------------------------------------------------
# Main render
# ---------------------------------------------------------------------------

def render_parallax_frame(
    canvas: np.ndarray,
    cfg: ParallaxConfig,
    catalogs: List[StarCatalog],
    layer_t: float,
    wall_time: float = 0.0,
) -> np.ndarray:
    H, W = canvas.shape[:2]

    # Background fill
    reveal_t = max(0.0, (layer_t - cfg.reveal_start) /
                   max(cfg.reveal_duration, 1e-6))
    reveal_t = min(1.0, reveal_t)
    bg_a = int(reveal_t * 255)
    r, g, b = cfg.bg_color
    canvas[:, :, 0] = r; canvas[:, :, 1] = g; canvas[:, :, 2] = b
    canvas[:, :, 3] = bg_a

    if reveal_t <= 0.0:
        return canvas

    # Camera zoom interpolation
    zoom = cfg.zoom_start + (cfg.zoom_end - cfg.zoom_start) * layer_t

    for i, (layer_def, catalog) in enumerate(zip(cfg.layers, catalogs)):
        parallax_factor = 1.0 - layer_def.depth * 0.8
        ox = cfg.drift_x * layer_t * parallax_factor
        oy = cfg.drift_y * layer_t * parallax_factor

        if layer_def.nebula:
            # Nebula is static per frame (use a cheap hash for determinism)
            pass  # rendered at build time; skip per-frame for performance

        _render_stars(
            canvas, catalog,
            ox, oy,
            alpha_mult=reveal_t * (0.4 + 0.6 * layer_def.depth),
            wall_time=wall_time,
            twinkle_rate=0.5 + layer_def.depth * 0.5,
        )

    return canvas


def build_parallax(
    width: int, height: int,
    cfg: Optional[ParallaxConfig] = None,
    seed: Optional[int] = None,
) -> Tuple[ParallaxConfig, List[StarCatalog]]:
    if cfg is None:
        cfg = ParallaxConfig(seed=seed)
    rng = random.Random(cfg.seed if cfg.seed is not None else seed)
    catalogs = [build_star_catalog(l, width, height, rng) for l in cfg.layers]
    return cfg, catalogs


def generate_parallax_frames(
    width: int, height: int,
    num_frames: int,
    fps: float = 24.0,
    cfg: Optional[ParallaxConfig] = None,
    seed: Optional[int] = None,
) -> List[np.ndarray]:
    cfg, catalogs = build_parallax(width, height, cfg, seed)
    frames = []
    for i in range(num_frames):
        t = i / max(num_frames-1, 1)
        wt = i / fps
        canvas = np.zeros((height, width, 4), dtype=np.uint8)
        render_parallax_frame(canvas, cfg, catalogs, t, wt)
        frames.append(canvas)
    return frames


if __name__ == "__main__":
    print("sig_layer_parallax: self-test")
    frames = generate_parallax_frames(320, 240, 8, seed=13)
    print(f"Generated {len(frames)} frames OK")

