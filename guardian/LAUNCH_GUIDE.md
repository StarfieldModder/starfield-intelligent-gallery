# IG Guardian AI — Launch Guide

## Overview

The **IG Guardian AI** is now ready for deployment. This guide walks you through launching and using the Guardian AI diagnostic console.

---

## ✓ Verification Complete

All systems verified and tested:

```
[TEST 1] Syntax Verification ..................... [OK]
[TEST 2] Import Verification ..................... [OK]
[TEST 3] Core Functionality ....................... [OK]
[TEST 4] Enums & Data Structures ................. [OK]

Result: Guardian AI is ready for deployment!
```

---

## Quick Start

### Method 1: Standalone Launch

Open PowerShell and run:

```powershell
cd C:\IG
python tools/GalleryApp/guardian/guardian_ai.py
```

**Expected result:**
- A new window opens titled "IG GUARDIAN AI — DIAGNOSTIC CONSOLE"
- Status indicator glows cyan (●) — THINKING
- Console log shows: "[THINKING] Guardian AI online. Baseline established."
- After ~30 seconds, indicator turns green (●) — HEALTHY
- First snapshot appears in log

### Method 2: From Python REPL

```python
>>> from tools.GalleryApp.guardian import GuardianAI
>>> from PySide6.QtWidgets import QApplication
>>> app = QApplication([])
>>> guardian = GuardianAI()
>>> guardian.show()
>>> app.exec()
```

---

## Understanding the UI

### Status Indicator (Guardian Glow)

| Color | Status | Meaning |
|-------|--------|---------|
| 🟢 Green | HEALTHY | All systems nominal |
| 🟡 Amber | WARNING | Minor issues detected |
| 🔴 Red | CRITICAL | Major issues requiring attention |
| 🔵 Cyan | THINKING | Scan in progress |
| ⚫ Gray | OFFLINE | Monitor disconnected |

### Main Tabs

1. **Status Tab**
   - Shows current health state
   - Displays status message
   - Updates automatically

2. **Anomalies Tab**
   - Table of detected issues
   - Type, Severity (1-10), Path
   - Description and Recommendation

3. **Predictions Tab**
   - Forecasted problems
   - Trend analysis results
   - Maintenance suggestions

4. **Artifact Protection Tab**
   - Protection strategy overview
   - "Validate All Artifacts" button
   - Protection status summary

### Diagnostic Console

Real-time log of Guardian AI activity:

```
[2026-07-27T12:15:22] [THINKING] Guardian AI online. Baseline established.
[2026-07-27T12:15:22] [SNAPSHOT] 5/5 modules OK, 2048MB free
[2026-07-27T12:16:22] [SNAPSHOT] 5/5 modules OK, 2045MB free
```

### Action Buttons

- **Full Scan** — Trigger immediate integrity scan
- **Auto-Fix Anomalies** — Attempt automatic fixes (with confirmation)
- **Export Diagnostics** — Save diagnostics to `C:\IG\logs\diagnostics_*.json`
- **Close** — Exit and stop monitoring

---

## What's Being Monitored

### Files (SHA256 verification):
- `main.py`
- `pyproject.toml`
- `pytest.ini`
- `tools/lint.py`
- `tools/run_tests.py`

### Core Modules (existence verification):
- `core/`
- `mission_controller/`
- `ui/`
- `config/`
- `data/`

### Backup Status:
- `C:\IG\backups\ssd` (SSD backup)
- `D:\IG\backups\hd` (HD backup)

### System Health:
- Disk space (C: and D: drives)
- Git repository status
- Historical trends

---

## Common Scenarios

### Scenario 1: Green Glow (HEALTHY)

**Status:** All systems nominal

**Action:** No action needed. Continue working.

**What to do:**
- Periodically check Predictions tab
- Export diagnostics weekly for audit trail
- Review backup freshness in Anomalies tab

---

### Scenario 2: Amber Glow (WARNING)

**Status:** Minor issues detected

**Common causes:**
- SSD backup older than 7 days
- Low disk space (>10 GB threshold)
- Slow git repository

**Actions:**
1. Check Anomalies tab for specific issues
2. Review recommendations
3. Click "Auto-Fix" if available (will ask for confirmation)
4. Or manually address the issue

**Example:**
```
[Anomaly] Backup is 10 days old
[Recommendation] Run backup scheduler to create fresh backup
```

---

### Scenario 3: Red Glow (CRITICAL)

**Status:** Major issues requiring immediate attention

**Critical causes:**
- File corruption (hash mismatch)
- Missing core module
- Git desynchronization

**Immediate actions:**
1. Check Anomalies tab for specific issue
2. Note the affected file/module
3. Click "Restore Panel" button in Recovery Dashboard
4. Select appropriate backup source (SSD or HD)
5. Click "Full Restore"
6. Wait for restore to complete
7. Guardian AI will re-establish baseline (turn green)

**Example:**
```
[Critical Anomaly] Hash mismatch detected: main.py
[Recommendation] Restore from backup or review with git diff
```

---

## Interpreting Anomalies

### File Corruption (Severity 8+)
```
Type: file_corruption
Description: Hash mismatch detected: main.py
Action: Restore from backup or git checkout
```

