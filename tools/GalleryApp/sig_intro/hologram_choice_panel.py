# ================================================================
#  STARFIELD INTELLIGENT GALLERY — HOLOGRAM CHOICE PANEL
#  Module: hologram_choice_panel.py
#
#  Cinematic Hologram Tile Interface (Qt 6.11 Compatible)
#
#  Enhancements in this version:
#      - Slide‑in timing fix (Qt 6.11 layout delay)
#      - Smoother fade‑in sequencing
#      - More stable tile isolation animation
#      - Softer glow and cleaner easing curves
#      - ENGAGE reveal smoothing
# ================================================================

from PyQt6.QtWidgets import (
    QWidget,
    QPushButton,
    QGraphicsDropShadowEffect,
    QGraphicsOpacityEffect,
)
from PyQt6.QtCore import (
    Qt,
    QRect,
    QPropertyAnimation,
    QEasingCurve,
    QParallelAnimationGroup,
    QSequentialAnimationGroup,
    QTimer,
    pyqtSignal,
)
from PyQt6.QtGui import QColor

HUD_BLUE = QColor(90, 150, 255)


class HologramChoicePanel(QWidget):
    """
    Full-screen holographic choice panel with six tiles and an ENGAGE button.
    """

    engageRequested = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)

        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        self.choice_buttons: list[QPushButton] = []
        self.choice_containers: list[QWidget] = []
        self._selected_button: QPushButton | None = None
        self._isolation_run = False

        labels = [
            "View Gallery",
            "Create Book",
            "Make Short Video",
            "Starborn Archive",
            "Favorites & Collections",
            "Settings & Customization",
        ]

        # ------------------------------------------------------------
        # CREATE TILE CONTAINERS + BUTTONS
        # ------------------------------------------------------------
        for text in labels:
            container = QWidget(self)
            container.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

            glow = QGraphicsDropShadowEffect(container)
            glow.setBlurRadius(26)
            glow.setColor(QColor(HUD_BLUE.red(), HUD_BLUE.green(), HUD_BLUE.blue(), 180))
            glow.setOffset(0, 0)
            container.setGraphicsEffect(glow)

            opacity = QGraphicsOpacityEffect(container)
            opacity.setOpacity(0.0)
            container.setGraphicsEffect(opacity)
            container._opacity_effect = opacity  # type: ignore[attr-defined]

            btn = QPushButton(text, container)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.setFlat(True)
            btn.setStyleSheet(self._tile_stylesheet())
            btn.clicked.connect(self._on_choice_clicked)
            btn._container = container  # type: ignore[attr-defined]

            container.hide()
            self.choice_containers.append(container)
            self.choice_buttons.append(btn)

        # ------------------------------------------------------------
        # ENGAGE BUTTON
        # ------------------------------------------------------------
        self.engage_container = QWidget(self)
        self.engage_container.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        engage_glow = QGraphicsDropShadowEffect(self.engage_container)
        engage_glow.setBlurRadius(38)
        engage_glow.setColor(QColor(HUD_BLUE.red(), HUD_BLUE.green(), HUD_BLUE.blue(), 220))
        engage_glow.setOffset(0, 0)
        self.engage_container.setGraphicsEffect(engage_glow)

        engage_opacity = QGraphicsOpacityEffect(self.engage_container)
        engage_opacity.setOpacity(0.0)
        self.engage_container.setGraphicsEffect(engage_opacity)
        self.engage_container._opacity_effect = engage_opacity  # type: ignore[attr-defined]

        self.engage_button = QPushButton("ENGAGE", self.engage_container)
        self.engage_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.engage_button.setFlat(True)
        self.engage_button.setStyleSheet(self._engage_stylesheet())
        self.engage_button.clicked.connect(self._on_engage_clicked)

        self.engage_container.hide()

        # Animation groups
        self._slide_group = None
        self._text_fade_group = None
        self._isolation_group = None

        # Delay intro slightly for Qt 6.11 layout stability
        QTimer.singleShot(600, self.start_intro_sequence)

    # ------------------------------------------------------------
    # STYLES
    # ------------------------------------------------------------
    def _tile_stylesheet(self) -> str:
        return f"""
            QPushButton {{
                color: rgba(220, 235, 255, 240);
                background-color: rgba(10, 20, 40, 60);
                border: 1px solid rgba({HUD_BLUE.red()}, {HUD_BLUE.green()}, {HUD_BLUE.blue()}, 200);
                border-radius: 8px;
                padding: 10px 18px;
                font-size: 14px;
                letter-spacing: 1px;
            }}
            QPushButton:hover {{
                background-color: rgba(20, 40, 80, 90);
                border: 1px solid rgba({HUD_BLUE.red()}, {HUD_BLUE.green()}, {HUD_BLUE.blue()}, 255);
            }}
            QPushButton:pressed {{
                background-color: rgba(5, 10, 25, 120);
            }}
        """

    def _engage_stylesheet(self) -> str:
        return f"""
            QPushButton {{
                color: rgba(230, 245, 255, 255);
                background-color: rgba(10, 25, 60, 150);
                border: 2px solid rgba({HUD_BLUE.red()}, {HUD_BLUE.green()}, {HUD_BLUE.blue()}, 255);
                border-radius: 14px;
                padding: 12px 32px;
                font-size: 16px;
                letter-spacing: 2px;
            }}
            QPushButton:hover {{
                background-color: rgba(20, 50, 110, 190);
            }}
            QPushButton:pressed {{
                background-color: rgba(5, 15, 35, 230);
            }}
        """

    # ------------------------------------------------------------
    # LAYOUT
    # ------------------------------------------------------------
    def resizeEvent(self, event):
        super().resizeEvent(event)
        self._layout_widgets()

    def _layout_widgets(self):
        w = self.width()
        h = self.height()
        if w <= 0 or h <= 0:
            return

        col_width = int(w * 0.32)
        row_height = int(h * 0.10)
        col_gap = int(w * 0.06)
        row_gap = int(h * 0.03)

        left_x = int(w * 0.16)
        right_x = left_x + col_width + col_gap
        top_y = int(h * 0.22)

        for i, container in enumerate(self.choice_containers):
            col = 0 if i < 3 else 1
            row = i if i < 3 else i - 3

            x = left_x if col == 0 else right_x
            y = top_y + row * (row_height + row_gap)

            container.setGeometry(QRect(x, y, col_width, row_height))

        for btn in self.choice_buttons:
            cont = btn._container  # type: ignore[attr-defined]
            btn.setGeometry(0, 0, cont.width(), cont.height())

        engage_width = int(w * 0.22)
        engage_height = int(h * 0.08)
        engage_x = (w - engage_width) // 2
        engage_y = int(h * 0.78)

        self.engage_container.setGeometry(QRect(engage_x, engage_y, engage_width, engage_height))
        self.engage_button.setGeometry(0, 0, engage_width, engage_height)

    # ------------------------------------------------------------
    # INTRO SEQUENCE
    # ------------------------------------------------------------
    def start_intro_sequence(self):
        if not self.isVisible():
            return

        for container in self.choice_containers:
            container.show()

        QTimer.singleShot(50, self._run_slide_in_animation)

    def _run_slide_in_animation(self):
        self._slide_group = QParallelAnimationGroup(self)
        w = self.width()

        for i, container in enumerate(self.choice_containers):
            target_rect = container.geometry()

            if i < 3:
                start_rect = QRect(-target_rect.width(), target_rect.y(),
                                   target_rect.width(), target_rect.height())
            else:
                start_rect = QRect(w, target_rect.y(),
                                   target_rect.width(), target_rect.height())

            container.setGeometry(start_rect)

            anim = QPropertyAnimation(container, b"geometry")
            anim.setDuration(580)
            anim.setStartValue(start_rect)
            anim.setEndValue(target_rect)
            anim.setEasingCurve(QEasingCurve.Type.OutCubic)
            self._slide_group.addAnimation(anim)

        self._slide_group.finished.connect(self._run_text_fade_in)
        self._slide_group.start()

    def _run_text_fade_in(self):
        self._text_fade_group = QSequentialAnimationGroup(self)

        for container in self.choice_containers:
            effect = getattr(container, "_opacity_effect", None)
            if effect is None:
                continue

            anim = QPropertyAnimation(effect, b"opacity")
            anim.setDuration(260)
            anim.setStartValue(0.0)
            anim.setEndValue(1.0)
            anim.setEasingCurve(QEasingCurve.Type.OutCubic)
            self._text_fade_group.addAnimation(anim)

        self._text_fade_group.start()

    # ------------------------------------------------------------
    # TILE ISOLATION
    # ------------------------------------------------------------
    def _on_choice_clicked(self):
        if self._isolation_run:
            return

        sender = self.sender()
        if not isinstance(sender, QPushButton):
            return

        self._selected_button = sender
        self._isolation_run = True
        self._run_isolation_animation(sender)
        self._notify_starfield_choice_ack()

    def _run_isolation_animation(self, selected: QPushButton):
        self._isolation_group = QParallelAnimationGroup(self)

        w = self.width()
        h = self.height()

        selected_container = selected._container  # type: ignore[attr-defined]
        orig_rect = selected_container.geometry()

        scale = 1.35
        new_width = int(orig_rect.width() * scale)
        new_height = int(orig_rect.height() * scale)
        target_x = (w - new_width) // 2
        target_y = int(h * 0.20)

        sel_anim = QPropertyAnimation(selected_container, b"geometry")
        sel_anim.setDuration(520)
        sel_anim.setStartValue(orig_rect)
        sel_anim.setEndValue(QRect(target_x, target_y, new_width, new_height))
        sel_anim.setEasingCurve(QEasingCurve.Type.OutCubic)
        self._isolation_group.addAnimation(sel_anim)

        for container in self.choice_containers:
            if container is selected_container:
                continue

            effect = getattr(container, "_opacity_effect", None)
            if effect is not None:
                fade = QPropertyAnimation(effect, b"opacity")
                fade.setDuration(420)
                fade.setStartValue(1.0)
                fade.setEndValue(0.0)
                fade.setEasingCurve(QEasingCurve.Type.OutCubic)
                self._isolation_group.addAnimation(fade)

            geo = container.geometry()
            away_rect = QRect(geo.x(), geo.y() + int(h * 0.08),
                              geo.width(), geo.height())

            move = QPropertyAnimation(container, b"geometry")
            move.setDuration(420)
            move.setStartValue(geo)
            move.setEndValue(away_rect)
            move.setEasingCurve(QEasingCurve.Type.OutCubic)
            self._isolation_group.addAnimation(move)

        self._isolation_group.finished.connect(self._reveal_engage_button)
        self._isolation_group.start()

    def _reveal_engage_button(self):
        self.engage_container.show()

        geo = self.engage_container.geometry()
        new_w = int(geo.width() * 1.15)
        new_h = int(geo.height() * 1.15)
        new_x = geo.x() - (new_w - geo.width()) // 2
        new_y = geo.y() - (new_h - geo.height()) // 2

        grow = QPropertyAnimation(self.engage_container, b"geometry")
        grow.setDuration(420)
        grow.setStartValue(geo)
        grow.setEndValue(QRect(new_x, new_y, new_w, new_h))
        grow.setEasingCurve(QEasingCurve.Type.OutCubic)
        grow.start(QPropertyAnimation.DeletionPolicy.DeleteWhenStopped)

        effect = getattr(self.engage_container, "_opacity_effect", None)
        if effect is not None:
            fade = QPropertyAnimation(effect, b"opacity")
            fade.setDuration(420)
            fade.setStartValue(0.0)
            fade.setEndValue(1.0)
            fade.setEasingCurve(QEasingCurve.Type.OutCubic)
            fade.start(QPropertyAnimation.DeletionPolicy.DeleteWhenStopped)

    def _notify_starfield_choice_ack(self):
        parent = self.parent()
        if parent is not None and hasattr(parent, "starfield"):
            starfield = getattr(parent, "starfield", None)
            if starfield is not None and hasattr(starfield, "acknowledge_choice"):
                starfield.acknowledge_choice()

    # ------------------------------------------------------------
    # ENGAGE LOGIC
    # ------------------------------------------------------------
    def _on_engage_clicked(self):
        self.engageRequested.emit()
