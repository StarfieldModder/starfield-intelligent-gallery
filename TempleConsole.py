# TempleConsole.py
#
# Temple Console UI — Co-Pilot Throne
# PySide6 implementation blueprint for the vertical monolith console.

from PySide6.QtCore import (
    Qt,
    QPropertyAnimation,
    QEasingCurve,
    QRect,
    QTimer,
)
from PySide6.QtGui import (
    QPixmap,
    QFont,
    QColor,
)
from PySide6.QtWidgets import (
    QWidget,
    QFrame,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QScrollArea,
    QTextBrowser,
    QGraphicsOpacityEffect,
)

from PySide6.QtCore import QUrl


try:
    from PySide6.QtMultimedia import QSoundEffect
    HAS_SOUND = True
except ImportError:
    HAS_SOUND = False


class TempleConsole(QFrame):
    """
    TempleConsole — vertical monolith beside the SIG chamber.
    This is the Co-Pilot Throne: quiet, luminous, always-present.
    """

    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)

        self.setObjectName("TempleConsole")
        self.setFrameShape(QFrame.NoFrame)
        self.setFrameShadow(QFrame.Plain)

        # Layout
        self._root_layout = QVBoxLayout(self)
        self._root_layout.setContentsMargins(0, 0, 0, 0)
        self._root_layout.setSpacing(0)

        # Glyph bar (Temple’s voice)
        self._glyph_bar = TempleGlyphBar(self)
        self._root_layout.addWidget(self._glyph_bar)

        # Scroll area (Temple scroll)
        self._scroll_area = QScrollArea(self)
        self._scroll_area.setWidgetResizable(True)
        self._scroll_area.setFrameShape(QFrame.NoFrame)
        self._scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self._scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)

        self._scroll_container = QWidget(self._scroll_area)
        self._scroll_layout = QVBoxLayout(self._scroll_container)
        self._scroll_layout.setContentsMargins(16, 12, 16, 12)
        self._scroll_layout.setSpacing(8)

        self._text_view = QTextBrowser(self._scroll_container)
        self._text_view.setObjectName("TempleTextView")
        self._text_view.setOpenExternalLinks(True)
        self._text_view.setReadOnly(True)
        self._text_view.setFrameShape(QFrame.NoFrame)

        font = QFont("Segoe UI Variable Display", 11)
        font.setWeight(QFont.Normal)
        self._text_view.setFont(font)

        self._scroll_layout.addWidget(self._text_view)
        self._scroll_container.setLayout(self._scroll_layout)
        self._scroll_area.setWidget(self._scroll_container)

        self._root_layout.addWidget(self._scroll_area)

        # Visual effects
        self._init_styles()
        self._init_glow_animation()
        self._init_activation_effects()
        self._init_temple_hum()

        # Start subtle glow loop
        self._glow_timer = QTimer(self)
        self._glow_timer.timeout.connect(self._start_glow_cycle)
        self._glow_timer.start(40000)  # every 40 seconds

        # Initial activation
        self.activate_console()

    # -------------------------------------------------------------------------
    # Public API
    # -------------------------------------------------------------------------

    def append_message(self, text: str, from_user: bool = True):
        """
        Append a line of text to the Temple scroll.
        from_user=True  -> architect’s voice
        from_user=False -> co-pilot voice
        """
        if from_user:
            prefix = '<span style="color:#f5e6c8;">You:</span> '
        else:
            prefix = '<span style="color:#c8e6ff;">Co-Pilot:</span> '

        html = f"{prefix}{text}<br/>"
        self._text_view.insertHtml(html)
        self._text_view.moveCursor(self._text_view.textCursor().End)

        # Animate glyph based on who spoke
        if from_user:
            self._glyph_bar.pulse()
        else:
            self._glyph_bar.rotate()

        # Soft shimmer on scroll
        self._shimmer_scroll()

    def set_context_glyph(self, glyph_name: str):
        """
        Change glyph based on context:
        'awaken', 'threshold', 'memory', 'journey', 'temple', etc.
        """
        self._glyph_bar.set_glyph(glyph_name)

    def activate_console(self):
        """
        Activation sequence — Temple breath.
        """
        self._start_activation_animation()
        self._play_temple_hum()

    # -------------------------------------------------------------------------
    # Internal setup
    # -------------------------------------------------------------------------

    def _init_styles(self):
        # Base QSS for TempleConsole and scrollbars
        self.setStyleSheet("""
        #TempleConsole {
            border-left: 2px solid rgba(255, 240, 200, 0.18); /* Temple Gold */
            background-color: #0e0e0f; /* Temple Stone */
            background-image: url("assets/temple_stone.png");
            background-repeat: no-repeat;
            background-position: center;
    #    background-size: cover;
        }

        #TempleTextView {
            background: transparent;
            color: #e8e4d9; /* Temple parchment */
            border: none;
        }

        QScrollArea {
            border: none;
            background: transparent;
        }

        QScrollBar:vertical {
            background: transparent;
            width: 6px;
            margin: 0px;
        }

        QScrollBar::handle:vertical {
            background: rgba(255, 240, 200, 0.25);
            border-radius: 3px;
        }

        QScrollBar::add-line:vertical,
        QScrollBar::sub-line:vertical {
            background: transparent;
            height: 0px;
        }
        """)

    def _init_glow_animation(self):
        # Animate border color via a dummy property using graphics effect
        self._glow_effect = QGraphicsOpacityEffect(self)
        self.setGraphicsEffect(self._glow_effect)

        self._glow_anim = QPropertyAnimation(self._glow_effect, b"opacity", self)
        self._glow_anim.setDuration(4000)
        self._glow_anim.setStartValue(0.9)
        self._glow_anim.setEndValue(1.0)
        self._glow_anim.setEasingCurve(QEasingCurve.InOutQuad)
        self._glow_anim.finished.connect(self._reset_glow_opacity)

    def _reset_glow_opacity(self):
        self._glow_effect.setOpacity(1.0)

    def _start_glow_cycle(self):
        self._glow_anim.stop()
        self._glow_anim.setStartValue(0.9)
        self._glow_anim.setEndValue(1.0)
        self._glow_anim.start()

    def _init_activation_effects(self):
        # Fade-in effect for the whole console
        self._activation_effect = QGraphicsOpacityEffect(self)
        self.setGraphicsEffect(self._activation_effect)
        self._activation_effect.setOpacity(0.0)

        self._activation_anim = QPropertyAnimation(self._activation_effect, b"opacity", self)
        self._activation_anim.setDuration(900)
        self._activation_anim.setStartValue(0.0)
        self._activation_anim.setEndValue(1.0)
        self._activation_anim.setEasingCurve(QEasingCurve.InOutQuad)

    def _start_activation_animation(self):
        self._activation_anim.stop()
        self._activation_effect.setOpacity(0.0)
        self._activation_anim.start()

    def _init_temple_hum(self):
        self._sound_effect = None
        if HAS_SOUND:
            self._sound_effect = QSoundEffect(self)
            self._sound_effect.setSource(
                # Adjust path as needed for your SIG assets structure
                QUrl.fromLocalFile("assets/temple_hum.wav")
            )
            self._sound_effect.setLoopCount(QSoundEffect.Infinite)
            self._sound_effect.setVolume(0.03)  # 3% volume

    def _play_temple_hum(self):
        if self._sound_effect is not None:
            self._sound_effect.play()

    def _shimmer_scroll(self):
        # Placeholder for subtle shimmer effect on scroll.
        # You can later add a gradient overlay or minor background shift.
        pass


