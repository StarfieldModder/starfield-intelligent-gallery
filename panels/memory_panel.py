from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton, QTextEdit
from PySide6.QtGui import QFont
from PySide6.QtCore import Qt

HOLO_BG = "#08101F"
HOLO_PANEL = "#0D1D34"
HOLO_ACCENT = "#00B4FF"
HOLO_TEXT = "#D8E8FF"


class MemoryPanel(QWidget):
    def __init__(self, guardian: "GuardianAI", parent=None):
        super().__init__(parent)
        self.guardian = guardian
        self.setWindowTitle("IG Memory Chamber — Starfield Archive")
        self.setMinimumSize(800, 600)
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        self.setStyleSheet(f"background-color: {HOLO_BG}; color: {HOLO_TEXT};")

        title = QLabel("IG MEMORY CHAMBER — STARFIELD ARCHIVE")
        title.setFont(QFont("Consolas", 18, QFont.Bold))
        title.setStyleSheet(f"color: {HOLO_ACCENT};")
        layout.addWidget(title)

        subtitle = QLabel(
            "The Temple’s remembered echoes — anomalies, restorations, and quiet moments of stability."
        )
        subtitle.setFont(QFont("Consolas", 10))
        subtitle.setStyleSheet(f"color: {HOLO_TEXT};")
        layout.addWidget(subtitle)

        self.console = QTextEdit()
        self.console.setReadOnly(True)
        self.console.setStyleSheet(
            f"background-color: {HOLO_PANEL}; color: {HOLO_TEXT}; "
            f"border: 1px solid {HOLO_ACCENT}; font-family: Consolas;"
        )
        layout.addWidget(self.console)

        recall_btn = QPushButton("Recall Memory")
        recall_btn.setStyleSheet(
            f"QPushButton {{ background-color: {HOLO_ACCENT}; color: {HOLO_BG}; "
            f"border: none; padding: 10px; font-weight: bold; }} "
            f"QPushButton:hover {{ background-color: #ffffff22; }}"
        )
        recall_btn.clicked.connect(self._on_recall_memory)
        layout.addWidget(recall_btn)

        layout.addStretch()

    def _on_recall_memory(self):
        response = self.guardian.recall_memory()
        self.console.append(response)
