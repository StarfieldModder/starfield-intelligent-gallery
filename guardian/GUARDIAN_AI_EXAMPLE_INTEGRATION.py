###############################################################################
#  IG GUARDIAN AI — EXAMPLE INTEGRATION PATTERNS
#  Module: GUARDIAN_AI_EXAMPLE_INTEGRATION.py
#
#  This file demonstrates 7 real-world integration patterns for Guardian AI.
#  Copy and adapt these patterns to your own IG modules.
#
###############################################################################

# =============================================================================
# PATTERN 1: Standalone Diagnostic Console
# =============================================================================
# Use this pattern when you want to launch Guardian AI as a standalone tool

def pattern_1_standalone():
    """Launch Guardian AI as a standalone diagnostic console."""
    from PySide6.QtWidgets import QApplication
    from tools.GalleryApp.guardian import GuardianAI

    app = QApplication([])
    guardian = GuardianAI()
    guardian.show()
    app.exec()


# =============================================================================
# PATTERN 2: Guardian AI from Recovery Dashboard
# =============================================================================
# Integrate Guardian AI button into Recovery Dashboard

def pattern_2_recovery_dashboard_integration():
    """Add Guardian AI button to Recovery Dashboard."""
    from PySide6.QtWidgets import QPushButton, QVBoxLayout
    from tools.GalleryApp.guardian import GuardianAI

    class RecoveryDashboardWithGuardian:
        def __init__(self):
            self.guardian = None
            # ... existing dashboard setup ...

            # Add Guardian AI button
            guardian_btn = QPushButton("Guardian AI — Diagnostic Console")
            guardian_btn.clicked.connect(self.open_guardian)
            # layout.addWidget(guardian_btn)  # Add to your layout

        def open_guardian(self):
            """Open the Guardian AI diagnostic console."""
            if self.guardian is None:
                self.guardian = GuardianAI(parent=self)
            self.guardian.show()


# =============================================================================
# PATTERN 3: Programmatic Anomaly Detection
# =============================================================================
# Use this when you want to detect anomalies in your own code

def pattern_3_programmatic_detection():
    """Detect anomalies programmatically without GUI."""
    from tools.GalleryApp.guardian import (
        AnomalyDetector, AnomalyType, HealthStatus
    )

    detector = AnomalyDetector()
    detector.initialize_baseline()

    anomalies = detector.detect_anomalies()

    # Process anomalies
    for anomaly in anomalies:
        print(f"Type: {anomaly.anomaly_type.value}")
        print(f"Severity: {anomaly.severity}/10")
        print(f"Description: {anomaly.description}")
        print(f"Recommendation: {anomaly.recommendation}")
        print()

    # Determine overall status
    if anomalies:
        max_severity = max(a.severity for a in anomalies)
        if max_severity >= 8:
            status = HealthStatus.CRITICAL
        elif max_severity >= 5:
            status = HealthStatus.WARNING
        else:
            status = HealthStatus.HEALTHY
    else:
        status = HealthStatus.HEALTHY

    print(f"Overall Status: {status.value}")


# =============================================================================
# PATTERN 4: Continuous Monitoring without GUI
# =============================================================================
# Use this when you want background monitoring but don't need the GUI

def pattern_4_background_monitoring():
    """Monitor IG health in background without GUI."""
    import time
    from tools.GalleryApp.guardian import (
        AnomalyDetector, PredictiveAnalyzer, IntegritySnapshot
    )
    from pathlib import Path
    import hashlib

    detector = AnomalyDetector()
    analyzer = PredictiveAnalyzer()
    detector.initialize_baseline()

    # Monitoring loop
    for iteration in range(10):  # Run 10 times
        print(f"\n=== Scan #{iteration + 1} ===")

        # Detect anomalies
        anomalies = detector.detect_anomalies()
        print(f"Anomalies found: {len(anomalies)}")
        for anomaly in anomalies:
            print(f"  - {anomaly.anomaly_type.value}: {anomaly.description}")

        # Create snapshot
        snapshot = IntegritySnapshot(
            timestamp=__import__('datetime').datetime.now(),
            file_hashes=detector.baseline_hashes.copy(),
            module_status={},  # Simplified
            backup_status={},  # Simplified
            disk_space_mb=1024,  # Simplified
            git_commit=None
        )
        analyzer.record_snapshot(snapshot)

        # Predict failures
        predictions = analyzer.predict_failures()
        if predictions:
            print("Predictions:")
            for pred in predictions:
                print(f"  - {pred}")

        time.sleep(5)  # Wait 5 seconds before next scan


