r"""
╔══════════════════════════════════════════════════════════════════════════════╗
║        ███████╗ ██╗  ██████╗   C O S M I C _ C H O I C E _ P A N E L . P Y  ║
║        ██╔════╝ ██║ ██╔════╝   Decision Surface — SIG Narrative Fork        ║
║        ███████╗ ██║ ██║  ███╗                                                ║
║        ╚════██║ ██║ ██║   ██║  Starfield Intelligent Gallery                 ║
║        ███████║ ██║ ╚██████╔╝                                                ║
║        ╚══════╝ ╚═╝  ╚═════╝   "The moment the player chooses their path."  ║
╠══════════════════════════════════════════════════════════════════════════════╣
║  File       :  cosmic_choice_panel.py                                        ║
║  Location   :  C:\SIG\cosmic_choice_panel.py                                 ║
║  Author     :  Mark J. Latsha  (StarfieldModder / Games)                     ║
║  Co-Author  :  Microsoft Copilot (AI Engineer Colleague)                     ║
║  Version    :  2026.07.05 — Guarded Imports + Safe Mode Launch Edition       ║
╠══════════════════════════════════════════════════════════════════════════════╣
║  WHAT THIS FILE IS                                                            ║
║    The interactive decision surface — receives control from Carrier Deck.    ║
║    Presents 4 mode buttons. Each launches its SIG mode.                      ║
║    All imports and mode launches are guarded — no silent crashes.            ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""

from __future__ import annotations

import traceback

from PySide6.QtCore    import Qt, QPropertyAnimation
from PySide6.QtGui     import QFont
from PySide6.QtWidgets import (
    QLabel, QPushButton, QVBoxLayout, QWidget,
)

# ── Mode imports — all guarded so one bad module can't kill the panel ─────────
try:
    from gallery_mode import GalleryMode
    _GALLERY_OK = True
except ImportError as e:
    _GALLERY_OK = False
    print(f"[CosmicChoice]  GalleryMode not available: {e}")

try:
    from relics_mode import RelicsMode
    _RELICS_OK = True
except ImportError as e:
    _RELICS_OK = False
    print(f"[CosmicChoice]  RelicsMode not available: {e}")

try:
    from companions_mode import CompanionMode
    _COMPANIONS_OK = True
except ImportError as e:
    _COMPANIONS_OK = False
    print(f"[CosmicChoice]  CompanionMode not available: {e}")

try:
    from archive_mode import ArchiveMode
    _ARCHIVE_OK = True
except ImportError as e:
    _ARCHIVE_OK = False
    print(f"[CosmicChoice]  ArchiveMode not available: {e}")

# ── Nebula — optional visual enhancement, never crashes the panel ─────────────
try:
    from nebula_module import render_nebula as _render_nebula
    _NEBULA_OK = True
except (ImportError, AttributeError):
    _NEBULA_OK = False
    print("[CosmicChoice]  nebula_module not available — continuing without it.")


# ══════════════════════════════════════════════════════════════════════════════
#  HoverButton
# ══════════════════════════════════════════════════════════════════════════════

class HoverButton(QPushButton):
    """Glowing hover button — deep space aesthetic."""

    def __init__(self, text: str) -> None:
        super().__init__(text)
        self.setStyleSheet("""
            QPushButton {
                background-color : #1a1f2b;
                color            : white;
                padding          : 20px;
                font-size        : 14px;
                letter-spacing   : 2px;
                border           : 2px solid #3a4a6b;
                border-radius    : 6px;
            }
            QPushButton:hover {
                background-color : #243047;
                border           : 2px solid #6fa3ff;
                color            : #aad4ff;
            }
            QPushButton:pressed {
                background-color : #0e1520;
                border           : 2px solid #3B78E7;
            }
            QPushButton:disabled {
                color            : #444;
                border           : 2px solid #222;
            }
        """)
        self._glyph_anim = QPropertyAnimation(self, b"windowOpacity")
        self._glyph_anim.setDuration(300)
        self._glyph_anim.setStartValue(0.85)
        self._glyph_anim.setEndValue(1.0)

    def enterEvent(self, event) -> None:
        self._glyph_anim.start()
        super().enterEvent(event)


# ══════════════════════════════════════════════════════════════════════════════
#  CosmicChoicePanel
# ══════════════════════════════════════════════════════════════════════════════

class CosmicChoicePanel(QWidget):
    """
    Four-button mode selection surface.
    Shown after the player clicks any Carrier Deck panel.
    Each button launches a SIG mode — all launches are error-protected.
    """

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setWindowTitle("SIG — Cosmic Choice Panel")
        self.setStyleSheet("background-color: #02040a; color: white;")

        # Optional nebula — purely cosmetic, never blocks startup
        if _NEBULA_OK:
            try:
                _render_nebula()
            except Exception:
                pass

        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.setSpacing(18)

        # Title
        title = QLabel("COSMIC CHOICE PANEL")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setFont(QFont("Segoe UI", 28, QFont.Weight.Thin))
        title.setStyleSheet("color: #3B78E7; letter-spacing: 6px;")
        layout.addWidget(title)

        # Subtitle
        prompt = QLabel("Choose your path among the stars...")
        prompt.setAlignment(Qt.AlignmentFlag.AlignCenter)
        prompt.setFont(QFont("Segoe UI", 14, QFont.Weight.Thin))
        prompt.setStyleSheet("color: #8090b0; margin-bottom: 20px;")
        layout.addWidget(prompt)

        # ── Mode buttons ──────────────────────────────────────────────────
        btn_gallery = HoverButton("⬡  ENTER GALLERY MODE")
        btn_gallery.setEnabled(_GALLERY_OK)
        btn_gallery.clicked.connect(self._enter_gallery)
        layout.addWidget(btn_gallery)

        btn_relics = HoverButton("⬡  ENTER RELICS MODE")
        btn_relics.setEnabled(_RELICS_OK)
        btn_relics.clicked.connect(self._enter_relics)
        layout.addWidget(btn_relics)

        btn_companion = HoverButton("⬡  ENTER COMPANION MODE")
        btn_companion.setEnabled(_COMPANIONS_OK)
        btn_companion.clicked.connect(self._enter_companion)
        layout.addWidget(btn_companion)

        btn_archive = HoverButton("⬡  ENTER ARCHIVE MODE")
        btn_archive.setEnabled(_ARCHIVE_OK)
        btn_archive.clicked.connect(self._enter_archive)
        layout.addWidget(btn_archive)

        # Keep launched mode widgets alive
        self._mode_widgets: list = []

    # ── Mode launchers — all error-protected ─────────────────────────────────

    def _enter_gallery(self) -> None:
        self._launch_mode("GalleryMode", GalleryMode if _GALLERY_OK else None)

    def _enter_relics(self) -> None:
        self._launch_mode("RelicsMode", RelicsMode if _RELICS_OK else None)

    def _enter_companion(self) -> None:
        self._launch_mode("CompanionMode", CompanionMode if _COMPANIONS_OK else None)

    def _enter_archive(self) -> None:
        self._launch_mode("ArchiveMode", ArchiveMode if _ARCHIVE_OK else None)

    def _launch_mode(self, name: str, mode_class) -> None:
        if mode_class is None:
            print(f"[CosmicChoice]  {name} is not available.")
            return
        try:
            mode = mode_class()
            self._mode_widgets.append(mode)  # keep alive
            if hasattr(mode, "show"):
                mode.showFullScreen()
            elif hasattr(mode, "run"):
                mode.run()
        except Exception as exc:
            print(f"[CosmicChoice]  {name} failed to launch: {exc}")
            traceback.print_exc()


if __name__ == "__main__":
    import sys
    from PySide6.QtWidgets import QApplication
    app = QApplication(sys.argv)
    w = CosmicChoicePanel()
    w.resize(1280, 720)
    w.show()
    sys.exit(app.exec())

