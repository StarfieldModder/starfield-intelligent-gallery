r"""
╔══════════════════════════════════════════════════════════════════════════════╗
║        ███████╗ ██╗  ██████╗      S I G _ L A U N C H E R . P Y              ║
║        ██╔════╝ ██║ ██╔════╝      GUI Front Door — Full Cinematic Chain      ║
║        ███████╗ ██║ ██║  ███╗                                                ║
║        ╚════██║ ██║ ██║   ██║     Starfield Intelligent Gallery              ║
║        ███████║ ██║ ╚██████╔╝                                                ║
║        ╚══════╝ ╚═╝  ╚═════╝      "Open the hatch. Let the story begin."     ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""

import sys
import traceback

from PySide6.QtCore    import QTimer
from PySide6.QtWidgets import QApplication, QMessageBox

from ui.carrier_deck         import CarrierDeck
from ui.intro_panel_widget   import IntroPanelWidget
from ui.space_flight_widget  import SpaceFlightWidget

# ⭐ FIXED IMPORT ⭐
from intro.cosmic_choice_panel import CosmicChoicePanel


def launch_sig(debug=False) -> None:
    """Full SIG cinematic launch sequence."""
    app = QApplication(sys.argv)

    from PySide6.QtCore import Qt, QEvent, QObject

    class EscEventFilter(QObject):
        def __init__(self, app):
            super().__init__()
            self._app = app

        def eventFilter(self, watched, event):
            if event.type() == QEvent.Type.KeyPress:
                if event.key() == Qt.Key.Key_Escape:
                    print("[SIG Launcher] ESC pressed — shutting down.")
                    self._app.quit()
                    return True
            return super().eventFilter(watched, event)

    esc_filter = EscEventFilter(app)
    app.installEventFilter(esc_filter)

    _alive: list = []

    intro = IntroPanelWidget()
    _alive.append(intro)

    def on_intro_finished() -> None:
        intro.hide()
        intro.close()
        _launch_flight()

    def _launch_flight() -> None:
        for w in _alive:
            if isinstance(w, SpaceFlightWidget):
                print("[SIG Launcher] SpaceFlightWidget already running — ignoring duplicate.")
                return

        try:
            flight = SpaceFlightWidget()
            _alive.append(flight)
            flight.flight_finished.connect(on_flight_finished)
            flight.show_flight()
            print("[SIG Launcher] ✦ Space Flight — engines lit.")
        except Exception as exc:
            print(f"[SIG Launcher] SpaceFlightWidget failed: {exc}")
            traceback.print_exc()
            print("[SIG Launcher] Skipping cinematic — going straight to Carrier Deck.")
            on_flight_finished()

    def on_flight_finished() -> None:
        for w in list(_alive):
            if isinstance(w, SpaceFlightWidget):
                try:
                    w.hide()
                    w.close()
                except Exception:
                    pass

        try:
            deck = CarrierDeck()
            _alive.append(deck)
            deck.panel_selected.connect(on_panel_selected)
            deck.showFullScreen()
            QTimer.singleShot(500, deck.begin_materialize)
            print("[SIG Launcher] ✦ Carrier Deck online — panels materialising.")
        except Exception as exc:
            print(f"[SIG Launcher] CarrierDeck failed: {exc}")
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
        print(f"[SIG Launcher] ✦ {name} selected — Cosmic Choice Panel.")

        try:
            choice = CosmicChoicePanel()
            _alive.append(choice)
            choice.showFullScreen()
        except Exception as exc:
            print(f"[SIG Launcher] CosmicChoicePanel failed: {exc}")
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

    intro.intro_finished.connect(on_intro_finished)
    intro.showFullScreen()
    intro.show_panel()

    sys.exit(app.exec())


if __name__ == "__main__":
    launch_sig()
