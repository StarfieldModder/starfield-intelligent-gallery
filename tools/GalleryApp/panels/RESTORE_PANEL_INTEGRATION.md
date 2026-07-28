# IG Restore Panel — Integration Guide

**Module:** `restore_panel.py`  
**Location:** `C:\IG\tools\GalleryApp\panels\`  
**Author:** Mark J. Latsha (Games) + Microsoft Copilot  
**Date:** July 26, 2026  
**Status:** Ready for Integration

---

## Overview

The **IG Restore Panel** is a holographic UI module that enables one-click recovery of the Intelligence Gallery from either the SSD backup (`C:\IG`) or HD backup (`D:\IG`). It integrates deeply with the Recovery Dashboard, Guardian AI companion system, and Git version control.

### Key Features

✓ **Dual-Source Restoration** — Restore from C:\IG (SSD) or D:\IG (HD)  
✓ **Pre-Restore Snapshot Commits** — Git snapshots enable atomic rollback  
✓ **Integrity Verification** — Hash-based verification before/after restore  
✓ **Holographic UI** — Starfield-inspired interface with progress tracking  
✓ **Guardian AI Integration** — Voice notifications on completion  
✓ **Async Workers** — Non-blocking restore operations with threading  
✓ **Comprehensive Logging** — Detailed audit trail for all operations  
✓ **Error Recovery** — Rollback capability with commit tracking  

---

## Architecture

### Class Hierarchy

```
RestorePanel (QWidget)
├── RestoreWorker (QObject) — async restore orchestration
├── IntegrityChecker — hash verification and manifest management
├── GitSnapshotManager — pre-restore snapshot creation
└── GuardianAINotifier — companion system integration
```

### Data Flow

```
1. User selects backup source (SSD or HD)
2. RestorePanel → Create RestoreWorker thread
3. RestoreWorker._run_pre_checks() → verify source exists
4. RestoreWorker._create_snapshot() → Git commit for rollback
5. RestoreWorker._verify_backup() → IntegrityChecker.verify()
6. RestoreWorker._restore_files() → copy from source to IG_ROOT
7. RestoreWorker._verify_integrity() → post-restore hash check
8. RestoreWorker._notify_guardian() → GuardianAINotifier.notify()
9. RestorePanel.on_complete() → display RestoreReport
```

---

## Integration Points

### 1. Recovery Dashboard Integration

The **Recovery Dashboard** (`recovery_dashboard.py`) should expose a button to launch the Restore Panel:

```python
# In RecoveryDashboard.__init__():
from tools.GalleryApp.panels.restore_panel import RestorePanel

restore_btn = QPushButton("Launch Restore Panel")
restore_btn.clicked.connect(self.open_restore_panel)

# Method:
def open_restore_panel(self):
    self.restore_panel = RestorePanel(self)
    self.restore_panel.show()
```

### 2. Guardian AI Integration

The panel notifies Guardian AI via the companion log. Voice alerts are triggered if companion mode is active:

```python
# GuardianAINotifier writes to:
# C:\IG\logs\companion_notifications.log

# Companion reader should poll this log for new entries and voice them.
```

### 3. Git Workflow

Pre-restore snapshots enable safe rollback:

```bash
# Before restore, a commit is created:
git -C C:\IG commit -m "Pre-restore snapshot" --allow-empty

# If restore fails, user can rollback to the snapshot commit hash.
```

### 4. Holographic UI

The panel uses Starfield-inspired color palette:

```python
HOLO_BG       = "#0A0E1A"      # Deep space background
HOLO_ACCENT   = "#00B4FF"      # Cyan accent
HOLO_SUCCESS  = "#00FF9C"      # Green for success
HOLO_ERROR    = "#FF4444"      # Red for errors
HOLO_WARNING  = "#FFB300"      # Amber for warnings
```

---

## Usage

### Standalone Execution

```bash
cd C:\IG\tools\GalleryApp\panels
python restore_panel.py
```

### Integration with Main App

```python
from tools.GalleryApp.panels.restore_panel import RestorePanel
from PySide6.QtWidgets import QApplication

