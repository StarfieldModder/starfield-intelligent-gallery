# ================================================================
# Starfield Intelligent Gallery (SIG)
# Filename: intro_panel_core.py
# Module: Intro Panel — Core Widget Skeleton
# Version: 2026.06.26 — Modular Edition
# ================================================================

from __future__ import annotations

import sys
from typing import Optional, Dict

from PySide6.QtCore import Qt, QRect
from PySide6.QtWidgets import (
    QWidget, QLabel, QPushButton, QVBoxLayout, QHBoxLayout,
    QApplication, QGraphicsOpacityEffect
)

# Import painter + animation modules
from intro_panel_painter import IntroPanelPainter
from intro_panel_animations import IntroPanelAnimations


class IntroPanelWidget(QWidget):

    # ------------------------------------------------------------
    # Constructor
    # ------------------------------------------------------------
    def __init__(self, app: QApplication, parent: QWidget | None = None) -> None:
        super().__init__(parent)

        self.app = app
        self.background = None

        # Window flags + transparency
        self.setWindowFlags(
            Qt.FramelessWindowHint |
            Qt.WindowStaysOnTopHint
        )
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setAttribute(Qt.WA_NoSystemBackground)
        self.setAttribute(Qt.WA_StyledBackground, False)

        # ------------------------------------------------------------
        # Theme colors
        # ------------------------------------------------------------
        self.panel_color = (80, 150, 255, 90)
        self.border_color = (120, 190, 255, 160)

        self.button_border_color = "rgba(120, 190, 255, 220)"
        self.button_border_color_selected = "rgba(255, 240, 180, 255)"
        self.button_bg_color = "rgba(8, 12, 28, 160)"
        self.button_bg_color_selected = "rgba(18, 26, 60, 220)"
        self.button_text_color = "rgba(210, 230, 255, 230)"

        # ------------------------------------------------------------
        # State
        # ------------------------------------------------------------
        self.buttons_left = []
        self.buttons_right = []
        self.button_original_geometries: Dict[QPushButton, QRect] = {}
        self.selected_button = None
        self.engage_button = None
        self.state = "intro"

        # ------------------------------------------------------------
        # Layout
        # ------------------------------------------------------------
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(40, 40, 40, 40)
        main_layout.setSpacing(30)

        # Title
        self.title_label = QLabel("STARFIELD INTELLIGENT GALLERY")
        self.title_label.setAlignment(Qt.AlignCenter)
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

        # Bottom area (ENGAGE)
        self.bottom_area = QVBoxLayout()
        self.bottom_area.setSpacing(16)
        main_layout.addLayout(self.bottom_area)

        self.setLayout(main_layout)

        # ------------------------------------------------------------
        # Choices
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
            "CREATE MY OWN",
        ]

        self._build_choice_buttons()

        # ------------------------------------------------------------
        # Attach painter + animation engines
        # ------------------------------------------------------------
        self.painter = IntroPanelPainter(self)
        self.anim = IntroPanelAnimations(self)

    # ------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------
    def set_background(self, background_widget: QWidget) -> None:
        self.background = background_widget

    def show_panel(self) -> None:
        self.anim.start_expansion()

    # ------------------------------------------------------------
    # Build choice buttons
    # ------------------------------------------------------------
    def _create_button(self, text: str) -> QPushButton:
        btn = QPushButton(text)
        btn.setCursor(Qt.PointingHandCursor)
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

        # Start transparent
        opacity = QGraphicsOpacityEffect(btn)
        opacity.setOpacity(0.0)
        btn.setGraphicsEffect(opacity)

        btn.clicked.connect(lambda checked=False, b=btn: self.anim.on_choice_clicked(b))
        return btn

    def _build_choice_buttons(self) -> None:
        for text in self.left_choices:
            btn = self._create_button(text)
            self.left_column_layout.addWidget(btn)
            self.buttons_left.append(btn)

        for text in self.right_choices:
            btn = self._create_button(text)
            self.right_column_layout.addWidget(btn)
            self.buttons_right.append(btn)

    # ------------------------------------------------------------
    # Painting
    # ------------------------------------------------------------
    def paintEvent(self, event) -> None:
        self.painter.paint(event)

    # ------------------------------------------------------------
    # Resize
    # ------------------------------------------------------------
    def resizeEvent(self, event) -> None:
        super().resizeEvent(event)
        self.update()


# Standalone launcher
if __name__ == "__main__":
    app = QApplication(sys.argv)
    panel = IntroPanelWidget(app)
    panel.show_panel()
    sys.exit(app.exec())