# =============================================================================
# PATTERN 5: Guardian AI + Restore Panel Coordination
# =============================================================================
# Use this when restore completes to re-establish Guardian baseline

def pattern_5_restore_coordination():
    """Coordinate between Restore Panel and Guardian AI."""
    from tools.GalleryApp.guardian import AnomalyDetector
    from tools.GalleryApp.panels import RestorePanel
    from PySide6.QtCore import Signal

    class RestorePanelWithGuardian(RestorePanel):
        restore_completed = Signal(bool)  # True if successful

        def on_restore_finished(self, report):
            """After restore completes, re-establish Guardian baseline."""
            from tools.GalleryApp.guardian import AnomalyDetector

            if report.status.value == "complete":
                # Restore succeeded; re-establish baseline
                detector = AnomalyDetector()
                detector.initialize_baseline()
                print("[Guardian AI] Baseline re-established after restore")
                self.restore_completed.emit(True)
            else:
                print("[Guardian AI] Restore failed; baseline unchanged")
                self.restore_completed.emit(False)


# =============================================================================
# PATTERN 6: Guardian AI + Backup Scheduler Coordination
# =============================================================================
# Use this when backup scheduler detects stale backups

def pattern_6_backup_coordination():
    """Coordinate between Backup Scheduler and Guardian AI."""
    from tools.GalleryApp.guardian import AnomalyDetector, AnomalyType
    import datetime

    class BackupSchedulerWithGuardian:
        def check_stale_backups(self):
            """Check if Guardian AI recommends backup refresh."""
            detector = AnomalyDetector()
            detector.initialize_baseline()

            anomalies = detector.detect_anomalies()

            for anomaly in anomalies:
                if anomaly.anomaly_type == AnomalyType.BACKUP_STALE:
                    print(f"[Backup Scheduler] Guardian recommends backup refresh")
                    print(f"  Reason: {anomaly.description}")
                    print(f"  Recommendation: {anomaly.recommendation}")

                    # Trigger backup
                    self.trigger_backup()
                    return True

            return False

        def trigger_backup(self):
            """Trigger backup operation."""
            print("[Backup Scheduler] Creating fresh backup...")
            # ... backup logic ...
            print("[Backup Scheduler] Backup complete")


# =============================================================================
# PATTERN 7: Guardian AI Health Dashboard
# =============================================================================
# Use this to build a health status widget for other panels

def pattern_7_health_widget():
    """Create a mini health status widget for embedding in other panels."""
    from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel
    from PySide6.QtGui import QFont
    from PySide6.QtCore import Qt
    from tools.GalleryApp.guardian import GuardianMonitor, HealthStatus

    class HealthStatusWidget(QWidget):
        def __init__(self, parent=None):
            super().__init__(parent)
            self.monitor = GuardianMonitor()
            self.monitor_thread = None
            self._build_ui()
            self._start_monitoring()

        def _build_ui(self):
            layout = QVBoxLayout(self)

            self.status_label = QLabel("●")
            self.status_label.setFont(QFont("Consolas", 16))
            layout.addWidget(self.status_label)

            self.message_label = QLabel("Initializing...")
            self.message_label.setFont(QFont("Consolas", 10))
            layout.addWidget(self.message_label)

        def _start_monitoring(self):
            from PySide6.QtCore import QThread
            self.monitor_thread = QThread()
            self.monitor.moveToThread(self.monitor_thread)
            self.monitor_thread.started.connect(self.monitor.run)
            self.monitor.health_changed.connect(self._on_health_changed)
            self.monitor_thread.start()

        def _on_health_changed(self, status: HealthStatus, message: str):
            color_map = {
                HealthStatus.HEALTHY: "#00FF9C",
                HealthStatus.WARNING: "#FFB300",
                HealthStatus.CRITICAL: "#FF4B61",
                HealthStatus.THINKING: "#00B4FF",
                HealthStatus.OFFLINE: "#666666",
            }
            self.status_label.setStyleSheet(f"color: {color_map[status]};")
            self.message_label.setText(message)

        def closeEvent(self, event):
            self.monitor.stop()
            self.monitor_thread.quit()
            self.monitor_thread.wait()
            event.accept()

    # Usage: embed in your dashboard
    # health_widget = HealthStatusWidget(parent=self)
    # layout.addWidget(health_widget)


