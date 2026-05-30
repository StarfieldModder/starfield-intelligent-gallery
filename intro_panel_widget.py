# ================================================================
# Starfield Intelligent Gallery (SIG)
# Filename: intro_panel_widget.py
# Module: Intro Panel Widget — Cinematic Choice Panel
# Version: 2026.05.26 — Two-Column Hologram Edition
# Author: Mark J. Latsha
# Co-Author: Microsoft Copilot (AI Engineering Assistant)
# Location: Brentwood, California — Pacific Daylight Time
#
# Description:
#     Cinematic holographic intro panel displayed during SIG startup.
#     Expands from a small seed into a full panel, then:
#         - slides in 8 deep-space holo buttons (4 left, 4 right)
#         - fades in their labels like warming holograms
#         - lets the user select one, which flies to the top-center
#         - materializes an ENGAGE button at the bottom-center
#         - on ENGAGE, triggers the starfield Jump Cruise sequence
#
# Integration Notes:
#     - Optionally call set_background(starfield_widget) with a
#       StarfieldBackground instance so ENGAGE can call:
#           background.start_jump_cruise()
#     - ESC key returns from ENGAGE state back to choice state.
#
# Launch Command (VS Code, works from ANY folder):
#     python "${file}"
#
# Timestamp:
#     Generated: May 26, 2026 — 6:10 AM PDT
# ================================================================

from __future__ import annotations

import sys
from typing import Optional, Dict

from PyQt6.QtCore import (
    Qt,
    QRect,
    QPoint,
    QPropertyAnimation,
    QEasingCurve,
    QSequentialAnimationGroup,
    QParallelAnimationGroup,
    QPauseAnimation,
)
from PyQt6.QtGui import QColor, QPainter, QBrush
from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QApplication,
    QPushButton,
    QGraphicsOpacityEffect,
)


