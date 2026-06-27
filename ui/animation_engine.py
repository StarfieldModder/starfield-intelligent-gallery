# ============================================================
# File        : animation_engine.py
# Project     : Starfield Intelligent Gallery (SIG)
# Author      : Mark J. Latsha
# Co-Author   : Microsoft Copilot (Engineering Assistant)
# Created     : June 2026
# Description : Central animation utilities for SIG UI panels.
#               Provides fade-in and glow-pulse animations.
# ============================================================

from PySide6.QtCore import QPropertyAnimation, QEasingCurve
from PySide6.QtWidgets import QGraphicsDropShadowEffect


# ------------------------------------------------------------
# Fade-In Animation
# ------------------------------------------------------------
def create_fade_in(widget, duration=1500):
    """
    Fades in a widget by animating its windowOpacity.
    """
    animation = QPropertyAnimation(widget, b"windowOpacity")
    animation.setDuration(duration)
    animation.setStartValue(0.0)
    animation.setEndValue(1.0)
    animation.setEasingCurve(QEasingCurve.InOutQuad)
    return animation


# ------------------------------------------------------------
# Glow Pulse Animation
# ------------------------------------------------------------
def create_glow_pulse(widget, color="white", min_radius=10, max_radius=40, duration=2000):
    """
    Creates a pulsing glow animation around a widget using a drop shadow effect.
    """
    glow = QGraphicsDropShadowEffect()
    glow.setColor(color)
    glow.setOffset(0, 0)
    glow.setBlurRadius(min_radius)
    widget.setGraphicsEffect(glow)

    animation = QPropertyAnimation(glow, b"blurRadius")
    animation.setDuration(duration)
    animation.setStartValue(min_radius)
    animation.setEndValue(max_radius)
    animation.setEasingCurve(QEasingCurve.InOutQuad)
    animation.setLoopCount(-1)

    return animation
