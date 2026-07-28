# IG Guardian AI — Integration & Architecture Guide

## Overview

The **IG Guardian AI** is the 24/7 sentinel of the Intelligence Gallery, providing:

- **Real-time integrity monitoring** of core modules and critical files
- **Anomaly detection** for file corruption, unauthorized changes, and missing components
- **Predictive failure analysis** based on trends and historical snapshots
- **Artifact protection** with SHA256 verification and unauthorized change alerts
- **Guardian Glow status indicators** (healthy/warning/critical/offline)
- **Diagnostic console** with full logging and forensics
- **Coordination** with Restore Panel and Backup Scheduler

## File Structure

```
C:\IG\tools\GalleryApp\guardian\
├── __init__.py                    # Package initializer
├── guardian_ai.py                 # Main module (976 lines)
└── GUARDIAN_AI_INTEGRATION.md      # This file
```

## Core Components

### 1. HealthStatus (Enum)
Represents the overall health state of the Intelligence Gallery:
- `HEALTHY` — All systems nominal
- `WARNING` — Minor issues detected (e.g., stale backup)
- `CRITICAL` — Major issues requiring immediate attention
- `THINKING` — Scan in progress
- `OFFLINE` — Monitor disconnected

### 2. AnomalyType (Enum)
Classifies detected anomalies:
- `FILE_CORRUPTION` — Hash mismatch on critical file
- `MISSING_MODULE` — Expected module directory not found
- `HASH_MISMATCH` — File has changed from baseline
- `BACKUP_STALE` — Backup older than 7 days
- `GIT_DESYNC` — Git state inconsistent
- `DISK_SPACE_LOW` — Less than 10 GB free on drive
- `UNAUTHORIZED_CHANGE` — File modified without snapshot commit

### 3. AnomalyReport (Dataclass)
Encapsulates a detected anomaly:
```python
@dataclass
class AnomalyReport:
    anomaly_type: AnomalyType
    severity: int          # 1-10
    timestamp: datetime.datetime
    affected_path: Optional[Path]
    description: str
    recommendation: str
    auto_fixable: bool = False
    errors: List[str] = field(default_factory=list)
```

### 4. IntegritySnapshot (Dataclass)
Point-in-time snapshot of system health:
```python
@dataclass
class IntegritySnapshot:
    timestamp: datetime.datetime
    file_hashes: Dict[str, str]
    module_status: Dict[str, bool]
    backup_status: Dict[str, bool]
    disk_space_mb: int
    git_commit: Optional[str]
```

### 5. AnomalyDetector
Scans for integrity violations:

**Key Methods:**
- `initialize_baseline()` — Store baseline SHA256 hashes of critical files
- `detect_anomalies()` — Return list of `AnomalyReport` objects
- `_check_backup_staleness()` — Warn if backups > 7 days old
- `_check_disk_space()` — Alert if < 10 GB free

**Critical Files Monitored:**
- `main.py`, `pyproject.toml`, `pytest.ini`
- `tools/lint.py`, `tools/run_tests.py`

**Core Modules Verified:**
- `core/`, `mission_controller/`, `ui/`, `config/`, `data/`

### 6. PredictiveAnalyzer
Analyzes trends to predict failures:

**Key Methods:**
- `record_snapshot(snapshot)` — Store system state for analysis
- `predict_failures()` — Return list of predicted failure scenarios

**Predictions Include:**
- Disk space depletion trends
- Increasing anomaly frequency
- Backup aging patterns

### 7. GuardianMonitor (QObject)
Background monitoring thread (runs in QThread):

**Signals:**
- `health_changed(HealthStatus, str)` — Status update
- `anomaly_detected(AnomalyReport)` — New anomaly found
- `snapshot_ready(IntegritySnapshot)` — Snapshot captured
- `prediction_ready(List[str])` — Predictions generated

**Main Loop:**
Runs every 30 seconds (configurable via `check_interval`):
1. Detect anomalies
2. Determine overall health status
3. Emit signals to UI
4. Create and record snapshot
5. Generate predictions

