r"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                                                                              ║
║        ███████╗ ██╗  ██████╗   I N T R O _ P A N E L _ W I D G E T . P Y    ║
║        ██╔════╝ ██║ ██╔════╝   Cinematic Title → Cached Video Engine        ║
║        ███████╗ ██║ ██║  ███╗                                                ║
║        ╚════██║ ██║ ██║   ██║  Starfield Intelligent Gallery                 ║
║        ███████║ ██║ ╚██████╔╝                                                ║
║        ╚══════╝ ╚═╝  ╚═════╝   "The moment SIG opens its eyes."             ║
╠══════════════════════════════════════════════════════════════════════════════╣
║  File       :  intro_panel_widget.py                                         ║
║  Location   :  C:\\SIG\\intro\\intro_panel_widget.py                         ║
║  Author     :  Mark J. Latsha  (StarfieldModder / Games)                     ║
║  Co-Author  :  Microsoft Copilot (AI Engineer Colleague)                     ║
║  Version    :  2026.07.03 — Cached Intro Engine Edition                      ║
╠══════════════════════════════════════════════════════════════════════════════╣
║  WHAT THIS FILE IS                                                            ║
║                                                                              ║
║  Controls the SIG intro sequence:                                             ║
║    • Fade-in of the SIG title                                                 ║
║    • Silent caching of “The Crossing”                                         ║
║    • Fade-out of the title                                                    ║
║    • Instant playback of the video                                            ║
║    • Hand-off to Carrier Deck after video ends                                ║
╠══════════════════════════════════════════════════════════════════════════════╣
║  SEQUENCE                                                                     ║
║                                                                              ║
║    1. Black                                                                   ║
║    2. Title fades in (3 seconds)                                              ║
║    3. Video loads silently (muted + hidden)                                   ║
║    4. Video caches (decoder ready)                                            ║
║    5. Title fades out (0.5 seconds)                                           ║
║    6. Video begins instantly                                                  ║
║    7. On completion → Carrier Deck                                            ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""

from PySide6.QtCore import Qt, QPropertyAnimation
from PySide6.QtWidgets import QWidget, QLabel, QVBoxLayout
from PySide6.QtMultimediaWidgets import QVideoWidget
from PySide6.QtMultimedia import QMediaPlayer, QAudioOutput
from PySide6.QtGui import QFont

class IntroPanel(QWidget):
    def __init__(self, video_path, on_finished):
        super().__init__()

        self._on_finished = on_finished

        self.setStyleSheet("background-color: black;")
        self.setWindowFlags(Qt.FramelessWindowHint)

        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignCenter)

        # Title text
        self.title = QLabel("STARFIELD INTELLIGENT GALLERY")
        self.title.setStyleSheet("color: white;")
        self.title.setFont(QFont("Segoe UI", 32))
        self.title.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.title)

        # Video widget (hidden at first)
        self.video_widget = QVideoWidget()
        self.video_widget.setVisible(False)
        layout.addWidget(self.video_widget)

        # Video player
        self.player = QMediaPlayer()
        self.audio = QAudioOutput()
        self.player.setAudioOutput(self.audio)
        self.player.setVideoOutput(self.video_widget)
        self.player.setSource(video_path)

        # Silent caching
        self.audio.setVolume(0.0)
        self.player.play()
        self.player.mediaStatusChanged.connect(self._on_media_ready)
        self.player.playbackStateChanged.connect(self._on_playback_state_changed)

        # Fade-in title
        self.fade_in = QPropertyAnimation(self.title, b"windowOpacity")
        self.fade_in.setDuration(3000)
        self.fade_in.setStartValue(0.0)
        self.fade_in.setEndValue(1.0)
        self.fade_in.start()

    def _on_media_ready(self, status):
        from PySide6.QtMultimedia import QMediaPlayer as MP
        if status == MP.MediaStatus.BufferedMedia:
            self.player.pause()
            self.player.setPosition(0)

            # Fade-out title
            self.fade_out = QPropertyAnimation(self.title, b"windowOpacity")
            self.fade_out.setDuration(500)
            self.fade_out.setStartValue(1.0)
            self.fade_out.setEndValue(0.0)
            self.fade_out.finished.connect(self._start_video)
            self.fade_out.start()

    def _start_video(self):
        self.title.setVisible(False)
        self.video_widget.setVisible(True)
        self.audio.setVolume(1.0)
        self.player.play()

    def _on_playback_state_changed(self, state):
        from PySide6.QtMultimedia import QMediaPlayer as MP
        if state == MP.PlaybackState.StoppedState:
            if self._on_finished:
                self._on_finished()
