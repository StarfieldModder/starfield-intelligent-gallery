# sig_intro_engine.py
import random
import math
from PySide6.QtCore import QTimer, QEasingCurve, QPointF
from PySide6.QtGui import QColor
from PySide6.QtWidgets import QWidget

class IntroEngine(QWidget):
    def __init__(self):
        super().__init__()
        self.setStyleSheet("background-color: black;")
        self.ignition_level = 0.0
        self.spark_pos = QPointF(0, 0)
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_frame)

        # Randomized timing
        self.pre_ignition_duration = random.uniform(0.8, 1.4)
        self.ignition_duration = 0.3
        self.elapsed = 0.0

        # Easing curves
        self.spark_curve = QEasingCurve(QEasingCurve.OutCubic)

        self.timer.start(16)  # ~60fps

    def update_frame(self):
        self.elapsed += 0.016

        # Phase 1: Pre-Ignition
        if self.elapsed < self.pre_ignition_duration:
            self.ignition_level = 0.0
            self.spark_pos = QPointF(
                random.uniform(-3, 3),
                random.uniform(-3, 3)
            )
            self.update()
            return

        # Phase 2: Ignition Spark
        t = (self.elapsed - self.pre_ignition_duration) / self.ignition_duration
        t = max(0.0, min(1.0, t))
        eased = self.spark_curve.valueForProgress(t)
        self.ignition_level = eased
        self.update()

    def paintEvent(self, event):
        from PySide6.QtGui import QPainter
        p = QPainter(self)

        # Draw ignition spark
        if self.ignition_level > 0:
            radius = 20 * self.ignition_level
            color = QColor(255, 200, 120)
            color.setAlphaF(self.ignition_level)
            p.setBrush(color)
            p.setPen(Qt.NoPen)

            cx = self.width() / 2 + self.spark_pos.x()
            cy = self.height() / 2 + self.spark_pos.y()
            p.drawEllipse(cx - radius, cy - radius, radius * 2, radius * 2)