app = QApplication([])
panel = RestorePanel()
panel.show()
app.exec()
```

### Recovery Dashboard Integration

```python
def open_restore_panel(self):
    self.restore_panel = RestorePanel(self)
    self.restore_panel.show()
```

---

## Core Classes

### RestorePanel

**Holographic UI widget for restore operations.**

**Methods:**
- `setup_ui()` — Build the Starfield-themed interface
- `start_restore()` — Launch async restore worker
- `verify_backup()` — Pre-flight integrity checks
- `cancel_restore()` — Abort ongoing operation
- `on_progress(value)` — Update progress bar
- `on_status(message)` — Update status label
- `on_error(error)` — Handle and display errors
- `on_complete(report)` — Display final report

**Signals (PyQt):**
- `progress_updated(int)` — Progress (0–100)
- `status_changed(str)` — Status message
- `error_occurred(str)` — Error message
- `complete(RestoreReport)` — Final report

---

### RestoreWorker

**Async worker thread for restore orchestration.**

**Workflow:**
1. Pre-checks (source validation)
2. Create snapshot (Git commit)
3. Verify backup (integrity check)
4. Restore files (copy directory tree)
5. Verify integrity (post-restore hash check)
6. Notify Guardian (companion system)

**Methods:**
- `run()` — Execute full restore workflow
- `_run_pre_checks()` — Validate source
- `_create_snapshot()` — Git snapshot commit
- `_verify_backup()` — IntegrityChecker.verify()
- `_restore_files()` — Copy files from backup
- `_verify_integrity()` — Post-restore verification
- `_notify_guardian()` — Send Guardian notification

---

### IntegrityChecker

**Hash-based file integrity verification.**

**Methods:**
- `compute_hash(file_path, algorithm)` — SHA256 hash for a file
- `scan_directory(target)` — Hash all Python files and configs
- `save_manifest()` → Save hashes to `.integrity_manifest.json`
- `load_manifest()` → Load saved manifest
- `verify(source)` → Verify all files at source location
  - Returns: `(passed: bool, errors: List[str], files_checked: int)`

**Manifest Format:**
```json
{
  "timestamp": "2026-07-26T06:01:27.123456",
  "hashes": {
    "core/module.py": "a3c7f2e...",
    "config/settings.json": "b5d8g4h...",
    ...
  }
}
```

---

### GitSnapshotManager

**Creates pre-restore snapshot commits for rollback.**

**Methods:**
- `create_snapshot(reason: str)` → Create commit, return hash
- `get_latest_commit()` → Get HEAD commit hash

**Snapshot Naming Convention:**
```
"Pre-restore snapshot [SSD|HD] [timestamp]"
```

---

### GuardianAINotifier

**Sends notifications to Guardian AI companion system.**

**Methods:**
- `notify(report: RestoreReport)` → Write to companion log
  - Returns: `bool` (success/failure)
- `_generate_message(report: RestoreReport)` → Voice-friendly text

**Output Location:**
```
C:\IG\logs\companion_notifications.log
```

**Log Format:**
```
[2026-07-26T06:01:27.123456] RESTORE: Restore from SSD backup complete. Restored 1234 files. Integrity verified.
```

---

### RestoreReport

**Complete audit trail of a restore operation.**

**Attributes:**
```python
@dataclass
class RestoreReport:
    status: RestoreStatus              # Final status (COMPLETE, FAILED, etc.)
    source: RestoreSource              # SSD or HD
    timestamp: datetime.datetime        # Operation start time
    files_restored: int                # Number of files copied
    files_checked: int                 # Number of files verified
    integrity_passed: bool             # Integrity check result
    snapshot_commit: Optional[str]      # Git commit hash for rollback
    guardian_notified: bool            # Notification sent to Guardian
    errors: List[str]                  # Error messages
    warnings: List[str]                # Warning messages
    rollback_executed: bool            # Whether rollback was needed
    rollback_point: Optional[str]      # Commit hash for rollback