### 8. GuardianAI (QWidget)
Main diagnostic console with tabs:

**Tabs:**
1. **Status** — Current health indicator and message
2. **Anomalies** — Table of detected issues with recommendations
3. **Predictions** — Forecasted failures and trends
4. **Artifact Protection** — Validation and protection status

**Features:**
- Guardian Glow status indicator (colored circle)
- Real-time diagnostic log
- Action buttons: Full Scan, Auto-Fix, Export, Close
- Automatic background monitoring

## Integration with Recovery Ecosystem

### Restore Panel Coordination
When restoration occurs:
1. Pre-restore snapshot is created via `GitSnapshotManager`
2. Post-restore verification via `IntegrityChecker`
3. Guardian AI receives notification of restoration
4. Baseline hashes are re-initialized if full restore succeeded

### Backup Scheduler Coordination
Guardian AI detects stale backups and flags them:
1. Anomaly of type `BACKUP_STALE` generated if > 7 days old
2. Recommendation suggests triggering backup scheduler
3. Auto-fix option available for eligible issues

### Recovery Dashboard Integration
Guardian AI can be launched from Recovery Dashboard:
```python
from tools.GalleryApp.guardian import GuardianAI

guardian = GuardianAI(parent=recovery_dashboard)
guardian.show()
```

## Configuration & Paths

```python
IG_ROOT = Path("C:/IG")
LOG_DIR = IG_ROOT / "logs"
GUARDIAN_LOG = LOG_DIR / "guardian_diagnostics.log"
ANOMALY_LOG = LOG_DIR / "anomaly_detection.log"
BACKUP_SSD = Path("C:/IG/backups/ssd")
BACKUP_HD = Path("D:/IG/backups/hd")
```

**Guardian Glow Colors:**
- `GLOW_HEALTHY = "#00FF9C"` — Vivid green
- `GLOW_WARNING = "#FFB300"` — Amber
- `GLOW_CRITICAL = "#FF4B61"` — Red
- `GLOW_THINKING = "#00B4FF"` — Cyan
- `GLOW_OFFLINE = "#666666"` — Gray

## Usage Examples

### Standalone Execution
```bash
python C:\IG\tools\GalleryApp\guardian\guardian_ai.py
```

### Integration into Panels
```python
from tools.GalleryApp.guardian import GuardianAI

# In RecoveryDashboard or other panel:
def open_guardian(self):
    self.guardian = GuardianAI(parent=self)
    self.guardian.show()
```

### Programmatic Use
```python
from tools.GalleryApp.guardian import AnomalyDetector, HealthStatus

detector = AnomalyDetector()
detector.initialize_baseline()

anomalies = detector.detect_anomalies()
for anomaly in anomalies:
    print(f"{anomaly.anomaly_type}: {anomaly.description}")
    print(f"Recommendation: {anomaly.recommendation}")
```

## Threading Model

Guardian AI uses Qt's thread architecture:

```
Main Thread (UI)
    ↓
GuardianMonitor (runs in QThread)
    ├── health_changed → update status indicator
    ├── anomaly_detected → populate table
    ├── snapshot_ready → log data
    └── prediction_ready → display predictions
```

The monitor thread runs continuously in the background. The main thread remains responsive.

## Diagnostic Log Format

Logs are written to `C:\IG\logs\guardian_diagnostics.log`:

```
[THINKING] Guardian AI online. Baseline established.
[SNAPSHOT] 5/5 modules OK, 1024MB free
[WARNING] Backup is 10 days old
[PREDICTION] Disk space declining (~512MB in last checks). Consider cleanup or archival.
[ANOMALY [4/10]: SSD Backup is 10 days old]
[STATUS: WARNING] Status: WARNING
```

## Artifact Protection Strategy

### Phase 1: Baseline Establishment
When Guardian AI starts:
1. Scan all critical files and compute SHA256 hashes
2. Store in `AnomalyDetector.baseline_hashes` dictionary
3. Record module existence status

