# ============================================================
# STARFIELD INTELLIGENT GALLERY — ANIMATION PACKAGE
# ============================================================
# File        : __init__.py
# Project     : Starfield Intelligent Gallery (SIG)
# Subsystem   : Intro Panel Animation Modules
#
# Description :
#     This package exposes the animation modules used by the
#     SIG Introductory Floating Panel. Only modules that actually
#     exist in this folder are imported here.
#
# Notes :
#     - This file must ONLY import modules that physically exist
#       in the animations/ directory.
#     - Incorrect imports here will break the entire package load.
#     - The __all__ list defines the public API for this package.
#
# Author      : Mark J. Latsha & Microsoft Copilot
# Created     : May 2026
# ============================================================

from .dissolve import Dissolve
from .drift import Drift
from .parallax import Parallax
from .scanline import Scanline

__all__ = [
    "Dissolve",
    "Drift",
    "Parallax",
    "Scanline",
]
