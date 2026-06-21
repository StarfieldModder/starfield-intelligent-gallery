#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
cinematic_mode_v2.py

Starfield Intelligent Gallery (SIG) — Cinematic Mode v2
Temple Resonance + Threshold Sequence (Scenes 03–05)

This module defines:
- Asset maps for Temple frames and audio
- A minimal audio hook interface
- Temple resonance playback (Scenes 03–04)
- Threshold crossing playback (Scene 05)
- A simple motion-curve interface (ready for future expansion)

All engine-specific calls (panel, audio_engine) are written as
clearly as possible so you can wire them into your real backend.

Author: Games + Copilot
"""

from dataclasses import dataclass
from typing import Dict, List, Optional


# ============================================================================
# ENGINE INTERFACES (TO BE WIRED TO YOUR REAL IMPLEMENTATION)
# ============================================================================

class Panel:
    """
    Abstract interface for a cinematic panel.
    Replace method bodies with your actual PyQt / rendering logic.
    """

    def set_background(self, image_path: str) -> None:
        pass

    def fade_in(self, duration_ms: int) -> None:
        pass

    def fade_out(self, duration_ms: int) -> None:
        pass

    def fade_to_white(self, duration_ms: int) -> None:
        pass

    def wait(self, duration_ms: int) -> None:
        pass

    def apply_shimmer(self, intensity: float = 0.15) -> None:
        pass

    def apply_glyph_activation(self) -> None:
        pass

    def pulse_brightness(self, intensity: float = 0.25) -> None:
        pass

    def zoom_slow(self, factor: float = 1.05, duration_ms: int = 1500) -> None:
        pass

    def pan_slow(self, x: float = 0.0, y: float = 0.0, duration_ms: int = 1500) -> None:
        pass

    def apply_warp(self, intensity: float = 0.2) -> None:
        pass

    def animate(
        self,
        zoom: float = 1.0,
        pan_x: float = 0.0,
        pan_y: float = 0.0,
        rotate: float = 0.0,
        duration_ms: int = 1500,
    ) -> None:
        pass


class AudioEngine:
    """
    Abstract interface for audio playback.
    Replace with your actual audio backend (QtMultimedia, pygame, etc.).
    """

    def play(self, path: str, volume: float = 0.8, loop: bool = False, fade_in: int = 0) -> None:
        pass

    def stop(self, track_name: Optional[str] = None, fade_out: int = 800) -> None:
        pass


# Global placeholder instance (you can inject your own)
audio_engine: Optional[AudioEngine] = None


# ============================================================================
# ASSET MAPS
# ============================================================================

# --- Temple Frames ---------------------------------------------------------

TEMPLE_FRAMES: Dict[str, List[str]] = {
    "scene03": [
        "assets/temple/frame_03A.jpg",  # The Breath Before Motion
        "assets/temple/frame_03B.jpg",  # The Chamber Remembers
        "assets/temple/frame_03C.jpg",  # The First Echo
    ],
    "scene04": [
        "assets/temple/frame_04A.jpg",  # The Glyphs Stir
        "assets/temple/frame_04B.jpg",  # The Awakening Geometry
        "assets/temple/frame_04C.jpg",  # The Moment of Becoming
    ],
    "scene05": [
        "assets/temple/frame_05A.jpg",  # The Ring as a Gate
        "assets/temple/frame_05B.jpg",  # Space Bends Inward
        "assets/temple/frame_05C.jpg",  # The Invitation
        "assets/temple/frame_05D.jpg",  # Step Beyond
    ],
}

# --- Audio Tracks ----------------------------------------------------------

AUDIO_TRACKS: Dict[str, str] = {
    "temple_low_drone": "assets/audio/temple_low_drone.wav",
    "glyph_activation": "assets/audio/glyph_activation.wav",
    "resonance_swell": "assets/audio/resonance_swell.wav",
    "threshold_chord": "assets/audio/threshold_chord.wav",
}


# ============================================================================
# AUDIO HOOKS
# ============================================================================

def play_audio(track_name: str, volume: float = 0.8, loop: bool = False, fade_in_ms: int = 0) -> None:
    """
    Play an audio track by name using the global audio_engine.
    Safe no-op if audio_engine is not set or track is missing.
    """
    global audio_engine

    if audio_engine is None:
        return

    track_path = AUDIO_TRACKS.get(track_name)
    if not track_path:
        return

    audio_engine.play(
        path=track_path,
        volume=volume,
        loop=loop,
        fade_in=fade_in_ms,
    )


def stop_audio(track_name: Optional[str] = None, fade_out_ms: int = 800) -> None:
    """
    Stop a specific track or all tracks via the global audio_engine.
    """
    global audio_engine

    if audio_engine is None:
        return

    audio_engine.stop(track_name=track_name, fade_out=fade_out_ms)


# ============================================================================
# MOTION CURVE (FUTURE-READY)
# ============================================================================

@dataclass
class MotionCurve:
    zoom: float = 1.0
    pan_x: float = 0.0
    pan_y: float = 0.0
    rotate: float = 0.0


def infer_motion_curve(prev_frame: str, next_frame: str) -> MotionCurve:
    """
    Placeholder for motion-curve inference between two frames.

    In a future version, this would analyze the images to infer:
    - Zoom delta
    - Pan delta
    - Subtle rotation / orbit

    For now, we return a gentle push-in and slight drift,
    matching the Temple's slow, inevitable pull.
    """
    zoom_delta = 0.08      # slight push-in
    pan_x_delta = -0.03    # drift left
    pan_y_delta = 0.01     # drift up
    rotate_delta = 0.0     # no roll

    return MotionCurve(
        zoom=1.0 + zoom_delta,
        pan_x=pan_x_delta,
        pan_y=pan_y_delta,
        rotate=rotate_delta,
    )


def apply_motion_curve(panel: Panel, frame_path: str, curve: MotionCurve, duration_ms: int = 1400) -> None:
    """
    Apply a motion curve to a given frame on the panel.
    """
    panel.set_background(frame_path)
    panel.animate(
        zoom=curve.zoom,
        pan_x=curve.pan_x,
        pan_y=curve.pan_y,
        rotate=curve.rotate,
        duration_ms=duration_ms,
    )


# ============================================================================
# TEMPLE RESONANCE (SCENES 03–04)
# ============================================================================

def play_temple_resonance_v2(panel: Panel) -> None:
    """
    Temple sequence with synchronized audio and visual resonance.
    Covers:
    - Scene 03: The First Resonance
    - Scene 04: The Glyphs Awaken
    """

    # Base atmosphere
    play_audio("temple_low_drone", volume=0.55, loop=True, fade_in_ms=1500)

    # Scene 03 — First Resonance
    for frame in TEMPLE_FRAMES.get("scene03", []):
        panel.set_background(frame)
        panel.fade_in(1200)
        panel.apply_shimmer(intensity=0.15)
        panel.wait(900)

    # Scene 04 — Glyphs Awaken
    play_audio("glyph_activation", volume=0.9, loop=False)
    for frame in TEMPLE_FRAMES.get("scene04", []):
        panel.set_background(frame)
        panel.apply_glyph_activation()
        panel.pulse_brightness(0.25)
        panel.wait(1100)


# ============================================================================
# SCENE 05 — CROSSING THE THRESHOLD
# ============================================================================

def play_scene05_threshold(panel: Panel) -> None:
    """
    Scene 05 — Crossing the Threshold.
    Uses Temple frames to create a slow, inevitable pull into the gate.
    """

    frames = TEMPLE_FRAMES.get("scene05", [])
    if len(frames) < 4:
        # Not enough frames; fail gracefully
        return

    # 05A — The Ring as a Gate
    panel.set_background(frames[0])
    panel.fade_in(1400)
    panel.zoom_slow(factor=1.05, duration_ms=1600)
    panel.wait(1600)

    # 05B — Space Bends Inward
    panel.set_background(frames[1])
    panel.apply_warp(intensity=0.18)
    panel.pan_slow(x=-0.03, y=0.01, duration_ms=1700)
    panel.wait(1700)

    # 05C — The Invitation
    panel.set_background(frames[2])
    panel.pulse_brightness(0.3)
    panel.zoom_slow(factor=1.08, duration_ms=1800)
    panel.wait(1800)

    # 05D — Step Beyond
    panel.set_background(frames[3])
    panel.fade_to_white(2200)
    panel.fade_out(1600)


def play_scene05_threshold_with_audio(panel: Panel) -> None:
    """
    Scene 05 with synchronized audio.
    """

    play_audio("resonance_swell", volume=1.0, loop=False, fade_in_ms=400)
    play_scene05_threshold(panel)
    play_audio("threshold_chord", volume=1.0, loop=False)


# ============================================================================
# FULL TEMPLE SEQUENCE (SCENES 03–05)
# ============================================================================

def play_full_temple_sequence(panel: Panel, with_audio: bool = True) -> None:
    """
    Plays the full Temple sequence:
    - Scene 03: First Resonance
    - Scene 04: Glyphs Awaken
    - Scene 05: Crossing the Threshold
    """

    if with_audio:
        play_temple_resonance_v2(panel)
        play_scene05_threshold_with_audio(panel)
        stop_audio(fade_out_ms=2000)
    else:
        play_temple_resonance_v2(panel)
        play_scene05_threshold(panel)
