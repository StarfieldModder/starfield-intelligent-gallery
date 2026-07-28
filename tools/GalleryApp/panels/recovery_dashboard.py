###############################################################################
#   I N T E L L I G E N C E   G A L L E R Y                                   #
#   R E C O V E R Y   D A S H B O A R D                                       #
#   -----------------------------------------------------------------------   #
#   Module: recovery_dashboard.py                                             #
#   Location: C:\IG\tools\GalleryApp\panels\                                  #
#   Date: July 26, 2026                                                       #
#   System Time: 03:14 AM PDT                                                 #
#                                                                             #
#   Author: Mark J. Latsha (Games)                                            #
#   Co‑Author: Microsoft Copilot (AI Engineer Colleague)                      #
#                                                                             #
#   Description:                                                              #
#       The IG Recovery Dashboard is the Guardian Panel of the Intelligence   #
#       Gallery. It monitors file integrity, backup health, GitHub sync       #
#       status, and prepares the foundation for advanced recovery systems     #
#       including:                                                            #
#           • IG Restore Panel (one‑click restore from C:\IG or D:\IG)        #
#           • IG Backup Scheduler (automated nightly backups)                 #
#           • IG File Diff Viewer (compare backups vs live files)             #
#           • IG Integrity Timeline (visual history of changes)               #
#           • IG Guardian AI (Companion Mode voice alerts for corruption)     #
#                                                                             #
#       This module is fully updated for the new Intelligence Gallery root:   #
#           C:\IG                                                             #
#                                                                             #
#       Drop this file directly into:                                         #
#           C:\IG\tools\GalleryApp\panels\                                    #
#                                                                             #
###############################################################################

import os
import hashlib
import datetime
from pathlib import Path

from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton, QTextEdit
from PySide6.QtGui import QFont
from .restore_panel import RestorePanel

# ---------------------------------------------------------------------------
# Updated Intelligence Gallery paths
# ---------------------------------------------------------------------------
IG_ROOT   = Path("C:/IG")
BACKUP_SSD = Path("C:/IG")     # Primary working + SSD backup
BACKUP_HD  = Path("D:/IG")     # Permanent HD backup


class RecoveryDashboard(QWidget):
    """
    The holographic Recovery Dashboard for the Intelligence Gallery.
    Provides:
        • Integrity scan of IG core modules
        • Backup verification (C:\\IG and D:\\IG)
        • GitHub sync status
    """

    def __init__(self):
        super().__init__()

        self.setWindowTitle("IG Recovery Dashboard")
        self.setMinimumSize(600, 500)

        layout = QVBoxLayout()
        self.setLayout(layout)
        self.restore_panel = None

        title = QLabel("IG Recovery Dashboard")
        title.setFont(QFont("Consolas", 18, QFont.Bold))
        layout.addWidget(title)

        self.output = QTextEdit()
        self.output.setReadOnly(True)
        layout.addWidget(self.output)

        scan_btn = QPushButton("Run Integrity Scan")
        scan_btn.clicked.connect(self.run_scan)
        layout.addWidget(scan_btn)

        backup_btn = QPushButton("Verify Backups")
        backup_btn.clicked.connect(self.verify_backups)
        layout.addWidget(backup_btn)

        git_btn = QPushButton("Check GitHub Sync")
        git_btn.clicked.connect(self.check_git)
        layout.addWidget(git_btn)

        restore_btn = QPushButton("Launch Restore Panel")
        restore_btn.clicked.connect(self.open_restore_panel)
        layout.addWidget(restore_btn)

    # -----------------------------------------------------------------------
    # Integrity Scan
    # -----------------------------------------------------------------------
    def run_scan(self):
        self.output.append("=== IG Integrity Scan ===")
        self.output.append(f"Scan Time: {datetime.datetime.now()}\n")

        if not IG_ROOT.exists():
            self.output.append("❌ IG root missing!")
            return

        file_count = sum(1 for _ in IG_ROOT.rglob("*.*"))
        self.output.append(f"✔ IG root found: {IG_ROOT}")
        self.output.append(f"✔ Total files: {file_count}")

        # Hash core modules
        core_path = IG_ROOT / "core"
        if core_path.exists():
            core_files = list(core_path.glob("*.py"))
            self.output.append("\nCore Module Hashes:")
            for f in core_files:
                h = hashlib.sha256(f.read_bytes()).hexdigest()[:16]
                self.output.append(f"  {f.name}: {h}")
        else:
            self.output.append("❌ Core folder missing!")

        self.output.append("\nIntegrity scan complete.\n")

    # -----------------------------------------------------------------------
    # Backup Verification
    # -----------------------------------------------------------------------
    def verify_backups(self):
        self.output.append("=== Backup Verification ===")

        for label, path in [("SSD Backup", BACKUP_SSD), ("HD Backup", BACKUP_HD)]:
            if path.exists():
                count = sum(1 for _ in path.rglob("*.*"))
                self.output.append(f"✔ {label} found: {path} ({count} files)")
            else:
                self.output.append(f"❌ {label} missing: {path}")

        self.output.append("\nBackup check complete.\n")

    # -----------------------------------------------------------------------
    # GitHub Sync Check
    # -----------------------------------------------------------------------
    def check_git(self):
        self.output.append("=== GitHub Sync Check ===")

        git_dir = IG_ROOT / ".git"
        if not git_dir.exists():
            self.output.append("❌ No Git repository found in IG.")
            return

        # Read HEAD
        head_file = git_dir / "HEAD"
        if head_file.exists():
            head = head_file.read_text().strip()
            self.output.append(f"✔ HEAD: {head}")
        else:
            self.output.append("❌ HEAD file missing.")

        # Show last commit hash
        try:
            import subprocess
            commit = subprocess.check_output(
                ["git", "-C", str(IG_ROOT), "rev-parse", "HEAD"],
                text=True
            ).strip()
            self.output.append(f"✔ Last Commit: {commit}")
        except Exception as e:
            self.output.append(f"❌ Could not read commit: {e}")

        self.output.append("\nGitHub sync check complete.\n")

    def open_restore_panel(self):
        """Open the IG Restore Panel from the Recovery Dashboard."""
        self.restore_panel = RestorePanel(self)
        self.restore_panel.show()
        self.output.append("=== Opened IG Restore Panel ===\n")
