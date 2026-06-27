# ================================================================
# Starfield Intelligent Gallery (SIG)
# Filename: cinematic_pipeline.py
# Module: Cinematic Startup Pipeline
# Version: 2026.06.26 — PySide6 Unified Edition
# Author: Mark J. Latsha
# Co-Author: Microsoft Copilot (AI Engineering Assistant)
# ================================================================

from __future__ import annotations

from PySide6.QtCore import QTimer
from PySide6.QtWidgets import QWidget, QStackedLayout

from ui.starfield_background import StarfieldBackground
from ui.intro_panel_widget import IntroPanelWidget


class CinematicPipeline(QWidget):
    """
    The unified cinematic pipeline for SIG.
    Controls the startup sequence:
        1. Wordless
        2. Starfield
        3. Relic arcs (placeholder)
        4. Holo panel (placeholder)
        5. Intro choice panel
    """

    def __init__(self, app, parent=None):
        super().__init__(parent)

        self.app = app

        # ------------------------------------------------------------
        # Layer stack
        # ------------------------------------------------------------
        self.stack = QStackedLayout(self)
        self.setLayout(self.stack)

        # ------------------------------------------------------------
        # Background layer
        # ------------------------------------------------------------
        self.starfield = StarfieldBackground(self)
        self.stack.addWidget(self.starfield)

        # ------------------------------------------------------------
        # Intro panel (choice panel)
        # ------------------------------------------------------------
        self.intro_panel = IntroPanelWidget(app, self)
        self.intro_panel.set_background(self.starfield)
        self.stack.addWidget(self.intro_panel)

        # ------------------------------------------------------------
        # Future layers (Phase 2+)
        # ------------------------------------------------------------
        # self.relic_arcs = RelicArcsLayer(self)
        # self.holo_panel = HoloPanel(self)

        # ------------------------------------------------------------
        # Begin cinematic sequence
        # ------------------------------------------------------------
        QTimer.singleShot(0, self._start_sequence)

    # ------------------------------------------------------------
    # Cinematic sequence controller
    # ------------------------------------------------------------
    def _start_sequence(self):
        """
        Phase 1:
        - Show starfield immediately
        - After a short delay, show intro panel
        """
        self.stack.setCurrentWidget(self.starfield)

        # Delay before intro panel expansion
        QTimer.singleShot(600, self._show_intro_panel)

    def _show_intro_panel(self):
        self.stack.setCurrentWidget(self.intro_panel)
        self.intro_panel.show_panel()
