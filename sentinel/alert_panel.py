# ============================================================
#  ALERT PANEL — Visual System of the Sentinel
#  Location: C:\IG\sentinel\alert_panel.py
#  Role: Soft overlay + Full-screen Temple takeover + Pulse UI
# ============================================================

from PySide6.QtWidgets import QWidget, QLabel, QVBoxLayout, QPushButton
from PySide6.QtGui import QColor, QPalette
from PySide6.QtCore import Qt, QTimer


# ------------------------------------------------------------
#  PULSE COLOR MAP — Cyan heartbeat intensities
# ------------------------------------------------------------
PULSE_COLOR_MAP = {
    "soft": QColor(0, 180, 255, 80),     # gentle cyan
    "medium": QColor(0, 180, 255, 140),  # stronger glow
    "bright": QColor(0, 180, 255, 220),  # intense pulse
}


# ------------------------------------------------------------
#  BASE PANEL CLASS
# ------------------------------------------------------------
class AlertPanel(QWidget):
    def __init__(self, payload, critical=False):
        super().__init__()

        self.payload = payload
        self.critical = critical
        self.pulse_word = payload.get("pulse_word", "soft")

        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.setAttribute(Qt.WA_TranslucentBackground)

        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        self._build_ui()
        self._apply_pulse()
        self._start_pulse_animation()

    # --------------------------------------------------------
    #  UI BUILD
    # --------------------------------------------------------
    def _build_ui(self):
        emotional = QLabel(self.payload["emotional_line"])
        analytical = QLabel(self.payload["analytical_line"])

        emotional.setStyleSheet("color: white; font-size: 26px;")
        analytical.setStyleSheet("color: white; font-size: 20px;")

        self.layout.addWidget(emotional)
        self.layout.addWidget(analytical)

        # Suggestions
        for s in self.payload["suggestions"]:
            suggestion_label = QLabel(f"• {s}")
            suggestion_label.setStyleSheet("color: #A0D8FF; font-size: 18px;")
            self.layout.addWidget(suggestion_label)

        # Buttons (placeholder)
        resume_btn = QPushButton("Resume Program")
        resume_btn.setStyleSheet("background-color: #004466; color: white; padding: 10px;")
        self.layout.addWidget(resume_btn)

    # --------------------------------------------------------
    #  PULSE APPLICATION
    # --------------------------------------------------------
    def _apply_pulse(self):
        pulse_color = PULSE_COLOR_MAP.get(self.pulse_word, PULSE_COLOR_MAP["soft"])

        palette = QPalette()
        palette.setColor(QPalette.Window, pulse_color)
        self.setPalette(palette)

    # --------------------------------------------------------
    #  PULSE ANIMATION — Temple heartbeat
    # --------------------------------------------------------
    def _start_pulse_animation(self):
        self.timer = QTimer()
        self.timer.timeout.connect(self._pulse_tick)
        self.timer.start(900)  # slow heartbeat

    def _pulse_tick(self):
        # Alternate between soft and bright for cinematic override
        if self.pulse_word == "bright":
            self._apply_pulse()
        else:
            # Soft breathing effect
            self._apply_pulse()


# ------------------------------------------------------------
#  PUBLIC FUNCTIONS — Soft vs Hard Alert
# ------------------------------------------------------------
def show_soft_alert(**payload):
    """
    Soft overlay — program visible, Temple whispers.
    """
    panel = AlertPanel(payload, critical=False)
    panel.resize(600, 300)
    panel.show()


def show_hard_alert(**payload):
    """
    Full-screen Temple takeover — Guardian intervenes.
    """
    panel = AlertPanel(payload, critical=True)
    panel.showFullScreen()
