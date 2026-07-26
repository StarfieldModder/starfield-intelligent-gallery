from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QListWidget
from PySide6.QtCore import Qt

class MythPanel(QWidget):
    def __init__(self, myth_result=None):
        super().__init__()

        # Panel styling
        self.setStyleSheet("""
            background-color: #0f172a;
            color: #e2e8f0;
            font-size: 16px;
            border: 2px solid #4c1d95;
            border-radius: 12px;
        """)

        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignTop)

        # Personality header
        persona = QLabel("THE ORACLE — Myth Intelligence Engine")
        persona.setAlignment(Qt.AlignCenter)
        persona.setStyleSheet("""
            font-size: 14px;
            color: #c084fc;
            margin-bottom: 10px;
            letter-spacing: 1px;
        """)
        layout.addWidget(persona)

        # Title
        title = QLabel("MYTH DASHBOARD — THE ORACLE")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("""
            font-size: 26px;
            font-weight: bold;
            color: #d8b4fe;
            letter-spacing: 2px;
        """)
        layout.addWidget(title)

        # Subtitle
        subtitle = QLabel("“I reveal the lore, symbolism, and cosmic echoes within your artifacts.”")
        subtitle.setAlignment(Qt.AlignCenter)
        subtitle.setStyleSheet("""
            font-size: 15px;
            color: #e9d5ff;
            font-style: italic;
        """)
        layout.addWidget(subtitle)

        # Myth list
        self.list = QListWidget()
        self.list.setStyleSheet("""
            QListWidget {
                background-color: #1e1b4b;
                border: none;
                padding: 10px;
            }
            QListWidget::item {
                padding: 10px;
            }
            QListWidget::item:selected {
                background-color: #4c1d95;
            }
        """)
        layout.addWidget(self.list)

        if myth_result:
            self.populate(myth_result)

    def populate(self, myth_result):
        myth_elements = myth_result.get("myth_elements", {})

        for name, data in myth_elements.items():
            lore = data.get("lore", "No lore available.")
            symbolism = data.get("symbolism", "No symbolism available.")

            text = (
                f"🔮 {name}\n"
                f"   • Lore: {lore}\n"
                f"   • Symbolism: {symbolism}"
            )

            self.list.addItem(text)
