# C:\SIG\mission_controller\ui.py
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QScrollArea, QFrame
from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap

from .database.schema import get_db

class MissionControllerWidget(QWidget):
    def __init__(self, db, parent=None):
        super().__init__(parent)
        self._db = db
        self._build_ui()

    def _build_ui(self):
        self.setStyleSheet("background-color: #0d0f14; color: #c0ccd8;")
        layout = QVBoxLayout(self)
        layout.setSpacing(12)

        title = QLabel("Database-Backed Mission Controller")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-size: 18px; font-weight: bold;")
        layout.addWidget(title)

        scroll = QScrollArea(self)
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("border: none;")

        container = QWidget()
        vbox = QVBoxLayout(container)
        vbox.setSpacing(20)

        for rec in get_db().get_all_images():
            frame = QFrame()
            f_layout = QVBoxLayout(frame)
            f_layout.setSpacing(6)

            pix = QPixmap(rec.path).scaledToWidth(300, Qt.SmoothTransformation)
            thumb = QLabel()
            thumb.setPixmap(pix)
            thumb.setAlignment(Qt.AlignCenter)
            f_layout.addWidget(thumb)

            meta = QLabel(
                f"{rec.name}<br>{rec.width} × {rec.height}"
            )
            meta.setAlignment(Qt.AlignCenter)
            meta.setStyleSheet("font-size: 12px; color: #5a6472;")
            f_layout.addWidget(meta)

            vbox.addWidget(frame)

        vbox.addStretch()
        scroll.setWidget(container)
        layout.addWidget(scroll)
