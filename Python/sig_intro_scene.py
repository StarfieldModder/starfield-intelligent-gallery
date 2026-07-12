# C:\SIG\Python\sig_intro_scene.py

from PyQt6.QtWidgets import (
    QWidget, QPushButton, QLabel, QVBoxLayout, QHBoxLayout, QGridLayout
)
from PyQt6.QtCore import (
    Qt, QPropertyAnimation, QEasingCurve, QSequentialAnimationGroup, QRect, pyqtSlot
)
from PyQt6.QtGui import QPalette, QColor, QMouseEvent


class IntroScene(QWidget):
    def __init__(self, on_intro_finished):
        super().__init__()

        self.on_intro_finished = on_intro_finished

        self.setAutoFillBackground(True)
        pal = self.palette()
        pal.setColor(QPalette.ColorRole.Window, QColor(0, 0, 0))
        self.setPalette(pal)

        self._build_ui()
        self._build_animations()

        # Start the intro automatically
        self.play_intro()

    def _build_ui(self):
        # Main vertical layout
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(80, 80, 80, 80)
        self.main_layout.setSpacing(40)
        self.main_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Title / mythic line
        self.title_label = QLabel("Traveler…")
        self.title_label.setStyleSheet("color: white; font-size: 32px;")
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.subtitle_label = QLabel("I have waited for you.")
        self.subtitle_label.setStyleSheet("color: #A0C0FF; font-size: 18px;")
        self.subtitle_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # ENGAGE button (precursor moment)
        self.engage_button = QPushButton("ENGAGE")
        self.engage_button.setFixedSize(220, 60)
        self.engage_button.setStyleSheet("""
            QPushButton {
                color: white;
                font-size: 20px;
                border: 2px solid #4FA3FF;
                border-radius: 8px;
                background-color: rgba(20, 40, 80, 180);
            }
            QPushButton:hover {
                background-color: rgba(40, 80, 140, 220);
            }
        """)
        self.engage_button.clicked.connect(self._on_engage_clicked)

        # Six tiles (choice panel proto-form)
        self.tiles_container = QWidget()
        grid = QGridLayout(self.tiles_container)
        grid.setSpacing(16)

        self.tiles = []
        tile_labels = [
            "Journey Records",
            "Starfield Moments",
            "Companions",
            "Artifacts",
            "Timelines",
            "Hidden Paths"
        ]

        for i, text in enumerate(tile_labels):
            tile = QLabel(text)
            tile.setAlignment(Qt.AlignmentFlag.AlignCenter)
            tile.setStyleSheet("""
                QLabel {
                    color: #D0E4FF;
                    font-size: 14px;
                    border: 1px solid #3A5A80;
                    background-color: rgba(10, 20, 40, 180);
                }
            """)
            tile.setVisible(False)  # awaken one by one
            self.tiles.append(tile)
            row, col = divmod(i, 3)
            grid.addWidget(tile, row, col)

        # Scanline shimmer overlay (simple bar)
        self.scanline = QLabel()
        self.scanline.setStyleSheet("background-color: rgba(120, 200, 255, 60);")
        self.scanline.setVisible(False)

        # Layout assembly
        self.main_layout.addWidget(self.title_label)
        self.main_layout.addWidget(self.subtitle_label)
        self.main_layout.addWidget(self.engage_button, alignment=Qt.AlignmentFlag.AlignCenter)
        self.main_layout.addWidget(self.tiles_container)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        # Position scanline to cover tiles area
        if self.tiles_container.isVisible():
            geo = self.tiles_container.geometry()
            self.scanline.setParent(self)
            self.scanline.setGeometry(geo.x(), geo.y(), geo.width(), 6)

    def _build_animations(self):
        self.anim_group = QSequentialAnimationGroup(self)

        # 1) ENGAGE button ignition (pulse)
        self.engage_pulse = QPropertyAnimation(self.engage_button, b"geometry")
        self.engage_pulse.setDuration(600)
        self.engage_pulse.setEasingCurve(QEasingCurve.Type.InOutQuad)

        # 2) Tiles awakening one by one
        self.tile_anims = []
        for tile in self.tiles:
            anim = QPropertyAnimation(tile, b"windowOpacity")
            anim.setDuration(250)
            anim.setStartValue(0.0)
            anim.setEndValue(1.0)
            anim.setEasingCurve(QEasingCurve.Type.InOutQuad)
            self.tile_anims.append(anim)

        # 3) Scanline shimmer
        self.scanline_anim = QPropertyAnimation(self.scanline, b"geometry")
        self.scanline_anim.setDuration(700)
        self.scanline_anim.setEasingCurve(QEasingCurve.Type.InOutQuad)

        # Build sequence
        self.anim_group.currentAnimationChanged.connect(self._on_anim_step_changed)
        self.anim_group.finished.connect(self._on_intro_finished)

    def play_intro(self):
        # Prepare ENGAGE pulse geometry
        btn_geo = self.engage_button.geometry()
        inflated = QRect(btn_geo.x() - 6, btn_geo.y() - 3,
                         btn_geo.width() + 12, btn_geo.height() + 6)
        self.engage_pulse.setStartValue(btn_geo)
        self.engage_pulse.setEndValue(inflated)

        self.anim_group.clear()
        self.anim_group.addAnimation(self.engage_pulse)

        # Tiles: show + fade in sequentially
        for tile, anim in zip(self.tiles, self.tile_anims):
            tile.setWindowOpacity(0.0)
            tile.setVisible(True)
            self.anim_group.addAnimation(anim)

        # Scanline: from top to bottom of tiles
        self.scanline.setVisible(True)
        geo = self.tiles_container.geometry()
        start_rect = QRect(geo.x(), geo.y(), geo.width(), 6)
        end_rect = QRect(geo.x(), geo.y() + geo.height(), geo.width(), 6)
        self.scanline_anim.setStartValue(start_rect)
        self.scanline_anim.setEndValue(end_rect)
        self.anim_group.addAnimation(self.scanline_anim)

        self.anim_group.start()

    def replay_intro(self):
        """Called from MainWindow when R is pressed."""
        self.scanline.setVisible(False)
        for tile in self.tiles:
            tile.setVisible(False)
        self.play_intro()

    @pyqtSlot()
    def _on_engage_clicked(self):
        # Immediate skip to gallery when ENGAGE is pressed
        if self.anim_group.state() == self.anim_group.State.Running:
            self.anim_group.stop()
        self.on_intro_finished()

    def _on_anim_step_changed(self, anim):
        # Hook for future: parallax, subtle color shifts, etc.
        pass

    def _on_intro_finished(self):
        # After full sequence, transition to gallery
        self.on_intro_finished()

    # Simple parallax-aware effect: slight tilt based on mouse
    def mouseMoveEvent(self, event: QMouseEvent):
        cx = self.width() / 2
        cy = self.height() / 2
        dx = (event.position().x() - cx) / cx
        dy = (event.position().y() - cy) / cy

        offset_x = dx * 10
        offset_y = dy * 6

        self.tiles_container.move(
            int(self.width() / 2 - self.tiles_container.width() / 2 + offset_x),
            int(self.height() / 2 - self.tiles_container.height() / 2 + offset_y)
        )
        super().mouseMoveEvent(event)