# =============================================================================
# PATTERN 8: Custom Anomaly Response Handler
# =============================================================================
# Use this to handle specific anomaly types with custom logic

def pattern_8_custom_anomaly_handler():
    """Handle specific anomaly types with custom logic."""
    from tools.GalleryApp.guardian import (
        AnomalyDetector, AnomalyType, AnomalyReport
    )

    class CustomAnomalyHandler:
        def handle_anomalies(self, anomalies: list):
            """Process anomalies with custom logic for each type."""

            for anomaly in anomalies:
                if anomaly.anomaly_type == AnomalyType.FILE_CORRUPTION:
                    self._handle_corruption(anomaly)

                elif anomaly.anomaly_type == AnomalyType.MISSING_MODULE:
                    self._handle_missing_module(anomaly)

                elif anomaly.anomaly_type == AnomalyType.BACKUP_STALE:
                    self._handle_stale_backup(anomaly)

                elif anomaly.anomaly_type == AnomalyType.DISK_SPACE_LOW:
                    self._handle_low_disk_space(anomaly)

        def _handle_corruption(self, anomaly: AnomalyReport):
            """Handle file corruption: trigger restore."""
            print(f"[Handler] File corruption detected: {anomaly.affected_path}")
            print(f"[Handler] Triggering restore from backup...")
            # Launch restore panel or trigger programmatic restore

        def _handle_missing_module(self, anomaly: AnomalyReport):
            """Handle missing module: urgent alert."""
            print(f"[Handler] CRITICAL: Module missing: {anomaly.affected_path}")
            print(f"[Handler] Sending alert to administrator...")
            # Send alert via email, webhook, or system notification

        def _handle_stale_backup(self, anomaly: AnomalyReport):
            """Handle stale backup: schedule refresh."""
            print(f"[Handler] Backup is stale: {anomaly.description}")
            print(f"[Handler] Scheduling backup refresh...")
            # Queue backup job in scheduler

        def _handle_low_disk_space(self, anomaly: AnomalyReport):
            """Handle low disk space: cleanup or alert."""
            print(f"[Handler] Low disk space: {anomaly.description}")
            print(f"[Handler] Recommending cleanup...")
            # Suggest files to delete or alert user


# =============================================================================
# UTILITY: Run All Patterns
# =============================================================================

if __name__ == "__main__":
    import sys

    print("IG Guardian AI — Example Integration Patterns")
    print("=" * 50)
    print("\nAvailable patterns:")
    print("1. Standalone Diagnostic Console")
    print("2. Guardian AI from Recovery Dashboard")
    print("3. Programmatic Anomaly Detection")
    print("4. Continuous Monitoring without GUI")
    print("5. Guardian AI + Restore Panel Coordination")
    print("6. Guardian AI + Backup Scheduler Coordination")
    print("7. Guardian AI Health Dashboard Widget")
    print("8. Custom Anomaly Response Handler")

    print("\nTo run a pattern, edit this file and call:")
    print("  pattern_1_standalone()")
    print("  pattern_3_programmatic_detection()")
    print("  pattern_4_background_monitoring()")
    print("\nExample: Run pattern 3")

    # Uncomment to run pattern 3
    try:
        pattern_3_programmatic_detection()
    except Exception as exc:
        print(f"Error: {exc}")
        print("Make sure you're in the C:\\IG directory with PYTHONPATH set.")