class IntroPanelWidget(QWidget):
    """
    Cinematic holographic intro panel for SIG startup.

    Sequence:
        1) Panel expands from seed → full frame
        2) 8 buttons slide in (4 left, 4 right)
        3) Labels fade in like holograms
        4) User selects a button → it flies to top-center
        5) ENGAGE appears at bottom-center
        6) ENGAGE triggers starfield Jump Cruise (if background set)
    """

    def __init__(self, app: QApplication, parent: QWidget | None = None) -> None:
        super().__init__(parent)

        self.app = app
        self.background = None  # type: Optional[QWidget]

        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint
            | Qt.WindowType.WindowStaysOnTopHint
        )

        # ------------------------------------------------------------
        # Soft Hologram / Deep-Space theme
        # ------------------------------------------------------------
        self.panel_color = QColor(80, 150, 255, 90)
        self.border_color = QColor(120, 190, 255, 160)

        self.button_border_color = "rgba(120, 190, 255, 220)"
        self.button_border_color_selected = "rgba(255, 240, 180, 255)"
        self.button_bg_color = "rgba(8, 12, 28, 160)"
        self.button_bg_color_selected = "rgba(18, 26, 60, 220)"
        self.button_text_color = "rgba(210, 230, 255, 230)"

        # State
        self.buttons_left: list[QPushButton] = []
        self.buttons_right: list[QPushButton] = []
        self.button_original_geometries: Dict[QPushButton, QRect] = {}
        self.selected_button: Optional[QPushButton] = None
        self.engage_button: Optional[QPushButton] = None
        self.state: str = "intro"  # intro, choices, engage

        # ------------------------------------------------------------
        # Layout + content
        # ------------------------------------------------------------
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(40, 40, 40, 40)
        main_layout.setSpacing(30)

        # Title
        self.title_label = QLabel("STARFIELD INTELLIGENT GALLERY")
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.title_label.setStyleSheet("""
            QLabel {
                color: rgba(200, 220, 255, 230);
                font-size: 32px;
                font-weight: 600;
                letter-spacing: 2px;
            }
        """)
        main_layout.addWidget(self.title_label)

        # Two-column choice area
        columns_layout = QHBoxLayout()
        columns_layout.setSpacing(40)

        self.left_column_layout = QVBoxLayout()
        self.left_column_layout.setSpacing(16)
        self.right_column_layout = QVBoxLayout()
        self.right_column_layout.setSpacing(16)

        columns_layout.addLayout(self.left_column_layout)
        columns_layout.addLayout(self.right_column_layout)

        main_layout.addLayout(columns_layout)

        # Bottom spacer area (for ENGAGE)
        self.bottom_area = QVBoxLayout()
        self.bottom_area.setSpacing(16)
        main_layout.addLayout(self.bottom_area)

        self.setLayout(main_layout)

        # ------------------------------------------------------------
        # Choices (4 left, 4 right)
        # ------------------------------------------------------------
        self.left_choices = [
            "MY STARFIELD JOURNEY",
            "MY COMPANIONS",
            "MY SHIPS",
            "MY PLANETS",
        ]
        self.right_choices = [
            "MY IMAGES",
            "MY VIDEOS",
            "MY NG+ RUNS",
            "CREATE MY OWN",  # non-negotiable, bottom-right
        ]

        self._build_choice_buttons()

        # ------------------------------------------------------------
        # Expansion animation (Hybrid 700ms)
        # ------------------------------------------------------------
        self.expand_anim = QPropertyAnimation(self, b"geometry")
        self.expand_anim.setDuration(700)
        self.expand_anim.setEasingCurve(QEasingCurve.Type.OutCubic)
        self.expand_anim.finished.connect(self._on_expansion_complete)

    # ------------------------------------------------------------
    # Public integration API
    # ------------------------------------------------------------

    def set_background(self, background_widget: QWidget) -> None:
        """
        Optionally attach the starfield background widget so that
        ENGAGE can trigger its Jump Cruise sequence.
        """
        self.background = background_widget

    # ------------------------------------------------------------
    # Panel show / expansion
    # ------------------------------------------------------------

    def show_panel(self) -> None:
        screen_geo = self.app.primaryScreen().availableGeometry()

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

        self.setGeometry(start_rect)
        self.show()

        self.expand_anim.stop()
        self.expand_anim.setStartValue(start_rect)
        self.expand_anim.setEndValue(end_rect)
        self.expand_anim.start()

    def _on_expansion_complete(self) -> None:
        # Once expanded, we enter the "choices" phase and animate buttons in.
        self.state = "choices"
        self._start_choice_intro()

    # ------------------------------------------------------------
    # Choice buttons construction
    # ------------------------------------------------------------

    def _create_button(self, text: str) -> QPushButton:
        btn = QPushButton(text)
        btn.setCursor(Qt.CursorShape.PointingHandCursor)
        btn.setFlat(True)
        btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {self.button_bg_color};
                border: 1px solid {self.button_border_color};
                border-radius: 12px;
                color: {self.button_text_color};
                font-size: 20px;
                font-weight: 500;
                padding: 10px 18px;
                letter-spacing: 1px;
            }}
            QPushButton:hover {{
                border-color: rgba(180, 230, 255, 255);
                background-color: rgba(12, 18, 40, 200);
            }}
        """)

        # Start fully transparent; we'll fade them in.
        opacity = QGraphicsOpacityEffect(btn)
        opacity.setOpacity(0.0)
        btn.setGraphicsEffect(opacity)

        btn.clicked.connect(lambda checked=False, b=btn: self._on_choice_clicked(b))
        return btn

    def _build_choice_buttons(self) -> None:
        # Left column
        for text in self.left_choices:
            btn = self._create_button(text)
            self.left_column_layout.addWidget(btn)
            self.buttons_left.append(btn)

        # Right column
        for text in self.right_choices:
            btn = self._create_button(text)
            self.right_column_layout.addWidget(btn)
            self.buttons_right.append(btn)

    # ------------------------------------------------------------
    # Choice intro animation (slide-in + fade-in)
    # ------------------------------------------------------------

    def _start_choice_intro(self) -> None:
        """
        Slides buttons in from left/right and fades them in.
        """
        if not self.buttons_left and not self.buttons_right:
            return

        # We need actual geometries, so ensure layout is updated.
        self.layout().activate()

        group = QParallelAnimationGroup(self)

        # Left column: slide in from left
        for index, btn in enumerate(self.buttons_left):
            start_rect = btn.geometry()
            self.button_original_geometries[btn] = QRect(start_rect)

            offscreen = QRect(
                start_rect.x() - 200,
                start_rect.y(),
                start_rect.width(),
                start_rect.height(),
            )

            anim = QPropertyAnimation(btn, b"geometry")
            anim.setDuration(700)
            anim.setStartValue(offscreen)
            anim.setEndValue(start_rect)
            anim.setEasingCurve(QEasingCurve.Type.OutCubic)

            seq = QSequentialAnimationGroup()
            seq.addAnimation(QPauseAnimation(index * 120))
            seq.addAnimation(anim)

            # Opacity fade-in
            effect = btn.graphicsEffect()
            if isinstance(effect, QGraphicsOpacityEffect):
                fade = QPropertyAnimation(effect, b"opacity")
                fade.setDuration(600)
                fade.setStartValue(0.0)
                fade.setEndValue(1.0)
                fade.setEasingCurve(QEasingCurve.Type.InOutQuad)

                fade_seq = QSequentialAnimationGroup()
                fade_seq.addAnimation(QPauseAnimation(index * 120 + 150))
                fade_seq.addAnimation(fade)

                group.addAnimation(fade_seq)

            group.addAnimation(seq)

        # Right column: slide in from right
        for index, btn in enumerate(self.buttons_right):
            start_rect = btn.geometry()
            self.button_original_geometries[btn] = QRect(start_rect)

            offscreen = QRect(
                start_rect.x() + 200,
                start_rect.y(),
                start_rect.width(),
                start_rect.height(),
            )

            anim = QPropertyAnimation(btn, b"geometry")
            anim.setDuration(700)
            anim.setStartValue(offscreen)
            anim.setEndValue(start_rect)
            anim.setEasingCurve(QEasingCurve.Type.OutCubic)

            seq = QSequentialAnimationGroup()
            seq.addAnimation(QPauseAnimation(index * 120))
            seq.addAnimation(anim)

            # Opacity fade-in
            effect = btn.graphicsEffect()
            if isinstance(effect, QGraphicsOpacityEffect):
                fade = QPropertyAnimation(effect, b"opacity")
                fade.setDuration(600)
                fade.setStartValue(0.0)
                fade.setEndValue(1.0)
                fade.setEasingCurve(QEasingCurve.Type.InOutQuad)

                fade_seq = QSequentialAnimationGroup()
                fade_seq.addAnimation(QPauseAnimation(index * 120 + 150))
                fade_seq.addAnimation(fade)

                group.addAnimation(fade_seq)

            group.addAnimation(seq)

        group.start(QParallelAnimationGroup.DeletionPolicy.DeleteWhenStopped)

    # ------------------------------------------------------------
    # Choice selection → fly to top-center → ENGAGE
    # ------------------------------------------------------------

    def _on_choice_clicked(self, button: QPushButton) -> None:
        if self.state not in ("choices", "engage"):
            return

        # If already selected and ENGAGE is visible, ignore re-click.
        if self.selected_button is button and self.state == "engage":
            return

        # Clear previous selection visuals
        if self.selected_button and self.selected_button is not button:
            self._set_button_selected(self.selected_button, False)

        self.selected_button = button
        self._set_button_selected(button, True)

        # Animate selected button to top-center
        self._animate_selected_to_top_center(button)

    def _set_button_selected(self, button: QPushButton, selected: bool) -> None:
        if selected:
            button.setStyleSheet(f"""
                QPushButton {{
                    background-color: {self.button_bg_color_selected};
                    border: 1px solid {self.button_border_color_selected};
                    border-radius: 12px;
                    color: {self.button_text_color};
                    font-size: 20px;
                    font-weight: 600;
                    padding: 10px 18px;
                    letter-spacing: 1px;
                }}
                QPushButton:hover {{
                    border-color: rgba(255, 255, 220, 255);
                    background-color: rgba(26, 34, 80, 240);
                }}
            """)
        else:
            button.setStyleSheet(f"""
                QPushButton {{
                    background-color: {self.button_bg_color};
                    border: 1px solid {self.button_border_color};
                    border-radius: 12px;
                    color: {self.button_text_color};
                    font-size: 20px;
                    font-weight: 500;
                    padding: 10px 18px;
                    letter-spacing: 1px;
                }}
                QPushButton:hover {{
                    border-color: rgba(180, 230, 255, 255);
                    background-color: rgba(12, 18, 40, 200);
                }}
            """)

    def _animate_selected_to_top_center(self, button: QPushButton) -> None:
        """
        Moves the selected button to a top-center position and then
        materializes the ENGAGE button.
        """
        if not self.layout():
            return

        panel_rect = self.rect()
        btn_rect = button.geometry()

        target_width = btn_rect.width()
        target_height = btn_rect.height()

        target_x = panel_rect.center().x() - target_width // 2
        target_y = self.title_label.geometry().bottom() + 30

        target_rect = QRect(target_x, target_y, target_width, target_height)

        anim = QPropertyAnimation(button, b"geometry")
        anim.setDuration(700)
        anim.setStartValue(btn_rect)
        anim.setEndValue(target_rect)
        anim.setEasingCurve(QEasingCurve.Type.InOutCubic)

        # Slight "lift" effect via opacity / no, keep it simple: just geometry.
        anim.finished.connect(self._show_engage_button)

        anim.start(QPropertyAnimation.DeletionPolicy.DeleteWhenStopped)
        self.state = "engage"

    def _show_engage_button(self) -> None:
        if self.engage_button is not None:
            return

        self.engage_button = QPushButton("ENGAGE")
        self.engage_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.engage_button.setFlat(True)
        self.engage_button.setStyleSheet("""
            QPushButton {
                background-color: rgba(40, 200, 255, 220);
                border: 1px solid rgba(255, 255, 255, 255);
                border-radius: 16px;
                color: rgba(10, 20, 30, 255);
                font-size: 22px;
                font-weight: 700;
                padding: 12px 26px;
                letter-spacing: 2px;
            }
            QPushButton:hover {
                background-color: rgba(80, 230, 255, 255);
            }
        """)

        # Start invisible
        opacity = QGraphicsOpacityEffect(self.engage_button)
        opacity.setOpacity(0.0)
        self.engage_button.setGraphicsEffect(opacity)

        self.engage_button.clicked.connect(self._on_engage_clicked)

        # Add to bottom area and center it
        self.bottom_area.addWidget(self.engage_button, alignment=Qt.AlignmentFlag.AlignHCenter)

        # Ensure layout is updated so geometry is valid
        self.layout().activate()

        # Fade-in + slight upward slide
        btn_rect = self.engage_button.geometry()
        start_rect = QRect(
            btn_rect.x(),
            btn_rect.y() + 30,
            btn_rect.width(),
            btn_rect.height(),
        )

        slide = QPropertyAnimation(self.engage_button, b"geometry")
        slide.setDuration(600)
        slide.setStartValue(start_rect)
        slide.setEndValue(btn_rect)
        slide.setEasingCurve(QEasingCurve.Type.OutCubic)

        fade = QPropertyAnimation(opacity, b"opacity")
        fade.setDuration(600)
        fade.setStartValue(0.0)
        fade.setEndValue(1.0)
        fade.setEasingCurve(QEasingCurve.Type.InOutQuad)

        group = QParallelAnimationGroup(self)
        group.addAnimation(slide)
        group.addAnimation(fade)
        group.start(QParallelAnimationGroup.DeletionPolicy.DeleteWhenStopped)

    def _on_engage_clicked(self) -> None:
        # Trigger Jump Cruise if background is attached
        if self.background is not None and hasattr(self.background, "start_jump_cruise"):
            try:
                self.background.start_jump_cruise()  # type: ignore[attr-defined]
            except Exception:
                pass

        # Here you can later add: fade-out panel, transition to main Gallery, etc.
        # For now, we simply keep the panel visible as the starfield jumps.

    # ------------------------------------------------------------
    # ESC handling — go back from ENGAGE to choices
    # ------------------------------------------------------------

    def keyPressEvent(self, event) -> None:
        if event.key() == Qt.Key.Key_Escape and self.state == "engage":
            self._reset_from_engage()
            event.accept()
            return
        super().keyPressEvent(event)

    def _reset_from_engage(self) -> None:
        # Hide ENGAGE
        if self.engage_button is not None:
            self.engage_button.hide()
            self.engage_button.deleteLater()
            self.engage_button = None

        # Move selected button back to its original position
        if self.selected_button is not None:
            original = self.button_original_geometries.get(self.selected_button)
            if original is not None:
                anim = QPropertyAnimation(self.selected_button, b"geometry")
                anim.setDuration(600)
                anim.setStartValue(self.selected_button.geometry())
                anim.setEndValue(original)
                anim.setEasingCurve(QEasingCurve.Type.InOutCubic)
                anim.start(QPropertyAnimation.DeletionPolicy.DeleteWhenStopped)

            self._set_button_selected(self.selected_button, False)
            self.selected_button = None

        self.state = "choices"

    # ------------------------------------------------------------
    # Painting
    # ------------------------------------------------------------

    def paintEvent(self, event) -> None:  # type: ignore[override]
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        painter.setBrush(QBrush(self.panel_color))
        painter.setPen(self.border_color)
        painter.drawRoundedRect(self.rect(), 18, 18)

    # ------------------------------------------------------------
    # Resize handling
    # ------------------------------------------------------------

    def resizeEvent(self, event) -> None:  # type: ignore[override]
        super().resizeEvent(event)
        self.update()


# ================================================================
# Standalone Launch Harness (RUNS DIRECTLY)
# ================================================================
if __name__ == "__main__":
    app = QApplication(sys.argv)
    panel = IntroPanelWidget(app)
    panel.show_panel()
    sys.exit(app.exec())
