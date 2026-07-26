from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton, QHBoxLayout
from PySide6.QtCore import Qt
import json
from pathlib import Path

# Intelligence engines
from companion.engines.ingestion_engine import build_gallery_db
from companion.engines.creative_intelligence import analyze_images
from companion.engines.curation_intelligence import curate
from companion.engines.story_intelligence import build_story
from companion.engines.myth_intelligence import build_myth_for_artifacts
from companion.engines.accessibility_intelligence import accessibility_wrap

# Models
from companion.models.sig_image import SIGImage
from companion.models.sig_sequence import SIGSequence

# UI Panels
from companion.ui.creative_panel import CreativePanel
from companion.ui.curation_panel import CurationPanel
from companion.ui.story_panel import StoryPanel
from companion.ui.myth_panel import MythPanel

# Temple Diagnostics
from core.diagnostic_reporter import record_error


class CompanionDashboard(QWidget):
    def __init__(self):
        super().__init__()

        self.gallery_db_path = Path(r"C:\SIG\data\gallery_db.json")
        self.gallery = self.load_gallery_db()

        self.setStyleSheet("""
            background-color: #111827;
            color: #e5e7eb;
            font-size: 18px;
            border: 2px solid #1f2937;
            border-radius: 12px;
        """)

        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignTop)

        # Persona
        persona = QLabel("THE CONDUCTOR — Companion Intelligence Hub")
        persona.setAlignment(Qt.AlignCenter)
        persona.setStyleSheet("""
            font-size: 14px;
            color: #a5b4fc;
            margin-bottom: 10px;
            letter-spacing: 1px;
        """)
        layout.addWidget(persona)

        # Title
        title = QLabel("COMPANION MODE — DASHBOARD")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("""
            font-size: 26px;
            font-weight: bold;
            color: #93c5fd;
            letter-spacing: 2px;
        """)
        layout.addWidget(title)

        subtitle = QLabel("“Select an intelligence engine to begin your exploration.”")
        subtitle.setAlignment(Qt.AlignCenter)
        subtitle.setStyleSheet("""
            font-size: 16px;
            color: #c7d2fe;
            font-style: italic;
        """)
        layout.addWidget(subtitle)

        # Buttons
        button_layout = QHBoxLayout()

        self.btn_creative = QPushButton("Creative Insights")
        self.btn_creative.clicked.connect(self.launch_creative)

        self.btn_curation = QPushButton("Curation Navigator")
        self.btn_curation.clicked.connect(self.launch_curation)

        self.btn_story = QPushButton("Story Dashboard")
        self.btn_story.clicked.connect(self.launch_story)

        self.btn_myth = QPushButton("Myth Dashboard")
        self.btn_myth.clicked.connect(self.launch_myth)

        for btn in [self.btn_creative, self.btn_curation, self.btn_story, self.btn_myth]:
            btn.setStyleSheet("""
                QPushButton {
                    background-color: #1f2937;
                    color: #e5e7eb;
                    padding: 12px;
                    border-radius: 6px;
                    font-size: 16px;
                    border: 1px solid #374151;
                }
                QPushButton:hover {
                    background-color: #374151;
                }
                QPushButton:pressed {
                    background-color: #4b5563;
                }
            """)
            button_layout.addWidget(btn)

        layout.addLayout(button_layout)

        # Refresh button
        self.btn_refresh = QPushButton("Refresh Gallery")
        self.btn_refresh.setStyleSheet("""
            QPushButton {
                background-color: #2563eb;
                color: #e5e7eb;
                padding: 10px;
                border-radius: 6px;
                font-size: 15px;
                border: 1px solid #1d4ed8;
            }
            QPushButton:hover {
                background-color: #1d4ed8;
            }
            QPushButton:pressed {
                background-color: #1e40af;
            }
        """)
        self.btn_refresh.clicked.connect(self.refresh_gallery)
        layout.addWidget(self.btn_refresh)

        # Status
        self.status_label = QLabel(self.get_gallery_status_text())
        self.status_label.setAlignment(Qt.AlignCenter)
        self.status_label.setStyleSheet("""
            font-size: 14px;
            color: #9ca3af;
            margin-top: 10px;
        """)
        layout.addWidget(self.status_label)


    # === Gallery Loading ===

    def load_gallery_db(self):
        if self.gallery_db_path.exists():
            try:
                with open(self.gallery_db_path, "r", encoding="utf-8") as f:
                    db = json.load(f)
                    media = db.get("media", [])
                    return [SIGImage(m["path"]) for m in media]
            except Exception as exc:
                record_error(
                    module="companion_dashboard",
                    function="load_gallery_db",
                    line=0,
                    error_type=type(exc).__name__,
                    message=str(exc),
                    severity="warning",
                    exc=exc,
                )
                return []
        return []


    def refresh_gallery(self):
        try:
            sources = [
                r"C:\SIG\media",
                r"C:\SIG\artifact_renders"
            ]

            build_gallery_db(sources, str(self.gallery_db_path))
            self.gallery = self.load_gallery_db()
            self.status_label.setText(self.get_gallery_status_text())

        except Exception as exc:
            record_error(
                module="companion_dashboard",
                function="refresh_gallery",
                line=0,
                error_type=type(exc).__name__,
                message=str(exc),
                severity="critical",
                exc=exc,
            )


    def get_gallery_status_text(self):
        return f"Gallery Loaded: {len(self.gallery)} media items indexed."


    # === Intelligence Launchers ===

    def launch_creative(self):
        try:
            result = {"images": analyze_images(self.gallery)}
            panel = CreativePanel(result)
            panel.showFullScreen()
        except Exception as exc:
            record_error(
                module="companion_dashboard",
                function="launch_creative",
                line=0,
                error_type=type(exc).__name__,
                message=str(exc),
                severity="critical",
                exc=exc,
            )

    def launch_curation(self):
        try:
            result = curate(self.gallery)
            panel = CurationPanel(result)
            panel.showFullScreen()
        except Exception as exc:
            record_error(
                module="companion_dashboard",
                function="launch_curation",
                line=0,
                error_type=type(exc).__name__,
                message=str(exc),
                severity="critical",
                exc=exc,
            )

    def launch_story(self):
        try:
            seq = SIGSequence(images=self.gallery, theme="Gallery", intensity="medium")
            result = {"story_nodes": build_story([seq])}
            panel = StoryPanel(result)
            panel.showFullScreen()
        except Exception as exc:
            record_error(
                module="companion_dashboard",
                function="launch_story",
                line=0,
                error_type=type(exc).__name__,
                message=str(exc),
                severity="critical",
                exc=exc,
            )

    def launch_myth(self):
        try:
            artifact_names = [Path(img.path).stem for img in self.gallery]
            result = {"myth_elements": build_myth_for_artifacts(artifact_names)}
            panel = MythPanel(result)
            panel.showFullScreen()
        except Exception as exc:
            record_error(
                module="companion_dashboard",
                function="launch_myth",
                line=0,
                error_type=type(exc).__name__,
                message=str(exc),
                severity="critical",
                exc=exc,
            )