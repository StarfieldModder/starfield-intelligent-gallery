from PyQt6.QtCore import Qt, QTimer, QEasingCurve, QPropertyAnimation
from PyQt6.QtGui import QPixmap
from PyQt6.QtMultimedia import QAudioOutput, QMediaPlayer
from PyQt6.QtMultimediaWidgets import QVideoWidget  # not used, but kept if you expand later
from PyQt6.QtWidgets import (
    QMainWindow,
    QWidget,
    QLabel,
    QStackedLayout,
    QVBoxLayout,
    QApplication,
    QGraphicsOpacityEffect,
)

import os


class MainWindow(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.setWindowTitle("Starfield Intelligent Gallery")
        self.resize(1600, 900)

        # --- core widgets ---
        self.central = QWidget(self)
        self.setCentralWidget(self.central)

        self.stack = QStackedLayout(self.central)

        # splash container
        self.splash_container = QWidget(self)
        self.splash_layout = QVBoxLayout(self.splash_container)
        self.splash_layout.setContentsMargins(0, 0, 0, 0)
        self.splash_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # large logo
        self.large_logo = QLabel(self.splash_container)
        self.large_logo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.large_logo.setStyleSheet("background-color: white;")
        self.large_logo.setPixmap(QPixmap(r"C:\SIG\Logos\starfield_logo.png"))
        self.large_logo.setScaledContents(True)

        # small icon
        self.small_icon = QLabel(self.splash_container)
        self.small_icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.small_icon.setStyleSheet("background-color: white;")
        self.small_icon.setPixmap(QPixmap(r"C:\SIG\SIG_icon.jpg"))
        self.small_icon.setScaledContents(True)
        self.small_icon.hide()

        self.splash_layout.addWidget(self.large_logo)
        self.splash_layout.addWidget(self.small_icon)

        # main working panel placeholder
        self.main_panel = QWidget(self)
        self.main_panel.setStyleSheet("background-color: #0D0F11;")
        # TODO: here you will embed gallery/sidebar/viewer components

        self.stack.addWidget(self.splash_container)
        self.stack.addWidget(self.main_panel)

        # audio
        self.audio_output = QAudioOutput(self)
        self.player = QMediaPlayer(self)
        self.player.setAudioOutput(self.audio_output)

        # opacity effects
        self.large_opacity = QGraphicsOpacityEffect(self.large_logo)
        self.large_logo.setGraphicsEffect(self.large_opacity)
        self.large_opacity.setOpacity(0.0)

        self.small_opacity = QGraphicsOpacityEffect(self.small_icon)
        self.small_icon.setGraphicsEffect(self.small_opacity)
        self.small_opacity.setOpacity(0.0)

        self.main_opacity = QGraphicsOpacityEffect(self.main_panel)
        self.main_panel.setGraphicsEffect(self.main_opacity)
        self.main_opacity.setOpacity(0.0)

        # start the cinematic startup
        QTimer.singleShot(100, self.play_startup_sequence)

    # ---------- generic fade helper ----------

    def fade_widget(self, widget, effect, start, end, duration, finished_cb=None):
        anim = QPropertyAnimation(effect, b"opacity", widget)
        anim.setStartValue(start)
        anim.setEndValue(end)
        anim.setDuration(duration)
        anim.setEasingCurve(QEasingCurve.Type.InOutCubic)
        if finished_cb:
            anim.finished.connect(finished_cb)
        anim.start(QPropertyAnimation.DeletionPolicy.DeleteWhenStopped)

    # ---------- startup sequence ----------

    def play_startup_sequence(self):
        self.stack.setCurrentWidget(self.splash_container)
        self.large_logo.show()
        self.small_icon.hide()
        self.main_panel.hide()

        # load Bach
        bach_path = r"C:\SIG\Audio\bach_interlude.mp3"
        if os.path.exists(bach_path):
            self.player.setSource(bach_path)

        # fade in large logo + play Bach
        self.fade_widget(self.large_logo, self.large_opacity, 0.0, 1.0, 1500)
        self.player.play()

        # after a pause, transition to small icon
        QTimer.singleShot(3500, self._startup_large_to_small)

    def _startup_large_to_small(self):
        # fade out large logo
        self.fade_widget(
            self.large_logo,
            self.large_opacity,
            1.0,
            0.0,
            1000,
            finished_cb=self._show_small_icon,
        )

    def _show_small_icon(self):
        self.large_logo.hide()
        self.small_icon.show()
        self.fade_widget(self.small_icon, self.small_opacity, 0.0, 1.0, 1000)

        # then fade into main panel
        QTimer.singleShot(2000, self._startup_to_main_panel)

    def _startup_to_main_panel(self):
        # fade out small icon, fade in main panel
        def switch_to_main():
            self.stack.setCurrentWidget(self.main_panel)
            self.main_panel.show()
            self.fade_widget(self.main_panel, self.main_opacity, 0.0, 1.0, 1200)

        self.fade_widget(
            self.small_icon,
            self.small_opacity,
            1.0,
            0.0,
            800,
            finished_cb=switch_to_main,
        )

    # ---------- exit sequence ----------

    def closeEvent(self, event):
        # intercept close, play exit sequence, then really close
        event.ignore()
        self.play_exit_sequence()

    def play_exit_sequence(self):
        # fade out main panel, show small icon, then large logo, then close
        def show_small():
            self.stack.setCurrentWidget(self.splash_container)
            self.main_panel.hide()
            self.small_icon.show()
            self.large_logo.hide()
            self.small_opacity.setOpacity(0.0)
            self.fade_widget(self.small_icon, self.small_opacity, 0.0, 1.0, 800)

            # restart Bach for exit
            bach_path = r"C:\SIG\Audio\bach_interlude.mp3"
            if os.path.exists(bach_path):
                self.player.setSource(bach_path)
            self.player.play()

            QTimer.singleShot(2200, show_large)

        def show_large():
            # fade out small, fade in large
            def swap_to_large():
                self.small_icon.hide()
                self.large_logo.show()
                self.large_opacity.setOpacity(0.0)
                self.fade_widget(self.large_logo, self.large_opacity, 0.0, 1.0, 1000)

                # final pause, then quit
                QTimer.singleShot(2200, QApplication.instance().quit)

            self.fade_widget(
                self.small_icon,
                self.small_opacity,
                1.0,
                0.0,
                700,
                finished_cb=swap_to_large,
            )

        # start by fading out main panel
        self.fade_widget(
            self.main_panel,
            self.main_opacity,
            1.0,
            0.0,
            800,
            finished_cb=show_small,
        )
