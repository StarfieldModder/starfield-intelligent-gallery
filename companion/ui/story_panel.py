from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QListWidget
from PySide6.QtCore import Qt

class StoryPanel(QWidget):
    def __init__(self, story_result=None):
        super().__init__()

        # Panel styling
        self.setStyleSheet("""
            background-color: #0f172a;
            color: #e2e8f0;
            font-size: 16px;
            border: 2px solid #1e3a8a;
            border-radius: 12px;
        """)

        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignTop)

        # Personality header
        persona = QLabel("THE CHRONICLER — Story Intelligence Engine")
        persona.setAlignment(Qt.AlignCenter)
        persona.setStyleSheet("""
            font-size: 14px;
            color: #60a5fa;
            margin-bottom: 10px;
            letter-spacing: 1px;
        """)
        layout.addWidget(persona)

        # Title
        title = QLabel("STORY DASHBOARD — THE CHRONICLER")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("""
            font-size: 26px;
            font-weight: bold;
            color: #93c5fd;
            letter-spacing: 2px;
        """)
        layout.addWidget(title)

        # Subtitle
        subtitle = QLabel("“I trace your journey through chapters, turning points, and emotional arcs.”")
        subtitle.setAlignment(Qt.AlignCenter)
        subtitle.setStyleSheet("""
            font-size: 15px;
            color: #bfdbfe;
            font-style: italic;
        """)
        layout.addWidget(subtitle)

        # Story list
        self.list = QListWidget()
        self.list.setStyleSheet("""
            QListWidget {
                background-color: #1e293b;
                border: none;
                padding: 10px;
            }
            QListWidget::item {
                padding: 10px;
            }
            QListWidget::item:selected {
                background-color: #1e3a8a;
            }
        """)
        layout.addWidget(self.list)

        if story_result:
            self.populate(story_result)

    def populate(self, story_result):
        nodes = story_result.get("story_nodes", [])

        for node in nodes:
            text = (
                f"📘 {node.title}\n"
                f"   • Emotion: {node.emotion}\n"
                f"   • Images: {len(node.images)}"
            )
            self.list.addItem(text)
