from PySide6.QtWidgets import QWidget
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QPainter, QPixmap, QTransform

class ArtifactPanel(QWidget):
    def __init__(self):
        super().__init__()

        self.setObjectName("ArtifactPanel")
        self.setStyleSheet("background-color: black;")

        # Load your ring images (you will provide these PNGs)
        self.ring1 = QPixmap("assets/artifact_ring1.png")
        self.ring2 = QPixmap("assets/artifact_ring2.png")
        self.ring3 = QPixmap("assets/artifact_ring3.png")

        # Rotation angles
        self.angle1 = 0
        self.angle2 = 0
        self.angle3 = 0

        # Timer for animation
        self.timer = QTimer()
        self.timer.setInterval(16)  # ~60 FPS
        self.timer.timeout.connect(self.update_animation)
        self.timer.start()

    def update_animation(self):
        # Rotate each ring at different speeds
        self.angle1 += 1.2
        self.angle2 -= 0.8
        self.angle3 += 2.0

        self.update()  # triggers paintEvent

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        # Center of widget
        cx = self.width() // 2
        cy = self.height() // 2

        # Draw ring 1
        t1 = QTransform().translate(cx, cy).rotate(self.angle1).translate(-self.ring1.width()/2, -self.ring1.height()/2)
        painter.setTransform(t1)
        painter.drawPixmap(0, 0, self.ring1)

        # Draw ring 2
        t2 = QTransform().translate(cx, cy).rotate(self.angle2).translate(-self.ring2.width()/2, -self.ring2.height()/2)
        painter.setTransform(t2)
        painter.drawPixmap(0, 0, self.ring2)

        # Draw ring 3
        t3 = QTransform().translate(cx, cy).rotate(self.angle3).translate(-self.ring3.width()/2, -self.ring3.height()/2)
        painter.setTransform(t3)
        painter.drawPixmap(0, 0, self.ring3)