### Missing Module (Severity 9+)
```
Type: missing_module
Description: Core module missing: core/
Action: Restore from backup immediately (CRITICAL)
```

### Stale Backup (Severity 4+)
```
Type: backup_stale
Description: SSD Backup is 10 days old
Action: Run Backup Scheduler to refresh
```

### Low Disk Space (Severity 7+)
```
Type: disk_space_low
Description: C: has only 5.2 GB free
Action: Delete old files or expand storage
```

---

## Diagnostic Log Locations

Guardian AI writes to:

**Main diagnostics:**
```
C:\IG\logs\guardian_diagnostics.log
```

**Anomaly log:**
```
C:\IG\logs\anomaly_detection.log
```

**View in PowerShell:**
```powershell
# Last 50 lines
Get-Content C:\IG\logs\guardian_diagnostics.log -Tail 50

# Real-time tail
Get-Content -Path C:\IG\logs\guardian_diagnostics.log -Wait
```

---

## Integration Points

### Recovery Dashboard Integration

To add Guardian AI to Recovery Dashboard:

1. Open `recovery_dashboard.py`
2. Add import: `from tools.GalleryApp.guardian import GuardianAI`
3. Add button in `__init__()`:
   ```python
   guardian_btn = QPushButton("Guardian AI")
   guardian_btn.clicked.connect(self.open_guardian)
   layout.addWidget(guardian_btn)
   ```
4. Add method:
   ```python
   def open_guardian(self):
       self.guardian = GuardianAI(parent=self)
       self.guardian.show()
   ```

---

## Customization

### Change Scan Interval

Edit `guardian_ai.py`, line ~195:

```python
self.check_interval = 30  # Change to 60 for slower systems
```

### Add Critical Files to Monitor

Edit `guardian_ai.py`, lines ~44-47:

```python
CRITICAL_FILES = [
    "main.py",
    "pyproject.toml",
    "pytest.ini",
    "tools/lint.py",
    "tools/run_tests.py",
    # Add your files here:
    # "my_important_file.py",
]
```

### Adjust Thresholds

**Stale backup threshold** (default 7 days):
```python
if age_days > 7:  # Edit line ~115
```

**Low disk space threshold** (default 10 GB):
```python
if free_gb < 10:  # Edit line ~131
```

---

## Troubleshooting

### Guardian AI Won't Launch

**Error:** `ModuleNotFoundError: No module named 'PySide6'`

**Fix:**
```powershell
pip install PySide6
```

### Status Indicator Shows OFFLINE

**Cause:** Monitor crashed or disconnected

**Fix:** Restart Guardian AI

### High CPU Usage

**Cause:** Scan interval too short or too many files

**Fix:** Increase `check_interval` from 30 to 60+ seconds

### No Anomalies Detected

**Cause:** Baseline not established or all systems healthy

**Fix:** Wait 30 seconds for first scan, then check console log

### Export Fails

**Cause:** No write permission on logs directory

**Fix:** Check that `C:\IG\logs\` exists and is writable

---

## Best Practices

1. **Launch on startup:** Add Guardian AI to your daily startup routine
2. **Check weekly:** Review Predictions tab for maintenance
3. **Export monthly:** Save diagnostics for audit trail
4. **Keep updated:** Monitor for new anomaly types or enhancements
5. **Coordinate:** Let Guardian AI guide backup scheduling

---

## Advanced Usage

### Programmatic Anomaly Detection

```python
from tools.GalleryApp.guardian import AnomalyDetector

detector = AnomalyDetector()
detector.initialize_baseline()

anomalies = detector.detect_anomalies()
for anomaly in anomalies:
    print(f"{anomaly.severity}/10: {anomaly.description}")
```

### Custom Anomaly Handling

See `GUARDIAN_AI_EXAMPLE_INTEGRATION.py` for 8 integration patterns including:
- Background monitoring without GUI
- Restore Panel coordination
- Backup Scheduler coordination
- Custom response handlers

---

## Performance Tips

- **Fast SSDs:** Decrease `check_interval` to 15 seconds
- **Network drives:** Increase `check_interval` to 120+ seconds
- **Older systems:** Increase `check_interval` to 60+ seconds

---

## Next Steps

1. ✓ Launch Guardian AI
2. ✓ Verify status indicator goes green
3. ✓ Review "Status" tab
4. ✓ Check "Anomalies" tab
5. ✓ Review "Predictions" tab
6. [ ] Integrate with Recovery Dashboard (optional)
7. [ ] Export diagnostics for record-keeping
8. [ ] Set up weekly review routine

---

## Support & Documentation

- **Quick Reference:** `README_GUARDIAN_AI.md`
- **Technical Details:** `GUARDIAN_AI_INTEGRATION.md`
- **Master Index:** `INDEX_GUARDIAN_AI.md`
- **Examples:** `GUARDIAN_AI_EXAMPLE_INTEGRATION.py`
- **Deployment Info:** `DEPLOYMENT_SUMMARY.txt`

---

## That's It!

Guardian AI is now live and protecting your Intelligence Gallery.

**Status:** 🟢 HEALTHY

Happy monitoring! 👁️
