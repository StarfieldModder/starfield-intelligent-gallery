from PySide6.QtWidgets import QWidget, QLabel, QVBoxLayout
from PySide6.QtCore import Qt, QTimer, QPropertyAnimation, QEasingCurve
from PySide6.QtGui import QFont

class IntroPanel(QWidget):
    def __init__(self):
        super().__init__()

        self.setObjectName("IntroPanel")
        self.setStyleSheet("""
            #IntroPanel {
                background-color: black;
            }
            QLabel {
                color: #66aaff;
                font-size: 48px;
                font-weight: bold;
            }
        """)

        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignCenter)

        # Title label
        self.title = QLabel("The Intelligent Gallery")
        self.title.setAlignment(Qt.AlignCenter)
        self.title.setFont(QFont("Segoe UI", 48))

        layout.addWidget(self.title)
        self.setLayout(layout)

        # Fade animation
        self.fade = QPropertyAnimation(self.title, b"windowOpacity")
        self.fade.setDuration(3000)
        self.fade.setStartValue(0.0)
        self.fade.setEndValue(1.0)
        self.fade.setEasingCurve(QEasingCurve.InOutQuad)

        # After fade-in, fade-out
        self.fade.finished.connect(self.fade_out)

        # Start fade-in
        self.fade.start()

    def fade_out(self):
        fade2 = QPropertyAnimation(self.title, b"windowOpacity")
        fade2.setDuration(3000)
        fade2.setStartValue(1.0)
        fade2.setEndValue(0.0)
        fade2.setEasingCurve(QEasingCurve.InOutQuad)
        fade2.start()
