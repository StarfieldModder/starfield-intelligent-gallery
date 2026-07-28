# IG Guardian AI — Quick Reference

## Launch Guardian AI

### Standalone
```bash
python C:\IG\tools\GalleryApp\guardian\guardian_ai.py
```

### From Recovery Dashboard
```python
from tools.GalleryApp.panels import RecoveryDashboard
dashboard = RecoveryDashboard()
# Click "Guardian AI" button in dashboard (when integrated)
```

---

## Status Indicator Guide

| Color  | Status | Meaning |
|--------|--------|---------|
| 🟢 Green | HEALTHY | All systems nominal |
| 🟡 Amber | WARNING | Minor issues (stale backup, low disk) |
| 🔴 Red | CRITICAL | Major issues (missing modules, corruption) |
| 🔵 Cyan | THINKING | Scan in progress |
| ⚫ Gray | OFFLINE | Monitor disconnected |

---

## Anomaly Types & Responses

| Anomaly | Severity | Action |
|---------|----------|--------|
| File Corruption (Hash Mismatch) | 8+ | Restore from backup |
| Missing Core Module | 9 | Restore immediately |
| Unauthorized Change | 6 | Review with git diff or restore |
| Stale Backup (>7 days) | 4 | Run Backup Scheduler |
| Low Disk Space (<10GB) | 7 | Delete old files or add storage |

---

## Common Scenarios

### Scenario 1: Hash Mismatch Detected
1. Guardian AI shows **CRITICAL** (red glow)
2. Anomalies tab shows: "Hash mismatch detected: main.py"
3. Recommendations:
   - Run `git diff main.py` to review changes
   - Use Restore Panel to restore from backup
   - Or `git checkout main.py` to revert

### Scenario 2: Backup is Stale
1. Guardian AI shows **WARNING** (amber glow)
2. Anomalies tab shows: "SSD Backup is 10 days old"
3. Recommendations:
   - Run Backup Scheduler to create fresh backup
   - Or trigger via: `python tools/GalleryApp/panels/backup_scheduler.py`

### Scenario 3: Missing Module
1. Guardian AI shows **CRITICAL** (red glow)
2. Anomalies tab shows: "Core module missing: core/"
3. Immediate Action:
   - Click "Restore Panel" button in Recovery Dashboard
   - Select appropriate backup source (SSD or HD)
   - Click "Full Restore"

### Scenario 4: Low Disk Space
1. Guardian AI shows **WARNING** (amber glow)
2. Anomalies tab shows: "C: has only 5.2 GB free"
3. Recommendations:
   - Delete old backup files from `C:\IG\backups\ssd\`
   - Move archives to external storage
   - Or expand C: drive capacity

---

## Tabs Explained

### Status Tab
Shows overall health state and current message:
- "All systems nominal"
- "3 anomalies detected"
- "Scan in progress"

**Use when:** You want quick health overview

### Anomalies Tab
Table of detected issues with full details:
- Type: FILE_CORRUPTION, MISSING_MODULE, etc.
- Severity: 1-10 (higher = more urgent)
- Path: Which file/directory affected
- Description: What went wrong
- Recommendation: How to fix

**Use when:** Investigating specific issues

### Predictions Tab
Forecasted problems based on trends:
- "Disk space declining (~512MB in last 10 scans). Consider cleanup."
- "Anomaly frequency increasing. Review diagnostics."
- "Backup aging pattern detected. Schedule refresh soon."

**Use when:** Planning maintenance

### Artifact Protection Tab
Overview of IG artifact protection:
- Core modules: Protected with SHA256 verification
- Config files: Monitored for unauthorized changes
- Database files: Snapshots available
- Git commits: Tracked and recoverable
- Backup integrity: Continuous verification

**Use when:** Understanding protection strategy

---

## Diagnostic Console

Real-time log of Guardian AI activity:

```
[2026-07-27T12:15:22] [THINKING] Guardian AI online. Baseline established.
[2026-07-27T12:15:22] [SNAPSHOT] 5/5 modules OK, 2048MB free
[2026-07-27T12:15:25] [WARNING] Backup is 10 days old
[2026-07-27T12:15:30] [ANOMALY [4/10]] SSD Backup is 10 days old
[2026-07-27T12:16:22] [SNAPSHOT] 5/5 modules OK, 2045MB free
[2026-07-27T12:17:22] [SNAPSHOT] 5/5 modules OK, 2040MB free
[2026-07-27T12:17:25] [PREDICTION] Disk space declining (~8MB in last checks). Consider cleanup or archival.
```

**Key prefixes:**
- `[THINKING]` — Scan starting
- `[SNAPSHOT]` — Data point recorded
- `[ANOMALY]` — Issue detected
- `[PREDICTION]` — Trend forecast
- `[ERROR]` — Monitor error

---

## Action Buttons

### Full Scan
Trigger immediate full integrity scan (normally happens automatically every 30s):
- Checks all critical files
- Verifies all core modules exist
- Reports all anomalies immediately
- Use when: You suspect issues or want immediate verification

### Auto-Fix Anomalies
Attempt automatic fixes for eligible issues:
- Can refresh stale backups (if Backup Scheduler available)
- **Cannot** fix corruption or missing modules
- Shows confirmation dialog before proceeding
- Use when: You want automated remediation of safe issues

### Export Diagnostics
Save full diagnostic report to file:
- Saved to: `C:\IG\logs\diagnostics_YYYYMMDD_HHMMSS.json`
- Contains: Timestamp, status, anomaly count
- Use when: Sharing diagnostics with support or archiving

### Close
Exit Guardian AI and stop background monitoring

---

## Integration with Other Panels

### Recovery Dashboard
Guardian AI coordinates with:
- **Restore Panel** — Receives restore notifications, re-initializes baseline
- **Backup Scheduler** — Detects stale backups, recommends refreshes
- **Integrity Timeline** — Provides historical data for visualization

### Data Flow
```
Guardian AI (Monitor)
    ↓ (anomaly_detected signal)
    ├→ Restore Panel (updates protection status)
    ├→ Backup Scheduler (detects stale backups)
    └→ Integrity Timeline (historical data)
