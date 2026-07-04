r"""
╔══════════════════════════════════════════════════════════════════════════════╗
║        ███████╗ ██╗  ██████╗      I N T R O _ P A N E L _ W I D G E T       ║
║        ██╔════╝ ██║ ██╔════╝      Cinematic Title + Video Orchestrator       ║
║        ███████╗ ██║ ██║  ███╗                                                ║
║        ╚════██║ ██║ ██║   ██║     Starfield Intelligent Gallery              ║
║        ███████║ ██║ ╚██████╔╝                                                ║
║        ╚══════╝ ╚═╝  ╚═════╝      "The stars remember everything."          ║
╠══════════════════════════════════════════════════════════════════════════════╣
║  File       :  intro_panel_widget.py                                         ║
║  Location   :  C:\SIG\ui\intro_panel_widget.py                               ║
║  Author     :  Mark J. Latsha  (StarfieldModder / Games)                     ║
║  Co-Author  :  Microsoft Copilot (AI Engineer Colleague)                     ║
║  Version    :  2026.07.04 — Title-First + Pre-Cache Edition                  ║
╠══════════════════════════════════════════════════════════════════════════════╣
║  WHAT THIS FILE DOES                                                         ║
║                                                                              ║
║  Two-part cinematic intro — ALWAYS in this exact order:                      ║
║                                                                              ║
║  STEP 1 — Title Sequence  (every launch, no exceptions)                      ║
║    "STARFIELD INTELLIGENT GALLERY" fades in — deep cobalt #3B78E7.          ║
║    Fade-in  1.5 s  →  Hold 2.5 s  →  Fade-out 1.5 s  =  5.5 s total.      ║
║    While the title shows, the video pre-buffers silently in background.      ║
║                                                                              ║
║  STEP 2 — PATH A  (video found)                                              ║
║    Video plays IMMEDIATELY — already cached during title display.            ║
║    Audio 100 %. Emits intro_finished on end. Safety timeout = 2 min.        ║
║                                                                              ║
║  STEP 2 — PATH B  (video not found — graceful fallback)                     ║
║    Brief black hold. Emits intro_finished. No crash. No panic.              ║
║                                                                              ║
║  VIDEO SEARCH ORDER                                                          ║
║    1. C:\SIG\video\The_Crossing_06-30-2026-9-00_PM.mp4                       ║
║    2. C:\SIG\Assets\crossing_FINAL.mp4                                       ║
║    3. C:\SIG\crossing_FINAL.mp4                                              ║
║    4. Script folder / parent folder  (auto-detect any *.mp4)                ║
║                                                                              ║
║  KEYBOARD   Space / Enter / Escape — skip intro immediately                 ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""

from __future__ import annotations

import sys
from pathlib import Path

from PySide6.QtCore    import Qt, QPropertyAnimation, QTimer, QUrl, Signal
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


# ── Timing constants ──────────────────────────────────────────────────────────
TITLE_FADE_IN_MS  = 1_500    # 1.5 s  fade in
TITLE_HOLD_MS     = 2_500    # 2.5 s  hold at full brightness
TITLE_FADE_OUT_MS = 1_500    # 1.5 s  fade out  → total 5.5 s
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
    # Last resort: grab any .mp4 found in C:\SIG\video
    video_dir = Path(r"C:\SIG\video")
    if video_dir.is_dir():
        mp4s = sorted(video_dir.glob("*.mp4"))
        if mp4s:
            print(f"[SIG Intro]  Auto-found video: {mp4s[0]}")
            return mp4s[0]
    return None


# ══════════════════════════════════════════════════════════════════════════════
#  I N T R O   P A N E L   W I D G E T
# ══════════════════════════════════════════════════════════════════════════════

class IntroPanelWidget(QWidget):
    """
    Cinematic two-part intro.

    Build order (critical for z-order):
      1. _build_video_layer()  → lower z, hidden
      2. _build_title_widget() → higher z, visible on top

    Sequence:
      show_panel() → title fades in/holds/fades out
                   → video.show() + player.play()  [PATH A]
                   → brief hold + intro_finished   [PATH B]
    """

    intro_finished = Signal()

    # ── Init ──────────────────────────────────────────────────────────────────

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setStyleSheet("background-color: black;")

        self._done          = False
        self._player        = None
        self._video_widget  = None
        self._timeout_timer = None

        self._video_path = _find_video()

        # !! ORDER MATTERS — video built first (lower z), title built second (on top) !!
        self._build_video_layer()   # hidden; starts pre-buffering immediately
        self._build_title_widget()  # visible on top, ready for fade animation

        # Skip shortcuts
        for key in ("Space", "Return", "Escape"):
            sc = QShortcut(QKeySequence(key), self)
            sc.activated.connect(self._finish)

    # ── Keep layers filling the window ────────────────────────────────────────

    def resizeEvent(self, event) -> None:
        super().resizeEvent(event)
        r = self.rect()
        self._title_widget.setGeometry(r)
        if self._video_widget is not None:
            self._video_widget.setGeometry(r)

    # ── Build helpers ─────────────────────────────────────────────────────────

    def _build_title_widget(self) -> None:
        """Full-screen black panel. Title label in deep cobalt #3B78E7."""
        self._title_widget = QWidget(self)
        self._title_widget.setStyleSheet("background-color: black;")

        self._title_label = QLabel(
            "STARFIELD INTELLIGENT GALLERY", self._title_widget
        )
        self._title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        font = QFont("Segoe UI", 28, QFont.Weight.Thin)
        font.setLetterSpacing(QFont.SpacingType.AbsoluteSpacing, 8)
        self._title_label.setFont(font)

        # ── Deep cobalt blue — rich, cinematic, unmistakably SIG ──────────
        self._title_label.setStyleSheet(
            "color: #3B78E7; background: transparent;"
        )

        lay = QVBoxLayout(self._title_widget)
        lay.addStretch()
        lay.addWidget(self._title_label)
        lay.addStretch()

        self._title_widget.setGeometry(self.rect())
        self._title_widget.show()
        self._title_widget.raise_()   # must be on TOP of video widget

    def _build_video_layer(self) -> None:
        """
        Create hidden video widget. Call player.pause() immediately so
        the 70 MB video buffers during the 5.5 s title sequence.
        When play() is called later it starts with zero buffering delay.
        """
        if not _MULTIMEDIA_AVAILABLE:
            print("[SIG Intro]  PySide6-QtMultimedia not installed — PATH B.")
            return
        if not self._video_path:
            print("[SIG Intro]  Video not found in any search path — PATH B.")
            return

        self._video_widget = QVideoWidget(self)
        self._video_widget.setStyleSheet("background-color: black;")
        self._video_widget.setAspectRatioMode(
            Qt.AspectRatioMode.KeepAspectRatio
        )
        self._video_widget.setGeometry(self.rect())
        self._video_widget.hide()          # ← stays hidden until title is done

        self._audio_output = QAudioOutput(self)
        self._audio_output.setVolume(1.0)

        self._player = QMediaPlayer(self)
        self._player.setAudioOutput(self._audio_output)
        self._player.setVideoOutput(self._video_widget)
        self._player.setSource(QUrl.fromLocalFile(str(self._video_path)))

        # ── PRE-CACHE: pause() loads and buffers the file without playing ──
        self._player.pause()
        print(f"[SIG Intro]  Pre-caching: {self._video_path.name}")

        self._player.playbackStateChanged.connect(self._on_playback_state)
        self._player.errorOccurred.connect(self._on_player_error)

    # ── Public API ────────────────────────────────────────────────────────────

    def show_panel(self) -> None:
        """Call once from sig_launcher.py to begin the intro sequence."""
        self._run_title_sequence()

    # ── Title sequence ────────────────────────────────────────────────────────

    def _run_title_sequence(self) -> None:
        """Fade in → hold → fade out. Fires _on_title_done() when complete."""

        # Safety: make sure title widget is on top and visible
        self._title_widget.raise_()
        self._title_widget.show()

        # Attach opacity effect to the LABEL only (most reliable approach)
        self._opacity_effect = QGraphicsOpacityEffect(self._title_label)
        self._title_label.setGraphicsEffect(self._opacity_effect)
        self._opacity_effect.setOpacity(0.0)   # start invisible

        # ── Fade IN ───────────────────────────────────────────────────────
        self._anim_in = QPropertyAnimation(
            self._opacity_effect, b"opacity", self
        )
        self._anim_in.setDuration(TITLE_FADE_IN_MS)
        self._anim_in.setStartValue(0.0)
        self._anim_in.setEndValue(1.0)

        # ── Fade OUT ──────────────────────────────────────────────────────
        self._anim_out = QPropertyAnimation(
            self._opacity_effect, b"opacity", self
        )
        self._anim_out.setDuration(TITLE_FADE_OUT_MS)
        self._anim_out.setStartValue(1.0)
        self._anim_out.setEndValue(0.0)
        self._anim_out.finished.connect(self._on_title_done)

        # Chain: fade-in ends → hold timer → fade-out starts
        def _start_hold() -> None:
            QTimer.singleShot(TITLE_HOLD_MS, self._anim_out.start)

        self._anim_in.finished.connect(_start_hold)
        self._anim_in.start()

    def _on_title_done(self) -> None:
        """Title fully faded out — hand off to video (PATH A) or end (PATH B)."""
        self._title_widget.hide()

        if self._player is not None:
            # PATH A — reveal video widget and play (already buffered)
            self._video_widget.setGeometry(self.rect())
            self._video_widget.show()
            self._video_widget.raise_()
            self._start_video()
        else:
            # PATH B — brief black pause then done
            QTimer.singleShot(FALLBACK_HOLD_MS, self._finish)

    # ── Video playback (PATH A) ───────────────────────────────────────────────

    def _start_video(self) -> None:
        print(f"[SIG Intro]  Playing (pre-cached): {self._video_path.name}")

        self._timeout_timer = QTimer(self)
        self._timeout_timer.setSingleShot(True)
        self._timeout_timer.timeout.connect(self._finish)
        self._timeout_timer.start(VIDEO_TIMEOUT_MS)

        self._player.play()   # resumes from frame 0 — instant, no buffering

    def _on_playback_state(self, state) -> None:
        from PySide6.QtMultimedia import QMediaPlayer as _QMP
        if state == _QMP.PlaybackState.StoppedState:
            self._finish()

    def _on_player_error(self, error, error_string: str) -> None:
        print(f"[SIG Intro]  Player error: {error_string} — falling back.")
        QTimer.singleShot(FALLBACK_HOLD_MS, self._finish)

    # ── Completion ────────────────────────────────────────────────────────────

    def _finish(self) -> None:
        """Emit intro_finished exactly once — however we got here."""
        if self._done:
            return
        self._done = True

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


# ══════════════════════════════════════════════════════════════════════════════
#  Standalone test  —  .venv\Scripts\python.exe ui\intro_panel_widget.py
# ══════════════════════════════════════════════════════════════════════════════

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
    sys.exit(app.exec())
