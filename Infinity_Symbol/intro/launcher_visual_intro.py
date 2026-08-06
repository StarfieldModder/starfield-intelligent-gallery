# intro/launcher_visual_intro.py
import sys
import math
from pathlib import Path
from PyQt6.QtCore import Qt, QTimer, QUrl, QPropertyAnimation, QEasingCurve
from PyQt6.QtGui import QFont, QPainter, QColor
from PyQt6.QtWidgets import QApplication, QWidget, QLabel, QVBoxLayout, QStackedLayout, QGraphicsOpacityEffect
from PyQt6.QtMultimedia import QMediaPlayer, QAudioOutput
from PyQt6.QtMultimediaWidgets import QVideoWidget

VIDEO_PATH = Path(__file__).resolve().parent / "media" / "The Crossing.mp4"

class StarfieldWidget(QWidget):
    def __init__(self, parent=None, star_count=300):
        super().__init__(parent)
        self.setAttribute(Qt.WidgetAttribute.WA_OpaquePaintEvent)
        self.stars = []
        self.star_count = star_count
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_frame)
        self.speed = 0.02  # base speed factor
        self._init_stars()
        self.timer.start(16)  # ~60 FPS

    def _init_stars(self):
        w, h = max(1, self.width()), max(1, self.height())
        self.stars = []
        for i in range(self.star_count):
            # x,y in normalized coords (-1..1), z depth (0.001..1)
            x = (2 * (i / self.star_count) - 1) * (0.8 + 0.4 * (i % 7) / 7)
            y = (2 * ((i * 37) % self.star_count) / self.star_count - 1) * (0.8 + 0.4 * ((i * 13) % 5) / 5)
            z = 0.001 + (i % 100) / 100.0
            self.stars.append([x, y, z])

    def resizeEvent(self, ev):
        # reinitialize stars to adapt to new size
        self._init_stars()
        super().resizeEvent(ev)

    def update_frame(self):
        # move stars toward viewer by decreasing z
        for s in self.stars:
            s[2] -= self.speed * (0.5 + s[2])  # accelerate as they get closer
            if s[2] <= 0.001:
                # respawn far away
                s[0] = (2 * (math.random() if hasattr(math, "random") else 0.0) - 1)
                s[1] = (2 * (math.random() if hasattr(math, "random") else 0.0) - 1)
                s[2] = 1.0
        self.update()

    def paintEvent(self, ev):
        painter = QPainter(self)
        painter.fillRect(self.rect(), QColor(0, 0, 0))
        w, h = self.width(), self.height()
        cx, cy = w / 2.0, h / 2.0
        for s in self.stars:
            # perspective projection
            z = s[2]
            if z <= 0:
                continue
            sx = cx + (s[0] / z) * (w / 2.5)
            sy = cy + (s[1] / z) * (h / 2.5)
            # size and brightness scale with 1/z
            size = max(1.0, min(6.0, 6.0 * (1.0 / (z * 4.0))))
            bright = int(max(80, min(255, 255 * (1.0 / (z * 2.5)))))
            color = QColor(bright, bright, bright)
            painter.setPen(color)
            painter.setBrush(color)
            painter.drawEllipse(int(sx), int(sy), int(size), int(size))
        painter.end()

class IntroWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Starfield Intelligent Gallery")
        self.setStyleSheet("background-color: black;")
        self.resize(1280, 720)

        # stacked layout: title -> video -> starfield
        self.stack = QStackedLayout()
        self.setLayout(self.stack)

        # Title widget
        self.title_widget = QWidget()
        title_layout = QVBoxLayout(self.title_widget)
        title_layout.setContentsMargins(0, 0, 0, 0)
        title_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.title_label = QLabel("Starfield Intelligent Gallery")
        self.title_label.setStyleSheet("color: white;")
        font = QFont("Arial", 48, QFont.Weight.Bold)
        self.title_label.setFont(font)
        title_layout.addWidget(self.title_label)
        self.stack.addWidget(self.title_widget)

        # Video widget
        self.video_widget = QVideoWidget()
        self.stack.addWidget(self.video_widget)

        # Starfield widget
        self.starfield = StarfieldWidget(self)
        self.stack.addWidget(self.starfield)

        # Media player
        self.player = QMediaPlayer(self)
        audio_output = QAudioOutput(self)
        self.player.setAudioOutput(audio_output)
        self.player.setVideoOutput(self.video_widget)

        # Fade effect for title
        self.opacity = QGraphicsOpacityEffect(self.title_label)
        self.title_label.setGraphicsEffect(self.opacity)
        self.fade_anim = QPropertyAnimation(self.opacity, b"opacity")
        self.fade_anim.setEasingCurve(QEasingCurve.Type.InOutQuad)

        # Start sequence
        QTimer.singleShot(200, self.start_title_sequence)

    def start_title_sequence(self):
        self.stack.setCurrentWidget(self.title_widget)
        # fade in
        self.fade_anim.stop()
        self.fade_anim.setDuration(1200)
        self.fade_anim.setStartValue(0.0)
        self.fade_anim.setEndValue(1.0)
        self.fade_anim.start()
        # after fade in, hold, then fade out
        QTimer.singleShot(2200, self.fade_title_out)

    def fade_title_out(self):
        self.fade_anim.stop()
        self.fade_anim.setDuration(1000)
        self.fade_anim.setStartValue(1.0)
        self.fade_anim.setEndValue(0.0)
        self.fade_anim.start()
        QTimer.singleShot(1200, self.start_video)

    def start_video(self):
        if not VIDEO_PATH.exists():
            print("Video not found:", VIDEO_PATH)
            # skip to starfield if missing
            self.start_starfield()
            return
        self.stack.setCurrentWidget(self.video_widget)
        self.player.setSource(QUrl.fromLocalFile(str(VIDEO_PATH)))
        # play
        self.player.play()
        # when video ends, show starfield
        self.player.mediaStatusChanged.connect(self._on_media_status)

    def _on_media_status(self, status):
        from PyQt6.QtMultimedia import QMediaPlayer as MP
        if status == MP.MediaStatus.EndOfMedia:
            # small delay to ensure clean stop
            QTimer.singleShot(200, self.start_starfield)

    def start_starfield(self):
        self.stack.setCurrentWidget(self.starfield)
        # optionally slow zoom effect by increasing speed gradually
        # keep window open until user closes it

def main():
    app = QApplication(sys.argv)
    w = IntroWindow()
    w.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
