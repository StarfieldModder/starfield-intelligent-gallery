###############################################################################
#  IG ∞∞∞ — The Temple Crest
#  Intelligent Gallery
#  RESTORE PANEL MODULE
#  “Guardian of the Core State”
#  Authors: Mark J. Latsha & Copilot
#  Python 3.13
#
#  Purpose:
#    Provide cinematic restore capabilities for the Intelligence Gallery.
#    Restore from SSD and HD backups, create pre-restore snapshot commits,
#    verify integrity, and notify Guardian AI of restoration events.
###############################################################################

import os
import shutil
import hashlib
import datetime
import json
import subprocess
from pathlib import Path
from typing import Optional, Dict, List
from dataclasses import dataclass
from enum import Enum

try:
    from PySide6.QtWidgets import (
        QWidget, QVBoxLayout, QHBoxLayout,
        QLabel, QPushButton, QTextEdit, QProgressBar,
        QComboBox, QMessageBox, QSizePolicy
    )
    from PySide6.QtGui import QFont
    from PySide6.QtCore import Qt, Signal, QObject, QThread
    PYSIDE6_AVAILABLE = True
except ImportError:
    PYSIDE6_AVAILABLE = False

IG_ROOT = Path("C:/IG")
BACKUP_SSD = Path("C:/IG/backups/ssd")
BACKUP_HD = Path("D:/IG/backups/hd")
LOG_DIR = IG_ROOT / "logs"
GUARDIAN_LOG = LOG_DIR / "guardian_notifications.log"
COMPANION_LOG = LOG_DIR / "companion_notifications.log"

CORE_MODULES = ["core", "mission_controller", "ui", "config", "data"]
PRESERVE_PATTERNS = [".venv", "__pycache__", ".pytest_cache", "*.log", "session-state"]

HOLO_BG = "#08101F"
HOLO_PANEL = "#0D1D34"
HOLO_ACCENT = "#00B4FF"
HOLO_SUCCESS = "#00FF9C"
HOLO_WARNING = "#FFB300"
HOLO_ERROR = "#FF4B61"
HOLO_TEXT = "#D8E8FF"


class RestoreSource(Enum):
    SSD = "SSD"
    HD = "HD"


class RestoreStatus(Enum):
    IDLE = "idle"
    PRE_CHECK = "pre_check"
    SNAPSHOT = "snapshot"
    VERIFYING = "verifying"
    RESTORING = "restoring"
    POST_VERIFY = "post_verify"
    NOTIFYING = "notifying"
    COMPLETE = "complete"
    FAILED = "failed"


@dataclass
class RestoreReport:
    status: RestoreStatus
    source: RestoreSource
    timestamp: datetime.datetime
    files_restored: int
    files_verified: int
    integrity_ok: bool
    snapshot_hash: Optional[str]
    guardian_notified: bool
    errors: List[str]
    warnings: List[str]
    partial: bool = False


class IntegrityChecker:
    def __init__(self, base: Path = IG_ROOT):
        self.base = base

    def compute_hash(self, path: Path) -> str:
        hasher = hashlib.sha256()
        with path.open("rb") as fh:
            for chunk in iter(lambda: fh.read(8192), b""):
                hasher.update(chunk)
        return hasher.hexdigest()

    def _should_skip(self, path: Path) -> bool:
        for pattern in PRESERVE_PATTERNS:
            if pattern.startswith("*") and path.match(pattern):
                return True
            if pattern in str(path):
                return True
        return False

    def scan(self, directory: Path) -> Dict[str, str]:
        hashes = {}
        if not directory.exists():
            return hashes

        for pattern in ["**/*.py", "**/*.json", "**/*.toml", "**/*.ini"]:
            for file_path in directory.glob(pattern):
                if file_path.is_file() and not self._should_skip(file_path):
                    hashes[str(file_path.relative_to(directory))] = self.compute_hash(file_path)
        return hashes

    def verify(self, directory: Path) -> (bool, List[str], int):
        errors = []
        if not directory.exists():
            return False, [f"Backup source does not exist: {directory}"], 0

        for module in CORE_MODULES:
            candidate = directory / module
            if not candidate.exists():
                errors.append(f"Missing expected module: {module}")

        files = self.scan(directory)
        return len(errors) == 0, errors, len(files)


class GitSnapshotManager:
    def __init__(self, repo_root: Path = IG_ROOT):
        self.repo_root = repo_root

    def _run_git(self, args: List[str]) -> Optional[str]:
        try:
            result = subprocess.run(
                ["git", "-C", str(self.repo_root)] + args,
                capture_output=True,
                text=True,
                check=True,
                timeout=30,
            )
            return result.stdout.strip()
        except Exception:
            return None

    def snapshot(self, message: str) -> Optional[str]:
        if not (self.repo_root / ".git").exists():
            return None

        self._run_git(["add", "-A"])
        commit = self._run_git(["commit", "-m", message, "--allow-empty"])
        if commit is None:
            return None
        return self._run_git(["rev-parse", "HEAD"])