```

---

## Configuration

### Backup Paths

```python
IG_ROOT      = Path("C:/IG")      # Main IG working directory
BACKUP_SSD   = Path("C:/IG")      # Primary SSD backup (same as root)
BACKUP_HD    = Path("D:/IG")      # Secondary HD backup
```

### Core Modules (Required for Restore)

```python
CORE_MODULES = [
    "core",
    "mission_controller",
    "ui",
    "config",
    "data",
]
```

### Files to Preserve (Not Overwritten)

```python
PRESERVE_PATTERNS = [
    ".venv",                    # Python virtual env
    "__pycache__",              # Compiled Python
    ".pytest_cache",            # Test cache
    "*.log",                    # Log files
    "session-state",            # Current session state
]
```

---

## Error Handling

### Pre-Restore Checks

- ✓ Source path exists
- ✓ Git repository is initialized
- ✓ All core modules present

### Restore Process

- ✓ File copy errors logged as warnings (restore continues)
- ✓ Integrity failures block restoration
- ✓ Guardian notification failures logged but don't block

### Rollback

- ✓ Pre-restore snapshot commit saved
- ✓ User can manually rollback via `git reset --hard <commit>`

---

## Dependencies

### Required

- **Python:** ≥3.10
- **PySide6:** for holographic UI (import fallback to CLI if missing)

### Optional

- **Companion AI:** for voice notifications

### Installation

```bash
pip install PySide6
```

---

## Testing

### Unit Tests

```python
# Test IntegrityChecker
def test_compute_hash():
    checker = IntegrityChecker()
    hash1 = checker.compute_hash(Path("test.py"))
    hash2 = checker.compute_hash(Path("test.py"))
    assert hash1 == hash2  # Deterministic

# Test RestoreWorker (mock threading)
def test_restore_worker_pre_checks():
    worker = RestoreWorker(RestoreSource.SSD)
    worker._run_pre_checks()  # Should not raise
```

### Integration Tests

```bash
# Full restore workflow from SSD
python -m pytest tests/test_restore_panel.py::test_full_restore_ssd

# Verify backup integrity
python -m pytest tests/test_restore_panel.py::test_verify_backup
```

---

## Troubleshooting

### "Source not found: C:/IG"

- Verify SSD is connected
- Check drive letter assignment
- Update `BACKUP_SSD` path if needed

### "Source not found: D:/IG"

- Verify HD backup is connected
- Check drive letter assignment
- Update `BACKUP_HD` path if needed

### "Backup verification failed"

- Integrity checker detected missing core modules
- Restore may not proceed safely
- Check backup for corruption

### "Guardian AI notification failed"

- Companion mode logs still created, notification just didn't voice
- Check `C:\IG\logs\companion_notifications.log` for details

### "Restore stuck in progress"

- Use Cancel button to abort
- Check Windows Task Manager for python process
- Restore will rollback to pre-restore snapshot

---

## Future Enhancements

1. **Incremental Restore** — Only restore changed files
2. **Differential Backup** — Track file changes over time
3. **Cloud Backup Support** — Restore from cloud storage
4. **Scheduled Backups** — Automatic backup scheduler
5. **Encryption** — Encrypted backup archives
6. **Multi-Archive Support** — Archive rotation management

---

## References

- **Recovery Dashboard:** `tools/GalleryApp/panels/recovery_dashboard.py`
- **Guardian AI:** Companion voice system integration
- **Git Integration:** Pre-restore snapshot commits
- **Holographic UI:** Starfield color palette and effects
- **Integrity Manifest:** `.integrity_manifest.json`

---

## Support

For issues or questions:
1. Check the troubleshooting section above
2. Review the error logs in `C:\IG\logs\`
3. Check Git history: `git log --oneline | head -20`
4. Consult the Recovery Dashboard integrity scan

---

**Module Status:** ✅ Complete and Ready for Integration  
**Last Updated:** July 26, 2026, 06:01 AM PDT  
**Maintainer:** Mark J. Latsha + Copilot AI