```

---

## Configuration

### Edit Scan Interval
In `guardian_ai.py`, line ~195:
```python
self.check_interval = 30  # seconds
```
Change to 60 for slower systems, 15 for faster checks.

### Add Critical Files
In `guardian_ai.py`, lines ~44-47:
```python
CRITICAL_FILES = [
    "main.py", "pyproject.toml", "pytest.ini",
    "tools/lint.py", "tools/run_tests.py",
    "tools/GalleryApp/guardian/guardian_ai.py",  # Add new file here
]
```

### Adjust Stale Backup Threshold
In `guardian_ai.py`, line ~115:
```python
if age_days > 7:  # Change 7 to your preferred threshold
```

### Modify Low Disk Space Alert
In `guardian_ai.py`, line ~131:
```python
if free_gb < 10:  # Change 10 to your preferred threshold
```

---

## Log Files

Guardian AI writes to:

**Main diagnostics log:**
`C:\IG\logs\guardian_diagnostics.log`

**Anomaly-specific log:**
`C:\IG\logs\anomaly_detection.log`

**View logs:**
```bash
# PowerShell
Get-Content C:\IG\logs\guardian_diagnostics.log -Tail 50

# Or tail with real-time updates
Get-Content -Path C:\IG\logs\guardian_diagnostics.log -Wait
```

---

## Troubleshooting

| Issue | Cause | Solution |
|-------|-------|----------|
| Guardian shows OFFLINE | Monitor crashed | Restart Guardian AI |
| Anomalies not detecting | Baseline not set | Guardian AI initializes on startup |
| High CPU usage | Scan interval too short | Increase check_interval to 60+ |
| Export fails | No write permission | Check C:\IG\logs\ is writable |
| False positives | File touched externally | Ignore if git shows no changes |

---

## Performance Tips

- **For 100K+ files:** Increase `check_interval` to 60 seconds
- **For SSDs:** Decrease `check_interval` to 15 seconds
- **For network drives:** Increase `check_interval` to 120+ seconds
- **For laptop:** Disable Guardian AI when on battery to save power

---

## What Guardian AI Monitors

✔ **Monitored:**
- main.py, pyproject.toml, pytest.ini
- tools/lint.py, tools/run_tests.py
- core/, mission_controller/, ui/, config/, data/ (existence)
- Backup freshness (SSD and HD)
- Disk space (C: and D: drives)
- Git commit status

✗ **Not Monitored:**
- Individual image files
- Cache directories (__pycache__)
- Virtual environments (.venv)
- Session state files

---

## Integration Checklist

- [ ] Guardian AI module compiles: `python -m py_compile guardian_ai.py`
- [ ] Import works: `from tools.GalleryApp.guardian import GuardianAI`
- [ ] Recovery Dashboard has "Guardian AI" button
- [ ] Guardian AI launches without errors
- [ ] Status indicator shows green (HEALTHY)
- [ ] Anomalies tab is empty or shows expected issues
- [ ] Diagnostic log is being written

---

**Last Updated:** July 2026  
**Version:** 1.0  
**Repository:** StarfieldModder/starfield-intelligent-gallery