class TempleGlyphBar(QFrame):
    """
    TempleGlyphBar — the Temple’s voice.
    Displays a glyph that pulses, rotates, and changes with context.
    """

    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)

        self.setObjectName("TempleGlyphBar")
        self.setFrameShape(QFrame.NoFrame)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 8, 0, 8)
        layout.setSpacing(0)

        self._glyph_label = QLabel(self)
        self._glyph_label.setAlignment(Qt.AlignCenter)

        layout.addWidget(self._glyph_label)

        # Default glyph
        self._current_glyph = "temple"
        self._load_glyph(self._current_glyph)

        # Simple opacity animation for pulse
        self._pulse_effect = QGraphicsOpacityEffect(self._glyph_label)
        self._glyph_label.setGraphicsEffect(self._pulse_effect)

        self._pulse_anim = QPropertyAnimation(self._pulse_effect, b"opacity", self)
        self._pulse_anim.setDuration(400)
        self._pulse_anim.setStartValue(1.0)
        self._pulse_anim.setEndValue(0.6)
        self._pulse_anim.setEasingCurve(QEasingCurve.InOutQuad)
        self._pulse_anim.finished.connect(self._reset_pulse)

    def set_glyph(self, glyph_name: str):
        self._current_glyph = glyph_name
        self._load_glyph(glyph_name)

    def _load_glyph(self, glyph_name: str):
        # Map glyph names to asset files
        glyph_map = {
            "awaken": "assets/glyph_awaken.png",
            "threshold": "assets/glyph_threshold.png",
            "memory": "assets/glyph_memory.png",
            "journey": "assets/glyph_journey.png",
            "temple": "assets/glyph_temple.png",
        }

        path = glyph_map.get(glyph_name, glyph_map["temple"])
        pixmap = QPixmap(path)
        if not pixmap.isNull():
            self._glyph_label.setPixmap(
                pixmap.scaled(48, 48, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            )
        else:
            self._glyph_label.setText("⟡")  # fallback symbol

    def pulse(self):
        self._pulse_anim.stop()
        self._pulse_effect.setOpacity(1.0)
        self._pulse_anim.setStartValue(1.0)
        self._pulse_anim.setEndValue(0.6)
        self._pulse_anim.start()

    def _reset_pulse(self):
        self._pulse_effect.setOpacity(1.0)

    def rotate(self):
        # Placeholder: you can later add a rotation animation using QGraphicsTransform
        self.pulse()  # for now, reuse pulse as subtle response

# ================================================================
#   S T A R F I E L D   I N T E L L I G E N T   G A L L E R Y
#   ------------------------------------------------------------
#   SIG STARTUP SEQUENCE — Temple Console Launcher
#   Author: Games
#   Co‑Author: Copilot
#   ------------------------------------------------------------
#   Launch Command:
#       python TempleConsole.py
# ================================================================

if __name__ == "__main__":
    import sys
    from PySide6.QtWidgets import QApplication
    from PySide6.QtCore import Qt

    # ------------------------------------------------------------
    # 1. Create SIG Application
    # ------------------------------------------------------------
    app = QApplication(sys.argv)

    # ------------------------------------------------------------
    # 2. Instantiate Temple Console
    # ------------------------------------------------------------
    console = TempleConsole()
    console.setWindowTitle("Intelligent Gallery — Temple Console")

    # ------------------------------------------------------------
    # 3. Cinematic Window Flags
    # ------------------------------------------------------------
    console.setWindowFlags(
        Qt.Window |
        Qt.FramelessWindowHint |
        Qt.WindowStaysOnTopHint
    )

    # ------------------------------------------------------------
    # 4. Initial Size / Position
    # ------------------------------------------------------------
    console.resize(1280, 900)

    # ------------------------------------------------------------
    # 5. SIG Boot Message
    # ------------------------------------------------------------
    try:
        console._text_view.append(
            "<h2>🜂 SIG Temple Console Activated</h2>"
            "<p>The Temple awakens. Systems online.</p>"
        )
    except Exception:
        pass

    # ------------------------------------------------------------
    # 6. Mission Controller Integration (if present)
    # ------------------------------------------------------------
    try:
        from SIG_MC_01_sig_mission_controller_integration import MissionController
        mc = MissionController(console)
        mc.initialize()
        console._text_view.append("<p>Mission Controller: <b>Online</b></p>")
    except Exception:
        console._text_view.append("<p>Mission Controller: <b>Not Found</b></p>")

    # ------------------------------------------------------------
    # 7. Child Widget Anchoring (Alpha / Beta)
    # ------------------------------------------------------------
    try:
        from SIG_MC_02_temple_child_widget_alpha import TempleChildWidgetAlpha
        from SIG_MC_03_temple_child_widget_beta import TempleChildWidgetBeta

        alpha = TempleChildWidgetAlpha(console)
        beta = TempleChildWidgetBeta(console)

        console._scroll_layout.addWidget(alpha)
        console._scroll_layout.addWidget(beta)

        console._text_view.append("<p>Child Widgets: <b>Alpha + Beta Anchored</b></p>")
    except Exception:
        console._text_view.append("<p>Child Widgets: <b>Not Found</b></p>")

    # ------------------------------------------------------------
    # 8. Show Console
    # ------------------------------------------------------------
    console.show()

    # ------------------------------------------------------------
    # 9. Begin SIG Event Loop
    # ------------------------------------------------------------
    sys.exit(app.exec())
