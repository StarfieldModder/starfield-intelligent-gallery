# ================================================================
# Starfield Intelligent Gallery (SIG)
# Filename: intro_panel_animations.py
# Module: Intro Panel — Animation Engine
# ================================================================

from PySide6.QtCore import (
    Qt, QRect, QPropertyAnimation, QEasingCurve,
    QSequentialAnimationGroup, QParallelAnimationGroup,
    QPauseAnimation
)
from PySide6.QtWidgets import QPushButton, QGraphicsOpacityEffect


class IntroPanelAnimations:

    def __init__(self, panel):
        self.panel = panel

    # ------------------------------------------------------------
    # Expansion
    # ------------------------------------------------------------
    def start_expansion(self):
        screen_geo = self.panel.app.primaryScreen().availableGeometry()

        seed_w, seed_h = 120, 80
        seed_x = screen_geo.center().x() - seed_w // 2
        seed_y = screen_geo.center().y() - seed_h // 2
        start_rect = QRect(seed_x, seed_y, seed_w, seed_h)

        end_rect = QRect(
            screen_geo.x() + 120,
            screen_geo.y() + 120,
            screen_geo.width() - 240,
            screen_geo.height() - 240,
        )

        self.panel.setGeometry(start_rect)
        self.panel.show()

        anim = QPropertyAnimation(self.panel, b"geometry")
        anim.setDuration(700)
        anim.setStartValue(start_rect)
        anim.setEndValue(end_rect)
        anim.setEasingCurve(QEasingCurve.OutCubic)
        anim.finished.connect(self._on_expansion_complete)

        self.expand_anim = anim
        anim.start()

    def _on_expansion_complete(self):
        self.panel.state = "choices"
        self.start_cinematic_sequence()

    # ------------------------------------------------------------
    # Cinematic sequence
    # ------------------------------------------------------------
    def start_cinematic_sequence(self):
        self._fade_panel()
        self._fade_title()
        self._fade_buttons()
        self._slide_buttons()

    # ------------------------------------------------------------
    # Fade animations
    # ------------------------------------------------------------
    def _fade_panel(self):
        effect = QGraphicsOpacityEffect(self.panel)
        self.panel.setGraphicsEffect(effect)

        anim = QPropertyAnimation(effect, b"opacity")
        anim.setDuration(800)
        anim.setStartValue(0.0)
        anim.setEndValue(1.0)
        anim.setEasingCurve(QEasingCurve.InOutQuad)
        anim.start()

    def _fade_title(self):
        effect = QGraphicsOpacityEffect(self.panel.title_label)
        self.panel.title_label.setGraphicsEffect(effect)

        anim = QPropertyAnimation(effect, b"opacity")
        anim.setDuration(1200)
        anim.setStartValue(0.0)
        anim.setEndValue(1.0)
        anim.setEasingCurve(QEasingCurve.InOutQuad)
        anim.start()

    def _fade_buttons(self):
        group = QSequentialAnimationGroup(self.panel)

        all_buttons = self.panel.buttons_left + self.panel.buttons_right

        for btn in all_buttons:
            effect = btn.graphicsEffect()
            anim = QPropertyAnimation(effect, b"opacity")
            anim.setDuration(600)
            anim.setStartValue(0.0)
            anim.setEndValue(1.0)
            anim.setEasingCurve(QEasingCurve.InOutQuad)
            group.addAnimation(anim)

        group.start()

    # ------------------------------------------------------------
    # Slide-in cinematic
    # ------------------------------------------------------------
    def _slide_buttons(self):
        self.panel.layout().activate()

        group = QParallelAnimationGroup(self.panel)

        # Left column
        for index, btn in enumerate(self.panel.buttons_left):
            start = btn.geometry()
            self.panel.button_original_geometries[btn] = start

            offscreen = QRect(start.x() - 200, start.y(), start.width(), start.height())

            slide = QPropertyAnimation(btn, b"geometry")
            slide.setDuration(700)
            slide.setStartValue(offscreen)
            slide.setEndValue(start)
            slide.setEasingCurve(QEasingCurve.OutCubic)

            seq = QSequentialAnimationGroup()
            seq.addAnimation(QPauseAnimation(index * 120))
            seq.addAnimation(slide)

            group.addAnimation(seq)

        # Right column
        for index, btn in enumerate(self.panel.buttons_right):
            start = btn.geometry()
            self.panel.button_original_geometries[btn] = start

            offscreen = QRect(start.x() + 200, start.y(), start.width(), start.height())

            slide = QPropertyAnimation(btn, b"geometry")
            slide.setDuration(700)
            slide.setStartValue(offscreen)
            slide.setEndValue(start)
            slide.setEasingCurve(QEasingCurve.OutCubic)

            seq = QSequentialAnimationGroup()
            seq.addAnimation(QPauseAnimation(index * 120))
            seq.addAnimation(slide)

            group.addAnimation(seq)

        group.start()

    # ------------------------------------------------------------
    # Choice selection
    # ------------------------------------------------------------
    def on_choice_clicked(self, button: QPushButton):
        if self.panel.state not in ("choices", "engage"):
            return

        # Already selected?
        if self.panel.selected_button is button and self.panel.state == "engage":
            return

        # Clear previous
        if self.panel.selected_button and self.panel.selected_button is not button:
            self._set_button_selected(self.panel.selected_button, False)

        self.panel.selected_button = button
        self._set_button_selected(button, True)

        self.panel.state = "engage"

    def _set_button_selected(self, btn: QPushButton, selected: bool):
        if selected:
            btn.setStyleSheet(btn.styleSheet().replace(
                self.panel.button_border_color,
                self.panel.button_border_color_selected
            ))
        else:
            btn.setStyleSheet(btn.styleSheet().replace(
                self.panel.button_border_color_selected,
                self.panel.button_border_color
            ))