class GuardianAINotifier:
    def __init__(self):
        self.log_dir = LOG_DIR
        self.log_dir.mkdir(parents=True, exist_ok=True)

    def notify(self, report: RestoreReport) -> bool:
        message = self._build_message(report)
        try:
            with GUARDIAN_LOG.open("a", encoding="utf-8") as fh:
                fh.write(f"[{report.timestamp.isoformat()}] {message}\n")
            with COMPANION_LOG.open("a", encoding="utf-8") as fh:
                fh.write(f"[{report.timestamp.isoformat()}] RESTORE: {message}\n")
            return True
        except Exception:
            return False

    def _build_message(self, report: RestoreReport) -> str:
        status = "completed successfully" if report.status == RestoreStatus.COMPLETE else "failed"
        source = report.source.value
        partial_text = "partial restore" if report.partial else "full restore"
        integrity_text = "Integrity verified" if report.integrity_ok else "Integrity issues detected"
        return (
            f"{partial_text.capitalize()} from {source} backup {status}. "
            f"{report.files_restored} files restored, {report.files_verified} files verified. {integrity_text}."
        )


class RestoreWorker(QObject):
    progress = Signal(int)
    status = Signal(str)
    finished = Signal(object)
    error = Signal(str)

    def __init__(self, source: RestoreSource, partial: bool = False):
        super().__init__()
        self.source = source
        self.partial = partial

    def run(self):
        report = RestoreReport(
            status=RestoreStatus.IDLE,
            source=self.source,
            timestamp=datetime.datetime.now(),
            files_restored=0,
            files_verified=0,
            integrity_ok=False,
            snapshot_hash=None,
            guardian_notified=False,
            errors=[],
            warnings=[],
            partial=self.partial,
        )
        try:
            self.status.emit("Performing pre-restore checks...")
            report.status = RestoreStatus.PRE_CHECK
            self.progress.emit(10)

            backup_root = BACKUP_SSD if self.source == RestoreSource.SSD else BACKUP_HD
            if not backup_root.exists():
                raise RuntimeError(f"Backup source unavailable: {backup_root}")

            self.status.emit("Creating pre-restore snapshot...")
            report.status = RestoreStatus.SNAPSHOT
            snapshot = GitSnapshotManager().snapshot(f"Pre-restore snapshot ({self.source.value})")
            report.snapshot_hash = snapshot
            self.progress.emit(25)

            self.status.emit("Verifying backup integrity...")
            report.status = RestoreStatus.VERIFYING
            checker = IntegrityChecker(backup_root)
            ok, errors, count = checker.verify(backup_root)
            report.files_verified = count
            if not ok:
                report.errors.extend(errors)
                raise RuntimeError("Backup integrity verification failed.")
            self.progress.emit(40)

            self.status.emit("Restoring files...")
            report.status = RestoreStatus.RESTORING
            report.files_restored = self._restore_backup(backup_root)
            self.progress.emit(70)

            self.status.emit("Verifying restored content...")
            report.status = RestoreStatus.POST_VERIFY
            post_ok, post_errors, post_count = IntegrityChecker().verify(IG_ROOT)
            report.integrity_ok = post_ok
            report.files_verified = post_count
            if not post_ok:
                report.errors.extend(post_errors)
            self.progress.emit(85)

            self.status.emit("Notifying Guardian AI...")
            report.status = RestoreStatus.NOTIFYING
            report.guardian_notified = GuardianAINotifier().notify(report)
            self.progress.emit(95)

            report.status = RestoreStatus.COMPLETE
            self.progress.emit(100)
        except Exception as exc:
            report.status = RestoreStatus.FAILED
            report.errors.append(str(exc))
            self.error.emit(str(exc))
        finally:
            self.finished.emit(report)

    def _restore_backup(self, backup_root: Path) -> int:
        target = IG_ROOT
        restored = 0
        if self.partial:
            candidates = [backup_root / folder for folder in CORE_MODULES]
        else:
            candidates = [backup_root]

        for source_dir in candidates:
            if not source_dir.exists():
                continue
            for item in source_dir.rglob("*"):
                if item.is_file() and not self._skip_file(item):
                    relative = item.relative_to(backup_root)
                    destination = target / relative
                    destination.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(item, destination)
                    restored += 1
        return restored

    def _skip_file(self, path: Path) -> bool:
        for pattern in PRESERVE_PATTERNS:
            if pattern.startswith("*") and path.match(pattern):
                return True
            if pattern in str(path):
                return True
        return False


