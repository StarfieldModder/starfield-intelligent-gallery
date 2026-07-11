r"""
╔══════════════════════════════════════════════════════════════════════════════╗
║        ███████╗ ██╗  ██████╗      I N T R O _ P A N E L _ W I D G E T        ║
║        ██╔════╝ ██║ ██╔════╝      Cinematic Title + Video Orchestrator       ║
║        ███████╗ ██║ ██║  ███╗                                                ║
║        ╚════██║ ██║ ██║   ██║     Starfield Intelligent Gallery              ║
║        ███████║ ██║ ╚██████╔╝                                                ║
║        ╚══════╝ ╚═╝  ╚═════╝      "The stars remember everything."           ║
╠══════════════════════════════════════════════════════════════════════════════╣
║  File       :  intro_panel_widget.py                                         ║
║  Location   :  C:\SIG\ui\intro_panel_widget.py                               ║
║  Author     :  Mark J. Latsha  (StarfieldModder / Games)                     ║
║  Co-Author  :  Microsoft Copilot (AI Engineer Colleague)                     ║
║  Version    :  2026.07.10 — Whispering Chamber Edition                       ║
╠══════════════════════════════════════════════════════════════════════════════╣
║  WHAT THIS FILE DOES                                                         ║
║                                                                              ║
║  Three-part cinematic intro — ALWAYS in this exact order:                    ║
║                                                                              ║
║  STEP 1 — Title Sequence  (every launch, no exceptions)                      ║
║    Title widget HIDDEN until animation starts — no flash.                    ║
║    QSequentialAnimationGroup: fade-in 1.5s → hold 2.5s → fade-out 1.5s       ║
║    Deep cobalt #3B78E7. Total: 5.5 seconds. Rock-solid reliable.             ║
║                                                                              ║
║  STEP 2 — PATH A  (video found)                                              ║
║    Video plays immediately — pre-cached during title display.                ║
║    Audio 100%. On end, hands off to the Whispering Chamber.                  ║
║                                                                              ║
║  STEP 2 — PATH B  (video not found — graceful fallback)                      ║
║    Brief black hold. Then hands off to the Whispering Chamber.               ║
║                                                                              ║
║  STEP 3 — WHISPERING CHAMBER                                                 ║
║    SpaceFlightWidget runs the 8-phase Ancient Intelligence Awakening.        ║
║    Emits flight_finished when REVELATION completes or user skips.            ║
║    On flight_finished → intro_finished is emitted exactly once.              ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""
from __future__ import annotations

import sys
from pathlib import Path

from PySide6.QtCore    import (Qt, QPropertyAnimation, QPauseAnimation,
                               QSequentialAnimationGroup, QTimer, QUrl, Signal)
from PySide6.QtGui     import QFont, QKeySequence, QShortcut
from PySide6.QtWidgets import (
    QApplication, QGraphicsOpacityEffect, QLabel, QVBoxLayout, QWidget,
)

# ── Optional multimedia (PATH A) ──────────────────────────────────────────────
try:
    from PySide6.QtMultimedia        import QAudioOutput, QMediaPlayer
    from PySide6.QtMultimediaWidgets import QVideoWidget
    _MULTIMEDIA_AVAILABLE = True
except ImportError:
    _MULTIMEDIA_AVAILABLE = False

# ── Whispering Chamber availability check (do not create widget here) ───────
try:
    from ui.space_flight_widget import SpaceFlightWidget  # type: ignore
    _SPACE_FLIGHT_AVAILABLE = True
except Exception:
    _SPACE_FLIGHT_AVAILABLE = False
    print("[IntroPanelWidget]  SpaceFlightWidget not importable — launcher will handle it.")

# ── Timing constants ──────────────────────────────────────────────────────────
TITLE_FADE_IN_MS  = 1_500    # 1.5 s  fade in
TITLE_HOLD_MS     = 2_500    # 2.5 s  hold at full brightness
TITLE_FADE_OUT_MS = 1_500    # 1.5 s  fade out   →  total 5.5 s
VIDEO_TIMEOUT_MS  = 120_000  # 2 min  absolute safety net
FALLBACK_HOLD_MS  =   800    # 0.8 s  black pause after title in PATH B


# ── Video search ──────────────────────────────────────────────────────────────
_VIDEO_FILENAMES = [
    "The_Crossing_06-30-2026-9-00_PM.mp4",
    "crossing_FINAL.mp4",
    "crossing_final.mp4",
    "The_Crossing.mp4",
]

_VIDEO_FOLDERS = [
    Path(r"C:\SIG\video"),
    Path(r"C:\SIG\Assets"),
    Path(r"C:\SIG"),
    Path(__file__).resolve().parent.parent / "video",
    Path(__file__).resolve().parent.parent / "Assets",
    Path(__file__).resolve().parent.parent,
    Path(__file__).resolve().parent,
]


def _find_video() -> Path | None:
    for folder in _VIDEO_FOLDERS:
        for name in _VIDEO_FILENAMES:
            candidate = folder / name
            if candidate.exists():
                return candidate
    video_dir = Path(r"C:\SIG\video")
    if video_dir.is_dir():
        mp4s = sorted(video_dir.glob("*.mp4"))
        if mp4s:
            print(f"[SIG Intro]  Auto-found video: {mp4s[0]}")
            return mp4s[0]
    return None


# ══════════════════════════════════════════════════════════════════════════════
class IntroPanelWidget(QWidget):
    """
    Cinematic three-part intro:

    1. Title sequence (fade-in → hold → fade-out).
    2. The Crossing video (PATH A) or brief black pause (PATH B).
    3. Hand off to launcher for Whispering Chamber (SpaceFlightWidget).

    intro_finished is emitted only after the Whispering Chamber completes
    (or is skipped). Intro no longer creates or shows the SpaceFlightWidget.
    """

    intro_finished = Signal()

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setStyleSheet("background-color: black;")
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)

        self._done          = False
        self._player        = None
        self._video_widget  = None
        self._timeout_timer = None
        self._anim_group    = None
        self._video_path    = _find_video()

        # Video built first (lower z-order), title built second (on top)
        self._build_video_layer()
        self._build_title_widget()

        # Skip shortcuts — any key bails out cleanly
        for key in ("Space", "Return", "Escape"):
            sc = QShortcut(QKeySequence(key), self)
            sc.activated.connect(self._finish)

    # ── Resize — keep layers filling window ───────────────────────────────────

    def resizeEvent(self, event) -> None:
        super().resizeEvent(event)
        r = self.rect()
        self._title_widget.setGeometry(r)
        if self._video_widget is not None:
            self._video_widget.setGeometry(r)

    # ── Build helpers ─────────────────────────────────────────────────────────

    def _build_title_widget(self) -> None:
        self._title_widget = QWidget(self)
        self._title_widget.setStyleSheet("background-color: black;")

        self._title_label = QLabel(
            "STARFIELD INTELLIGENT GALLERY", self._title_widget
        )
        self._title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        font = QFont("Segoe UI", 28, QFont.Weight.Thin)
        font.setLetterSpacing(QFont.SpacingType.AbsoluteSpacing, 8)
        self._title_label.setFont(font)
        self._title_label.setStyleSheet(
            "color: #3B78E7; background: transparent;"
        )

        lay = QVBoxLayout(self._title_widget)
        lay.addStretch()
        lay.addWidget(self._title_label)
        lay.addStretch()

        self._opacity_effect = QGraphicsOpacityEffect(self._title_label)
        self._title_label.setGraphicsEffect(self._opacity_effect)
        self._opacity_effect.setOpacity(0.0)

        self._title_widget.setGeometry(self.rect())
        self._title_widget.hide()

    def _build_video_layer(self) -> None:
        if not _MULTIMEDIA_AVAILABLE:
            print("[SIG Intro]  PySide6-QtMultimedia not installed — PATH B.")
            return
        if not self._video_path:
            print("[SIG Intro]  Video not found — PATH B.")
            return

        self._video_widget = QVideoWidget(self)
        self._video_widget.setStyleSheet("background-color: black;")
        self._video_widget.setAspectRatioMode(
            Qt.AspectRatioMode.KeepAspectRatio
        )
        self._video_widget.setGeometry(self.rect())
        self._video_widget.hide()

        self._audio_output = QAudioOutput(self)
        self._audio_output.setVolume(1.0)

        self._player = QMediaPlayer(self)
        self._player.setAudioOutput(self._audio_output)
        self._player.setVideoOutput(self._video_widget)
        self._player.setSource(QUrl.fromLocalFile(str(self._video_path)))

        # Pre-cache: buffers video without playing — instant start later
        self._player.pause()
        print(f"[SIG Intro]  Pre-caching: {self._video_path.name}")

        self._player.playbackStateChanged.connect(self._on_playback_state)
        self._player.errorOccurred.connect(self._on_player_error)

    # ── Public API ────────────────────────────────────────────────────────────

    def show_panel(self) -> None:
        """Call once from sig_launcher.py. Title sequence always runs first."""
        self._run_title_sequence()

    # ── Title sequence ───────────────────────────────────────────────────────

    def _run_title_sequence(self) -> None:
        self._title_widget.show()
        self._title_widget.raise_()

        anim_in = QPropertyAnimation(self._opacity_effect, b"opacity", self)
        anim_in.setDuration(TITLE_FADE_IN_MS)
        anim_in.setStartValue(0.0)
        anim_in.setEndValue(1.0)

        anim_out = QPropertyAnimation(self._opacity_effect, b"opacity", self)
        anim_out.setDuration(TITLE_FADE_OUT_MS)
        anim_out.setStartValue(1.0)
        anim_out.setEndValue(0.0)

        self._anim_group = QSequentialAnimationGroup(self)
        self._anim_group.addAnimation(anim_in)
        self._anim_group.addPause(TITLE_HOLD_MS)
        self._anim_group.addAnimation(anim_out)
        self._anim_group.finished.connect(self._on_title_done)
        self._anim_group.start()

    def _on_title_done(self) -> None:
        self._title_widget.hide()

        if self._player is not None:
            self._video_widget.setGeometry(self.rect())
            self._video_widget.show()
            self._video_widget.raise_()
            self._start_video()
        else:
            QTimer.singleShot(FALLBACK_HOLD_MS, self._start_whispering_chamber)

    # ── Video playback (PATH A) ───────────────────────────────────────────────

    def _start_video(self) -> None:
        print(f"[SIG Intro]  Playing (pre-cached): {self._video_path.name}")

        self._timeout_timer = QTimer(self)
        self._timeout_timer.setSingleShot(True)
        self._timeout_timer.timeout.connect(self._start_whispering_chamber)
        self._timeout_timer.start(VIDEO_TIMEOUT_MS)

        self._player.play()

    def _on_playback_state(self, state) -> None:
        from PySide6.QtMultimedia import QMediaPlayer as _QMP
        if state == _QMP.PlaybackState.StoppedState:
            self._start_whispering_chamber()

    def _on_player_error(self, error, error_string: str) -> None:
        print(f"[SIG Intro]  Player error: {error_string} — falling back.")
        QTimer.singleShot(FALLBACK_HOLD_MS, self._start_whispering_chamber)

    # ── Whispering Chamber handoff (launcher owns widget) ────────────────────

    def _start_whispering_chamber(self) -> None:
        """
        Stop video and hand off to the launcher. Do NOT create or show
        SpaceFlightWidget here — the launcher will create it after
        intro_finished is emitted.
        """
        if self._done:
            return

        if self._timeout_timer:
            self._timeout_timer.stop()
            self._timeout_timer = None
        if self._player:
            self._player.stop()
        if self._video_widget:
            self._video_widget.hide()

        if not _SPACE_FLIGHT_AVAILABLE:
            print("[IntroPanelWidget]  SpaceFlightWidget unavailable — finishing intro directly.")
            self._finish()
            return

        # Hand off to the launcher to create and show the flight widget.
        print("[IntroPanelWidget]  Whispering Chamber ready — handing off to launcher.")
        self._finish()

    def _on_flight_finished(self) -> None:
        """SpaceFlightWidget has completed — now emit intro_finished."""
        print("[IntroPanelWidget]  Whispering Chamber complete — handing off to Carrier Deck.")
        self._finish()

    # ── Completion ────────────────────────────────────────────────────────────

    def _finish(self) -> None:
        """Emit intro_finished exactly once — however we got here."""
        if self._done:
            return
        self._done = True

        if self._anim_group:
            self._anim_group.stop()
        if self._timeout_timer:
            self._timeout_timer.stop()
        if self._player:
            self._player.stop()

        print("[SIG Intro]  Complete — handing off to Carrier Deck.")
        self.intro_finished.emit()

    # ── Key press ─────────────────────────────────────────────────────────────

    def keyPressEvent(self, event) -> None:
        skip = (Qt.Key.Key_Space, Qt.Key.Key_Return,
                Qt.Key.Key_Enter, Qt.Key.Key_Escape)
        if event.key() in skip:
            self._finish()
        else:
            super().keyPressEvent(event)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    w = IntroPanelWidget()
    w.resize(1280, 720)
    w.setWindowTitle("SIG — Intro Panel Test")
    w.intro_finished.connect(
        lambda: (print("[TEST]  intro_finished emitted!"), app.quit())
    )
    w.show()
    w.show_panel()
    sys.exit(sys.argv and app.exec())
