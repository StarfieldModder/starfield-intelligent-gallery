# File: ui/temple_console.py
r"""
╔══════════════════════════════════════════════════════════════════════════════╗
║        ███████╗ ██╗  ██████╗      T E M P L E _ C O N S O L E . P Y          ║
║        ██╔════╝ ██║ ██╔════╝      System Status — Intelligent Gallery        ║
║        ███████╗ ██║ ██║  ███╗      SIG Self‑Diagnostic Panel                 ║
║        ╚════██║ ██║ ██║   ██║     "The Temple listens to the engine."        ║
║        ███████║ ██║ ╚██████╔╝                                                ║
║        ╚══════╝ ╚═╝  ╚═════╝      Location: C:\SIG\ui\temple_console.py      ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""

from __future__ import annotations

import json
from pathlib import Path

from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QLabel,
    QTextEdit,
    QPushButton,
    QHBoxLayout,
)
from PySide6.QtCore import Qt

DIAG_DB_PATH = Path(r"C:\SIG\diagnostics\program_error_database.json")


class TempleConsole(QWidget):
    """
    Temple Console — SIG Self‑Diagnostic Viewer.

    Shows:
      • Recorded errors from program_error_database.json
      • Basic system health summary
    """

    def __init__(self, parent=None) -> None:
        super().__init__(parent)

        self.setWindowTitle("Intelligent Gallery — Temple Console")
        self.setStyleSheet("""
            QWidget {
                background-color: #020617;
                color: #e5e7eb;
                font-family: Segoe UI, sans-serif;
            }
            QLabel#TitleLabel {
                font-size: 22px;
                font-weight: bold;
                color: #93c5fd;
            }
            QLabel#SubtitleLabel {
                font-size: 14px;
                color: #a5b4fc;
            }
            QTextEdit {
                background-color: #0b1120;
                color: #e5e7eb;
                border: 1px solid #1f2937;
                border-radius: 6px;
                font-size: 13px;
            }
            QPushButton {
                background-color: #1f2937;
                color: #e5e7eb;
                padding: 8px 14px;
                border-radius: 6px;
                border: 1px solid #374151;
            }
            QPushButton:hover {
                background-color: #374151;
            }
            QPushButton:pressed {
                background-color: #4b5563;
            }
        """)

        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignTop)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(10)

        title = QLabel("TEMPLE CONSOLE — SYSTEM DIAGNOSTICS")
        title.setObjectName("TitleLabel")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        subtitle = QLabel("“The Gallery speaks when something is wrong.”")
        subtitle.setObjectName("SubtitleLabel")
        subtitle.setAlignment(Qt.AlignCenter)
        layout.addWidget(subtitle)

        # Controls
        button_row = QHBoxLayout()
        self.btn_refresh = QPushButton("Refresh Diagnostics")
        self.btn_clear = QPushButton("Clear Error Log (Soft Reset)")

        self.btn_refresh.clicked.connect(self.refresh_view)
        self.btn_clear.clicked.connect(self.clear_errors)

        button_row.addWidget(self.btn_refresh)
        button_row.addWidget(self.btn_clear)
        layout.addLayout(button_row)

        # System summary
        self.summary_label = QLabel("System Status: Unknown — refresh to load diagnostics.")
        self.summary_label.setAlignment(Qt.AlignLeft)
        self.summary_label.setStyleSheet("font-size: 13px; color: #9ca3af;")
        layout.addWidget(self.summary_label)

        # Error log view
        self.error_view = QTextEdit()
        self.error_view.setReadOnly(True)
        layout.addWidget(self.error_view)

        # Initial load
        self.refresh_view()

    def _load_db(self) -> dict:
        if DIAG_DB_PATH.exists():
            try:
                with open(DIAG_DB_PATH, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception as exc:
                return {
                    "errors": [],
                    "_load_error": str(exc),
                }
        return {"errors": []}

    def refresh_view(self) -> None:
        db = self._load_db()
        errors = db.get("errors", [])

        if not errors:
            self.summary_label.setText("System Status: No recorded errors. (Or diagnostics not yet initialized.)")
            self.error_view.setPlainText(
                "No entries in program_error_database.json.\n\n"
                "Once the Self‑Diagnostic Engine records errors, they will appear here."
            )
            return

        # Build summary
        total = len(errors)
        critical = sum(1 for e in errors if e.get("severity") == "critical")
        warnings = sum(1 for e in errors if e.get("severity") == "warning")
        self.summary_label.setText(
            f"System Status: {total} recorded events — {critical} critical, {warnings} warnings."
        )

        # Build detailed log
        lines: list[str] = []
        for entry in errors:
            ts = entry.get("timestamp", "unknown time")
            module = entry.get("module", "unknown module")
            func = entry.get("function", "unknown function")
            line = entry.get("line", "?")
            etype = entry.get("error_type", "UnknownError")
            msg = entry.get("message", "")
            severity = entry.get("severity", "error")

            lines.append(
                f"[{ts}] ({severity.upper()}) {etype} in {module}:{line} :: {func}\n"
                f"    {msg}\n"
            )

            tb_str = entry.get("traceback")
            if tb_str:
                lines.append("    Traceback:\n")
                for tline in tb_str.splitlines():
                    lines.append(f"        {tline}\n")
            lines.append("\n")

        self.error_view.setPlainText("".join(lines))

    def clear_errors(self) -> None:
        """
        Soft reset: clears the error list in the diagnostics database.
        """
        db = self._load_db()
        db["errors"] = []
        DIAG_DB_PATH.parent.mkdir(parents=True, exist_ok=True)
        with open(DIAG_DB_PATH, "w", encoding="utf-8") as f:
            json.dump(db, f, indent=2)

        self.summary_label.setText("System Status: Error log cleared (soft reset).")
        self.error_view.setPlainText("Error log cleared.\n\nNew diagnostics will appear here as they are recorded.")
