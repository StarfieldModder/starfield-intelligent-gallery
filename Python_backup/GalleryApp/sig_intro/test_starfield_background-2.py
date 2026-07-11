# ================================================================
# Starfield Intelligent Gallery (SIG)
# Filename: test_starfield_background.py
# Module: Test — Starfield Background Renderer
# Version: 2026.05.25 — Test Harness Edition
# Author: Mark J. Latsha
# Co-Author: Microsoft Copilot (AI Engineering Assistant)
# Location: Brentwood, California — Pacific Daylight Time
#
# Description:
#     Test harness for the StarfieldBackground module.
#     Allows SIG developers to launch and visually inspect the
#     cinematic starfield renderer, nebula layers, and drift motion.
#
# Launch Command:
#     python -m GalleryApp.sig_intro.test_starfield_background
#
# Notes:
#     - Requires __init__.py in both GalleryApp and sig_intro folders
#     - Does NOT modify or replace the main background renderer
#     - Purely for testing and visual verification
#
# Timestamp:
#     Generated: May 26, 2026 — 2:58 AM PDT
# ================================================================

from PyQt6.QtWidgets import QApplication
import sys

from GalleryApp.sig_intro.starfield_background import StarfieldBackground


def main():
    app = QApplication(sys.argv)
    w = StarfieldBackground()
    w.resize(1280, 720)
    w.show()
    w.raise_()   # Ensures window appears above VS Code
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
