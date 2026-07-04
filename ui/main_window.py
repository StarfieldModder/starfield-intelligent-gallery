# ================================================================
# ╔══════════════════════════════════════════════════════════════╗
# ║              S I G  —  M A I N   W I N D O W                ║
# ║              Starfield Intelligent Gallery                   ║
# ╠══════════════════════════════════════════════════════════════╣
# ║  File      :  main_window.py                                 ║
# ║  Location  :  C:\SIG\ui\main_window.py                       ║
# ║  Author    :  Mark J. Latsha  (StarfieldModder / Games)      ║
# ║  Co-Author :  Microsoft Copilot (AI Engineering Collaborator)║
# ║  Version   :  2026.07.02 — Cinematic Controller Edition      ║
# ╠══════════════════════════════════════════════════════════════╣
# ║  ARCHITECTURE                                                ║
# ║                                                              ║
# ║  QMainWindow                                                 ║
# ║    └─ QStackedWidget (central widget)                        ║
# ║         ├─ Page 0 : IntroPanelWidget  (The Crossing MP4)     ║
# ║         └─ Page 1 : CarrierDeck       (Five sovereign panels)║
# ║                                                              ║
# ║  SIGNAL CHAIN                                                ║
# ║    IntroPanelWidget.intro_finished                           ║
# ║      → _on_intro_finished()                                  ║
# ║           → stack flips to Page 1                            ║
# ║           → CarrierDeck.begin_materialize()  (100 ms delay)  ║
# ║    CarrierDeck.panel_selected(int)                           ║
# ║      → _on_panel_selected(panel_id)                          ║
# ║           → CinematicController.play(panel_id)               ║
# ║    CinematicController.on_return                             ║
# ║      → _on_cinema_finished()                                  ║
# ╠══════════════════════════════════════════════════════════════╣
# ║  FIX LOG                                                     ║
# ║  2026.06.26 — Initial build                                  ║
# ║  2026.07.01 — IntroPanelWidget added to QStackedWidget       ║
# ║  2026.07.02 — # header (unicode-safe)                        ║
# ║  2026.07.02 — CinematicController wired to all 5 panels      ║
# ╚══════════════════════════════════════════════════════════════╝
# ================================================================

from __future__ import annotations

import sys

from PySide6.QtCore    import QTimer
from PySide6.QtGui     import QColor
from PySide6.QtWidgets import QApplication, QMainWindow, QStackedWidget

from ui.intro_panel_widget   import IntroPanelWidget
from ui.carrier_deck          import CarrierDeck
from ui.cinematic_controller  import CinematicController


class MainWindow(QMainWindow):
    """
    Root application window.
    Page 0: IntroPanelWidget — plays crossing_FINAL.mp4
    Page 1: CarrierDeck      — five sovereign panels
    """

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setWindowTitle("Starfield Intelligent Gallery")
        self.showFullScreen()

        # ── Stacked pages ────────────────────────────────────────────────────
        self._stack = QStackedWidget(self)
        self.setCentralWidget(self._stack)

        # Page 0 — intro video
        self._intro = IntroPanelWidget(self)
        self._stack.addWidget(self._intro)

        # Page 1 — carrier deck
        self._deck = CarrierDeck(self)
        self._stack.addWidget(self._deck)

        # ── Cinematic controller ─────────────────────────────────────────────
        self._cinema = CinematicController(
            parent    = self,
            on_return = self._on_cinema_finished,
        )

        # ── Signal wiring ────────────────────────────────────────────────────
        self._intro.intro_finished.connect(self._on_intro_finished)
        self._deck.panel_selected.connect(self._on_panel_selected)

        # Start on page 0
        self._stack.setCurrentIndex(0)
        self._intro.show_panel()

    # ── Intro finished ───────────────────────────────────────────────────────

    def _on_intro_finished(self) -> None:
        """Flip to the Carrier Deck and begin panel materialisation."""
        print("[MainWindow]  Intro finished — switching to Carrier Deck.")
        self._stack.setCurrentIndex(1)
        QTimer.singleShot(100, self._deck.begin_materialize)

    # ── Panel selected ───────────────────────────────────────────────────────

    def _on_panel_selected(self, panel_id: int) -> None:
        """Route the panel click to the cinematic controller."""
        names = {
            1: "Journey",
            2: "Archive",
            3: "Artifacts",
            4: "Companions",
            5: "Cosmic Choice",
        }
        name = names.get(panel_id, f"Panel {panel_id}")
        print(f"[MainWindow]  Panel selected: {panel_id} ({name})")
        self._cinema.play(panel_id)

    # ── Cinema finished (back to deck) ───────────────────────────────────────

    def _on_cinema_finished(self) -> None:
        """Called when the user exits a cinematic sequence."""
        print("[MainWindow]  Returned to Carrier Deck.")
        # Carrier Deck is already visible — nothing extra needed.


# ══════════════════════════════════════════════════════════════════════════════
#  Standalone test  —  python ui\main_window.py
# ══════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = MainWindow()
    win.show()
    sys.exit(app.exec())
