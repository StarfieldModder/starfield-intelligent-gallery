r"""
╔══════════════════════════════════════════════════════════════════════════════╗
║              S I G   V I D E O   B A C K G R O U N D   L A Y E R             ║
║              Starfield Intelligent Gallery — Real Video Layer                ║
╠══════════════════════════════════════════════════════════════════════════════╣
║  File       :  sig_layer_video.py                                            ║
║  Author     :  Mark J. Latsha  (StarfieldModder / Games)                     ║
║  Co-Author  :  Microsoft Copilot (AI Engineering Collaborator)               ║
║  Repo       :  github.com/StarfieldModder/starfield-intelligent-gallery      ║
╠══════════════════════════════════════════════════════════════════════════════╣
║  PURPOSE                                                                     ║
║  Reads frames from The Crossing MP4 and composites them as the               ║
║  bottom-most background layer beneath all SIG procedural layers.             ║
║  Rings, glyphs, hologrid, and title all render ON TOP of this layer.         ║
╠══════════════════════════════════════════════════════════════════════════════╣
║  CHANGELOG                                                                   ║
║  v1.0   Initial real-video background layer                                  ║
║  v1.1   Fixed NumPy broadcast error: out_a shape (H,W,1) -> (H,W)            ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional, Tuple

import numpy as np


# ─────────────────────────────────────────────────────────────────────────────
#  Config
# ─────────────────────────────────────────────────────────────────────────────

@dataclass
class VideoLayerConfig:
    """Configuration for the real-video background layer."""

    # Path to the local cached MP4 file (set by sig_asset_fetch)
    video_path: str = ""

    # Blend opacity of the video layer (0.0 = invisible, 1.0 = fully opaque)
    opacity: float = 0.85

    # Fade in / fade out as fractions of total sequence duration
    fade_in_end:    float = 0.08   # video reaches full opacity by 8% in
    fade_out_start: float = 0.88   # video starts fading at 88%

    # If True, loop the video if it is shorter than the SIG sequence
    loop: bool = True

    # Resize mode: "fill" (crop-to-fill), "fit" (letterbox), "stretch"
    resize_mode: str = "fill"

    # Optional source crop (left, top, right, bottom) as 0.0-1.0 fractions
    crop: Optional[Tuple[float, float, float, float]] = None


# ─────────────────────────────────────────────────────────────────────────────
#  Frame loader
# ─────────────────────────────────────────────────────────────────────────────

def load_video_frames(
    video_path: str,
    target_w: int,
    target_h: int,
    cfg: VideoLayerConfig,
    max_frames: int = 99999,
) -> List[np.ndarray]:
    """
    Load all frames from an MP4, resize to (target_w x target_h).
    Returns list of uint8 RGB arrays shaped (H, W, 3).
    """
    try:
        import imageio
    except ImportError:
        raise RuntimeError(
            "imageio not found. Run:  pip install imageio imageio-ffmpeg"
        )

    path = Path(video_path)
    if not path.exists():
        raise FileNotFoundError(
            f"Video not found: {path}\n"
            "Run sig_asset_fetch.fetch_crossing_video() first."
        )

    print(f"\n  Loading video frames: {path.name}")
    reader = imageio.get_reader(str(path), format="ffmpeg")

    frames: List[np.ndarray] = []
    for i, frame in enumerate(reader):
        if i >= max_frames:
            break
        frame = _resize_frame(frame, target_w, target_h, cfg)
        frames.append(frame)
        if (i + 1) % 100 == 0:
            print(f"\r    Loaded {i + 1} frames…", end="", flush=True)

    reader.close()
    print(f"\r    ✅  {len(frames)} frames loaded from {path.name}          ")
    return frames


def _resize_frame(
    frame: np.ndarray,
    target_w: int,
    target_h: int,
    cfg: VideoLayerConfig,
) -> np.ndarray:
    """Resize a single (H x W x 3) uint8 frame to (target_h x target_w)."""
    try:
        from PIL import Image
    except ImportError:
        raise RuntimeError("Pillow not found. Run:  pip install pillow")

    img = Image.fromarray(frame)

    # Optional source crop first
    if cfg.crop:
        l, t, r, b = cfg.crop
        W0, H0 = img.size
        img = img.crop((int(l * W0), int(t * H0), int(r * W0), int(b * H0)))

    src_w, src_h = img.size

    if cfg.resize_mode == "stretch":
        img = img.resize((target_w, target_h), Image.LANCZOS)

    elif cfg.resize_mode == "fit":
        # Letterbox — preserve aspect ratio, pad with black
        scale = min(target_w / src_w, target_h / src_h)
        nw, nh = int(src_w * scale), int(src_h * scale)
        img = img.resize((nw, nh), Image.LANCZOS)
        canvas = Image.new("RGB", (target_w, target_h), (0, 0, 0))
        canvas.paste(img, ((target_w - nw) // 2, (target_h - nh) // 2))
        img = canvas

    else:  # "fill" — scale up, crop centre
        scale = max(target_w / src_w, target_h / src_h)
        nw, nh = int(src_w * scale), int(src_h * scale)
        img = img.resize((nw, nh), Image.LANCZOS)
        ox = (nw - target_w) // 2
        oy = (nh - target_h) // 2
        img = img.crop((ox, oy, ox + target_w, oy + target_h))

    return np.array(img, dtype=np.uint8)


# ─────────────────────────────────────────────────────────────────────────────
#  Per-frame renderer
# ─────────────────────────────────────────────────────────────────────────────

def render_video_frame(
    canvas: np.ndarray,
    frames: List[np.ndarray],
    cfg: VideoLayerConfig,
    frame_idx: int,
    t_global: float,
) -> None:
    """
    Blend the video frame onto canvas (RGBA H x W x 4 uint8) in-place.

    Args:
        canvas     : RGBA output array, modified in-place.
        frames     : Pre-loaded list of RGB frame arrays.
        cfg        : VideoLayerConfig instance.
        frame_idx  : Current frame index in the SIG sequence.
        t_global   : Normalised time [0.0, 1.0] within the full sequence.
    """
    if not frames:
        return

    # Choose source frame (loop if needed)
    n   = len(frames)
    idx = frame_idx % n if cfg.loop else min(frame_idx, n - 1)
    src = frames[idx]          # shape: (H, W, 3)  uint8

    # Compute fade-envelope opacity
    opacity = cfg.opacity
    if t_global < cfg.fade_in_end and cfg.fade_in_end > 0:
        opacity *= t_global / cfg.fade_in_end
    elif t_global > cfg.fade_out_start and cfg.fade_out_start < 1.0:
        fade_len = 1.0 - cfg.fade_out_start
        opacity *= 1.0 - (t_global - cfg.fade_out_start) / fade_len
    opacity = max(0.0, min(1.0, opacity))

    # Build RGBA overlay from the source RGB frame
    H, W = src.shape[:2]
    overlay = np.empty((H, W, 4), dtype=np.uint8)
    overlay[:, :, :3] = src
    overlay[:, :, 3]  = np.uint8(int(opacity * 255))

    # Alpha-composite overlay onto canvas (both RGBA float32 for precision)
    b  = canvas.astype(np.float32)            # (H, W, 4)
    o  = overlay.astype(np.float32)           # (H, W, 4)

    # Keep alpha as (H, W, 1) for broadcasting over RGB, then squeeze for alpha
    oa = o[:, :, 3:4] / 255.0                # (H, W, 1)
    ba = b[:, :, 3:4] / 255.0                # (H, W, 1)

    out_a   = oa + ba * (1.0 - oa)           # (H, W, 1)
    safe    = np.maximum(out_a, 1e-6)        # (H, W, 1)  avoid div-by-zero
    out_rgb = (o[:, :, :3] * oa + b[:, :, :3] * ba * (1.0 - oa)) / safe

    # Write results back — RGB channels take (H,W,3), alpha channel takes (H,W)
    canvas[:, :, :3] = out_rgb.clip(0, 255).astype(np.uint8)
    canvas[:, :,  3] = (out_a[:, :, 0] * 255).clip(0, 255).astype(np.uint8)
    #                          ^^^^^^^^
    #  v1.1 FIX: index [0] on last axis squeezes (H,W,1) → (H,W)
    #  Without this, NumPy raises:
    #  ValueError: could not broadcast input array from shape (H,W,1) into shape (H,W)

