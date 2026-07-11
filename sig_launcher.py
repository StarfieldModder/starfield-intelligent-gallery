r"""
╔══════════════════════════════════════════════════════════════════════════════╗
║        ███████╗ ██╗  ██████╗      S I G _ L A U N C H E R . P Y              ║
║        ██╔════╝ ██║ ██╔════╝      GUI Front Door — Full Cinematic Chain      ║
║        ███████╗ ██║ ██║  ███╗                                                ║
║        ╚════██║ ██║ ██║   ██║     Starfield Intelligent Gallery              ║
║        ███████║ ██║ ╚██████╔╝                                                ║
║        ╚══════╝ ╚═╝  ╚═════╝      "Open the hatch. Let the story begin."     ║
╠══════════════════════════════════════════════════════════════════════════════╣
║  File       :  sig_launcher.py                                               ║
║  Location   :  C:\SIG\sig_launcher.py                                        ║
║  Author     :  Mark J. Latsha  (StarfieldModder / Games)                     ║
║  Co-Author  :  Microsoft Copilot (AI Engineer Colleague)                     ║
║  Version    :  2026.07.10 — Full Cinematic Chain Edition                     ║
╠══════════════════════════════════════════════════════════════════════════════╣
║  FULL SEQUENCE                                                               ║
║    1. IntroPanelWidget    Title fade + The Crossing video (29.9 s)           ║
║    2. SpaceFlightWidget   Deep space cinematic (22 s):                       ║
║                             Black → Pinpoint → Warp + Nebulae                ║
║                             → JOURNEY panel approach                         ║
║                             → Varuun glyphs dart in + land                   ║
║                             → "JOURNEY" coalesces letter by letter           ║
║    3. CarrierDeck         5 panels materialise from particle clouds          ║
║    4. CosmicChoicePanel   Player selects their path                          ║
║                                                                              ║
║  SAFETY RULES                                                                ║
║    • All widgets kept in _alive[] — no Python GC kills them                  ║
║    • Every step wrapped in try/except — no silent black freezes              ║
║    • SpaceFlightWidget failure skips straight to CarrierDeck                 ║
╠══════════════════════════════════════════════════════════════════════════════╣
║  NOTES                                                                       ║
║    • IntroPanelWidget now hands off to the launcher; launcher creates the    ║
║      SpaceFlightWidget and calls show_flight().                              ║
║    • Global ESC event filter installed so Escape quits cleanly.              ║
║    • Defensive duplicate-check prevents double flight launches.              ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""

import sys
import traceback

from PySide6.QtCore    import QTimer
from PySide6.QtWidgets import QApplication, QMessageBox

from ui.carrier_deck         import CarrierDeck
from ui.intro_panel_widget   import IntroPanelWidget
from ui.space_flight_widget  import SpaceFlightWidget
from cosmic_choice_panel     import CosmicChoicePanel


def launch_sig() -> None:
    """Full SIG cinematic launch sequence."""
    app = QApplication(sys.argv)

    # -----------------------------------------------------------------
    # Global ESC handler: install an event filter that quits the app
    # when the user presses the Escape key anywhere in the UI.
    # -----------------------------------------------------------------
    from PySide6.QtCore import Qt, QEvent, QObject

    class EscEventFilter(QObject):
        def __init__(self, app):
            super().__init__()
            self._app = app

        def eventFilter(self, watched, event):
            # Catch KeyPress events and handle Escape
            if event.type() == QEvent.Type.KeyPress:
                if event.key() == Qt.Key.Key_Escape:
                    print("[SIG Launcher] ESC pressed — shutting down.")
                    # Cleanly stop the Qt event loop
                    self._app.quit()
                    return True
            return super().eventFilter(watched, event)

    # Install the filter on the application so ESC is caught globally
    esc_filter = EscEventFilter(app)
    app.installEventFilter(esc_filter)

    # All top-level widgets stored here — prevents Python garbage collection
    _alive: list = []

    # ─────────────────────────────────────────────────────────────────────────
    # STEP 1 — IntroPanelWidget: title fade + The Crossing
    # ─────────────────────────────────────────────────────────────────────────
    intro = IntroPanelWidget()
    _alive.append(intro)

    def on_intro_finished() -> None:
        intro.hide()
        intro.close()
        _launch_flight()

    def _launch_flight() -> None:
        # ── STEP 2 — SpaceFlightWidget ────────────────────────────────────
        # Defensive: if a SpaceFlightWidget is already alive, skip duplicate launch.
        for w in _alive:
            if isinstance(w, SpaceFlightWidget):
                print("[SIG Launcher] _launch_flight called but SpaceFlightWidget already running — ignoring duplicate.")
                return

        try:
            flight = SpaceFlightWidget()
            _alive.append(flight)
            flight.flight_finished.connect(on_flight_finished)
            # Use the widget's public API to start the cinematic
            flight.show_flight()
            print("[SIG Launcher]  ✦ Space Flight — engines lit.")
        except Exception as exc:
            print(f"[SIG Launcher]  SpaceFlightWidget failed: {exc}")
            traceback.print_exc()
            print("[SIG Launcher]  Skipping cinematic — going straight to Carrier Deck.")
            on_flight_finished()   # graceful skip

    def on_flight_finished() -> None:
        # Cleanly close the flight widget
        for w in list(_alive):
            if isinstance(w, SpaceFlightWidget):
                try:
                    w.hide()
                    w.close()
                except Exception:
                    pass

        # ── STEP 3 — CarrierDeck ──────────────────────────────────────────
        try:
            deck = CarrierDeck()
            _alive.append(deck)
            deck.panel_selected.connect(on_panel_selected)
            deck.showFullScreen()

            # begin_materialize() fires 500 ms after deck is visible
            QTimer.singleShot(500, deck.begin_materialize)
            print("[SIG Launcher]  ✦ Carrier Deck online — panels materialising.")

        except Exception as exc:
            print(f"[SIG Launcher]  CarrierDeck failed: {exc}")
            traceback.print_exc()
            _show_error("Carrier Deck", exc)
            app.quit()

    def on_panel_selected(panel_id: int) -> None:
        _PANEL_NAMES = {
            1: "JOURNEY",
            2: "ARCHIVE",
            3: "ARTIFACTS",
            4: "COMPANIONS",
            5: "COSMIC CHOICE",
        }
        name = _PANEL_NAMES.get(panel_id, f"Panel {panel_id}")
        print(f"[SIG Launcher]  ✦ {name} selected — Cosmic Choice Panel.")

        # ── STEP 4 — CosmicChoicePanel ────────────────────────────────────
        try:
            choice = CosmicChoicePanel()
            _alive.append(choice)
            choice.showFullScreen()
        except Exception as exc:
            print(f"[SIG Launcher]  CosmicChoicePanel failed: {exc}")
            traceback.print_exc()
            _show_error("Cosmic Choice Panel", exc)

    def _show_error(name: str, exc: Exception) -> None:
        msg = QMessageBox()
        msg.setWindowTitle(f"SIG — {name} Error")
        msg.setIcon(QMessageBox.Icon.Critical)
        msg.setText(
            f"{name} failed to load.\n\n"
            f"Error: {exc}\n\n"
            "Check the VS Code terminal for the full traceback."
        )
        msg.exec()

    # ── Begin the sequence ────────────────────────────────────────────────
    intro.intro_finished.connect(on_intro_finished)
    intro.showFullScreen()
    intro.show_panel()

    sys.exit(app.exec())


if __name__ == "__main__":
    launch_sig()
