from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QListWidget
from PySide6.QtCore import Qt

class CreativePanel(QWidget):
    def __init__(self, creative_result=None):
        super().__init__()

        self.setStyleSheet("""
            background-color: #0f172a;
            color: #e2e8f0;
            font-size: 16px;
            border: 2px solid #1e1b4b;
            border-radius: 12px;
        """)

        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignTop)

        # Personality header
        persona = QLabel("THE ARTIST — Creative Intelligence Engine")
        persona.setAlignment(Qt.AlignCenter)
        persona.setStyleSheet("""
            font-size: 14px;
            color: #818cf8;
            margin-bottom: 10px;
            letter-spacing: 1px;
        """)
        layout.addWidget(persona)

        # Title
        title = QLabel("CREATIVE INSIGHTS — THE ARTIST")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("""
            font-size: 26px;
            font-weight: bold;
            color: #a5b4fc;
            letter-spacing: 2px;
        """)
        layout.addWidget(title)

        # Subtitle
        subtitle = QLabel("“I see color, mood, and the quiet stories hidden inside your images.”")
        subtitle.setAlignment(Qt.AlignCenter)
        subtitle.setStyleSheet("""
            font-size: 15px;
            color: #c7d2fe;
            font-style: italic;
        """)
        layout.addWidget(subtitle)

        # List widget
        self.list = QListWidget()
        self.list.setStyleSheet("""
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
        layout.addWidget(self.list)

        # Populate if results exist
        if creative_result:
            self.populate(creative_result)

    def populate(self, creative_result):
        images = creative_result.get("images", [])
        for img in images:
            text = (
                f"🎨 {img.path}\n"
                f"   • Mood: {img.emotion}\n"
                f"   • Themes: {', '.join(img.themes)}\n"
                f"   • Tags: {', '.join(img.tags)}"
            )
            self.list.addItem(text)