### Phase 2: Continuous Monitoring
Every 30 seconds:
1. Recompute hashes for critical files
2. Compare against baseline
3. Detect unauthorized changes (hash mismatch without git commit)
4. Flag as `UNAUTHORIZED_CHANGE` anomaly

### Phase 3: Auto-Recovery
If unauthorized changes detected:
1. Guardian AI recommends `git checkout` or restore from snapshot
2. User can trigger restore via Restore Panel
3. Baseline is re-initialized post-restore

### Phase 4: Long-term Validation
- All anomalies logged to `anomaly_detection.log`
- Historical trend analysis via `PredictiveAnalyzer`
- Drift detection (gradual unauthorized changes)

## Extending Guardian AI

### Adding Custom Anomaly Types
1. Extend `AnomalyType` enum in `guardian_ai.py`
2. Add detection logic to `AnomalyDetector.detect_anomalies()`
3. Emit `anomaly_detected` signal with `AnomalyReport`

### Adding Custom Predictions
1. Extend `PredictiveAnalyzer.predict_failures()` method
2. Add trend analysis logic
3. Emit `prediction_ready` signal with list of strings

### Custom UI Tabs
1. Extend `GuardianAI._build_ui()` method
2. Add new tab via `self.tabs.addTab(...)`
3. Connect signals to update the new tab

## Performance Considerations

- **Scan interval:** 30 seconds (configurable)
- **Hash computation:** Uses streaming (8KB chunks) to avoid memory spikes
- **Snapshot retention:** Last 50 snapshots (configurable deque maxlen)
- **Anomaly log:** Last 100 anomalies (configurable deque maxlen)

For systems with 100K+ files, consider:
1. Increasing scan interval to 60+ seconds
2. Reducing monitored files to critical paths only
3. Using separate fast-scan vs. full-scan modes

## Testing

### Unit Tests
```bash
pytest tests/test_guardian_anomaly.py
pytest tests/test_guardian_analyzer.py
pytest tests/test_guardian_ui.py
```

### Integration Tests
```bash
# Test with Recovery Dashboard
python tools/GalleryApp/panels/recovery_dashboard.py

# Trigger anomaly and verify detection
touch C:\IG\main.py  # Changes mtime, will trigger hash check
```

### Performance Tests
```bash
# Measure scan time
python -m cProfile -s cumtime tools/GalleryApp/guardian/guardian_ai.py
```

## Troubleshooting

### Guardian AI Shows "OFFLINE"
- Check that PySide6 is installed: `pip install PySide6`
- Verify C:\IG directory exists and is readable
- Check logs: `tail -f C:\IG\logs\guardian_diagnostics.log`

### High CPU Usage During Scans
- Increase `check_interval` in `GuardianMonitor.__init__()` from 30 to 60+ seconds
- Reduce number of files in `CRITICAL_FILES` list
- Use partial scan for non-critical files

### Anomalies Not Detected
- Verify `initialize_baseline()` was called: check log for "Baseline established"
- Ensure files in `CRITICAL_FILES` actually exist
- Check file permissions (Guardian AI must be able to read files)

### Export Diagnostics Fails
- Verify `C:\IG\logs\` directory exists and is writable
- Check disk space on C: drive
- Ensure no file lock conflicts

## Security Considerations

1. **Hash verification only** — Guardian AI doesn't encrypt or sign files, only verifies integrity
2. **Local monitoring only** — No network communication; all data stays on machine
3. **User permissions** — Must run as user who owns IG directory
4. **Log file access** — Diagnostics logs may contain sensitive paths; protect `C:\IG\logs\`

## Future Enhancements

- [ ] GPU-accelerated hashing for large files
- [ ] Distributed monitoring across multiple machines
- [ ] Guardian AI API for external tools
- [ ] Machine learning-based anomaly scoring
- [ ] Automated rollback on critical anomalies
- [ ] Integration with Windows Event Log
- [ ] Remote alerting via email/webhooks

---

**Last Updated:** July 2026  
**Maintained by:** Copilot AI  
**Repository:** StarfieldModder/starfield-intelligent-gallery
