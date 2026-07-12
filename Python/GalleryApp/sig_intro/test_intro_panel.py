# ================================================================
#  STARFIELD INTELLIGENT GALLERY (SIG)
#  Filename: test_intro_panel.py
#  Module: Test Harness — Intro Panel Widget
#
#  Version: 2026.05.25 — Test Harness Edition
#  Author: Mark J. Latsha (Games)
#  Co‑Author: Microsoft Copilot (AI Development Assistant)
#  Location: Brentwood, California — Pacific Daylight Time
#
#  Description:
#      This module launches the IntroPanelWidget independently of the
#      main SIG application. It is used for visual testing of the
#      holographic intro panel expansion animation, color gradients,
#      and transparency behavior.
#
#  Launch Command:
#      python -m GalleryApp.sig_intro.test_intro_panel
#
#  Requirements:
#      - PyQt6 installed
#      - __init__.py present in:
#            GalleryApp/
#            GalleryApp/sig_intro/
#
#  Notes:
#      - This file contains no production logic.
#      - It is purely for development and visual verification.
#      - Window raise() is used to ensure the panel appears above VS Code.
#
#  Timestamp:
#      Generated: May 25, 2026 — 8:10 PM PDT
# ================================================================

from PyQt6.QtWidgets import QApplication
import sys

from GalleryApp.sig_intro.intro_panel_widget import IntroPanelWidget


def main():
    app = QApplication(sys.argv)
    panel = IntroPanelWidget(app)
    panel.show_panel()
    panel.raise_()   # Ensures window appears above VS Code
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
