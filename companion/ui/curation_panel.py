from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QListWidget
from PySide6.QtCore import Qt

class CurationPanel(QWidget):
    def __init__(self, curation_result=None):
        super().__init__()

        # Panel styling
        self.setStyleSheet("""
            background-color: #0f172a;
            color: #e2e8f0;
            font-size: 16px;
            border: 2px solid #0c4a6e;
            border-radius: 12px;
        """)

        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignTop)

        # Personality header
        persona = QLabel("THE ARCHIVIST — Curation Intelligence Engine")
        persona.setAlignment(Qt.AlignCenter)
        persona.setStyleSheet("""
            font-size: 14px;
            color: #7dd3fc;
            margin-bottom: 10px;
            letter-spacing: 1px;
        """)
        layout.addWidget(persona)

        # Title
        title = QLabel("CURATION NAVIGATOR — THE ARCHIVIST")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("""
            font-size: 26px;
            font-weight: bold;
            color: #38bdf8;
            letter-spacing: 2px;
        """)
        layout.addWidget(title)

        # Subtitle
        subtitle = QLabel("“I organize your gallery into wings, clusters, and thematic constellations.”")
        subtitle.setAlignment(Qt.AlignCenter)
        subtitle.setStyleSheet("""
            font-size: 15px;
            color: #bae6fd;
            font-style: italic;
        """)
        layout.addWidget(subtitle)

        # Wing label
        wing_label = QLabel("Gallery Wings:")
        wing_label.setStyleSheet("font-size: 18px; color: #bfdbfe; margin-top: 20px;")
        layout.addWidget(wing_label)

        # Wing list
        self.wing_list = QListWidget()
        self.wing_list.setStyleSheet("""
            QListWidget {
                background-color: #1e293b;
                border: none;
                padding: 10px;
            }
            QListWidget::item {
                padding: 8px;
            }
            QListWidget::item:selected {
                background-color: #334155;
            }
        """)
        layout.addWidget(self.wing_list)

        # Cluster label
        cluster_label = QLabel("Theme Clusters:")
        cluster_label.setStyleSheet("font-size: 18px; color: #bfdbfe; margin-top: 20px;")
        layout.addWidget(cluster_label)

        # Cluster list
        self.cluster_list = QListWidget()
        self.cluster_list.setStyleSheet("""
            QListWidget {
                background-color: #1e293b;
                border: none;
                padding: 10px;
            }
            QListWidget::item {
                padding: 8px;
            }
            QListWidget::item:selected {
                background-color: #334155;
            }
        """)
        layout.addWidget(self.cluster_list)

        # Populate if data exists
        if curation_result:
            self.populate(curation_result)

    def populate(self, curation_result):
        wings = curation_result.get("wings", {})
        clusters = curation_result.get("clusters", {})

        # Populate wings
        for wing_name in wings.keys():
            self.wing_list.addItem(f"📁 Wing: {wing_name}")

        # Populate clusters
        for theme, imgs in clusters.items():
            self.cluster_list.addItem(f"🔷 Cluster: {theme} — {len(imgs)} images")