class RestorePanel(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("IG Restore Panel")
        self.setMinimumSize(760, 640)
        self.worker_thread = None
        self.worker = None
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        self.setStyleSheet(f"background-color: {HOLO_BG}; color: {HOLO_TEXT};")

        title = QLabel("IG RESTORE PANEL")
        title.setFont(QFont("Consolas", 24, QFont.Bold))
        title.setStyleSheet(f"color: {HOLO_ACCENT};")
        layout.addWidget(title)

        subtitle = QLabel("Guardian-grade recovery from SSD and HD backups.")
        subtitle.setFont(QFont("Consolas", 10))
        subtitle.setStyleSheet(f"color: {HOLO_TEXT};")
        layout.addWidget(subtitle)

        source_layout = QHBoxLayout()
        source_label = QLabel("Backup Source:")
        source_label.setFont(QFont("Consolas", 10))
        source_label.setStyleSheet(f"color: {HOLO_TEXT};")
        source_layout.addWidget(source_label)

        self.source_combo = QComboBox()
        self.source_combo.addItem("SSD Backup (C:/IG/backups/ssd)", RestoreSource.SSD)
        self.source_combo.addItem("HD Backup (D:/IG/backups/hd)", RestoreSource.HD)
        self.source_combo.setStyleSheet(
            f"background-color: {HOLO_PANEL}; color: {HOLO_TEXT}; border: 1px solid {HOLO_ACCENT};"
        )
        source_layout.addWidget(self.source_combo)
        layout.addLayout(source_layout)

        button_layout = QHBoxLayout()
        self.full_restore_btn = QPushButton("Full Restore")
        self.full_restore_btn.clicked.connect(self._on_full_restore)
        self.full_restore_btn.setStyleSheet(self._button_style(HOLO_ACCENT))
        button_layout.addWidget(self.full_restore_btn)

        self.partial_restore_btn = QPushButton("Partial Restore")
        self.partial_restore_btn.clicked.connect(self._on_partial_restore)
        self.partial_restore_btn.setStyleSheet(self._button_style(HOLO_SUCCESS))
        button_layout.addWidget(self.partial_restore_btn)

        self.ssd_restore_btn = QPushButton("Restore from SSD")
        self.ssd_restore_btn.clicked.connect(self._on_restore_ssd)
        self.ssd_restore_btn.setStyleSheet(self._button_style(HOLO_SUCCESS))
        button_layout.addWidget(self.ssd_restore_btn)

        self.hd_restore_btn = QPushButton("Restore from HD")
        self.hd_restore_btn.clicked.connect(self._on_restore_hd)
        self.hd_restore_btn.setStyleSheet(self._button_style(HOLO_WARNING))
        button_layout.addWidget(self.hd_restore_btn)

        layout.addLayout(button_layout)

        self.progress = QProgressBar()
        self.progress.setRange(0, 100)
        self.progress.setValue(0)
        self.progress.setTextVisible(True)
        self.progress.setStyleSheet(
            f"QProgressBar {{background-color: {HOLO_PANEL}; color: {HOLO_TEXT}; border: 1px solid {HOLO_ACCENT};}}"
            f"QProgressBar::chunk {{background-color: {HOLO_ACCENT};}}"
        )
        layout.addWidget(self.progress)

        self.status_area = QTextEdit()
        self.status_area.setReadOnly(True)
        self.status_area.setStyleSheet(
            f"background-color: {HOLO_PANEL}; color: {HOLO_TEXT}; border: 1px solid {HOLO_ACCENT};"
        )
        self.status_area.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        layout.addWidget(self.status_area)

        self.cancel_btn = QPushButton("Cancel")
        self.cancel_btn.clicked.connect(self._cancel_restore)
        self.cancel_btn.setStyleSheet(self._button_style(HOLO_ERROR))
        self.cancel_btn.setEnabled(False)
        layout.addWidget(self.cancel_btn)

        self._append_status("Restore panel ready.")

    def _button_style(self, color: str) -> str:
        return (
            f"QPushButton {{ background-color: {color}; color: {HOLO_BG}; border: none; padding: 10px; }}"
            f"QPushButton:hover {{ background-color: #ffffff22; }}"
        )

    def _append_status(self, message: str):
        self.status_area.append(f"[{datetime.datetime.now().isoformat()}] {message}")

    def _selected_source(self) -> RestoreSource:
        return self.source_combo.currentData()

    def _on_full_restore(self):
        self._begin_restore(partial=False)

    def _on_partial_restore(self):
        self._begin_restore(partial=True)

    def _on_restore_ssd(self):
        self.source_combo.setCurrentIndex(0)
        self._begin_restore(partial=False)

    def _on_restore_hd(self):
        self.source_combo.setCurrentIndex(1)
        self._begin_restore(partial=False)

    def _begin_restore(self, partial: bool):
        source = self._selected_source()
        if source is None:
            QMessageBox.warning(self, "Restore Source", "Please select a backup source.")
            return

        source_label = "SSD" if source == RestoreSource.SSD else "HD"
        restore_type = "partial