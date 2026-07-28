###############################################################################
#   I N T E L L I G E N C E   G A L L E R Y                                   #
#   E X A M P L E: R E S T O R E   P A N E L   I N T E G R A T I O N        #
#   -----------------------------------------------------------------------   #
#   File: RESTORE_PANEL_EXAMPLE_INTEGRATION.py                               #
#   Location: C:\IG\tools\GalleryApp\panels\                                  #
#                                                                             #
#   Description:                                                              #
#       Example showing how to integrate RestorePanel with RecoveryDashboard  #
#       and other IG subsystems.                                              #
#                                                                             #
#       This file demonstrates:                                               #
#           1. Importing and instantiating RestorePanel                       #
#           2. Adding RestorePanel to RecoveryDashboard                       #
#           3. Handling RestoreReport after completion                        #
#           4. Coordinating with Guardian AI                                  #
#                                                                             #
###############################################################################

"""
EXAMPLE 1: Standalone Restore Panel
====================================
Run the Restore Panel as a standalone application.
"""

def example_standalone():
    from PySide6.QtWidgets import QApplication
    from restore_panel import RestorePanel

    app = QApplication([])
    panel = RestorePanel()
    panel.show()
    app.exec()


"""
EXAMPLE 2: Add Restore Button to Recovery Dashboard
====================================================
Modify RecoveryDashboard to launch the Restore Panel.
"""

def example_recovery_dashboard_integration():
    """
    This would go in recovery_dashboard.py:
    """

    # Import in RecoveryDashboard class
    from restore_panel import RestorePanel

    # Add this to RecoveryDashboard.__init__():
    code_snippet = """
    restore_btn = QPushButton("🔄 RESTORE GALLERY")
    restore_btn.clicked.connect(self.open_restore_panel)
    layout.addWidget(restore_btn)
    
    # Add this method to RecoveryDashboard:
    def open_restore_panel(self):
        self.restore_panel = RestorePanel(self)
        self.restore_panel.show()
        self.output.append("Restore Panel opened")
    """
    print(code_snippet)


"""
EXAMPLE 3: Custom Report Handler
=================================
Process RestoreReport after restore completion.
"""

def example_handle_restore_report():
    from restore_panel import RestoreReport, RestoreStatus, RestoreSource
    import json
    from pathlib import Path

    def handle_restore_completion(report: RestoreReport):
        """
        Handle the completion report from a restore operation.
        """

        # Log the report to a file
        report_file = Path("C:/IG/logs/restore_reports.jsonl")
        report_file.parent.mkdir(parents=True, exist_ok=True)

        report_dict = {
            "timestamp": report.timestamp.isoformat(),
            "status": report.status.value,
            "source": report.source.value,
            "files_restored": report.files_restored,
            "files_checked": report.files_checked,
            "integrity_passed": report.integrity_passed,
            "snapshot_commit": report.snapshot_commit,
            "guardian_notified": report.guardian_notified,
            "errors": report.errors,
            "warnings": report.warnings,
            "rollback_executed": report.rollback_executed,
        }

        with open(report_file, "a") as f:
            f.write(json.dumps(report_dict) + "\n")

        # Take action based on status
        if report.status == RestoreStatus.COMPLETE:
            print(f"✓ Restore successful from {report.source.name}")
            if report.integrity_passed:
                print("✓ Integrity verified")
            else:
                print("⚠ Warning: Integrity check had issues")

        elif report.status == RestoreStatus.FAILED:
            print(f"❌ Restore failed from {report.source.name}")
            for error in report.errors:
                print(f"  ❌ {error}")

            # Consider triggering rollback
            if report.snapshot_commit:
                print(f"Rollback available to commit: {report.snapshot_commit}")

        elif report.status == RestoreStatus.ROLLED_BACK:
            print(f"⚠ Restore rolled back to: {report.rollback_point}")

    return handle_restore_completion


"""
EXAMPLE 4: Guardian AI Integration
===================================
Notify Guardian AI about restore status via voice.
"""

def example_guardian_ai_integration():
    """
    Integrate restore notifications with Guardian AI voice system.
    """

    companion_integration = """
    # In your companion_mode.py or guardian_system.py:
    
    from pathlib import Path
    import json
    from datetime import datetime
    
    class CompanionRestoreMonitor:
        def __init__(self):
            self.notification_log = Path("C:/IG/logs/companion_notifications.log")
            self.last_read = 0
        
        def check_restore_notifications(self):
            '''Poll the restore notification log.'''
            if not self.notification_log.exists():
                return []
            
            with open(self.notification_log, "r") as f:
                lines = f.readlines()
            
            # Read only new lines since last check
            new_lines = lines[self.last_read:]
            self.last_read = len(lines)
            
            notifications = []
            for line in new_lines:
                if "RESTORE:" in line:
                    # Parse the notification
                    message = line.split("RESTORE:")[-1].strip()
                    notifications.append(message)
            
            return notifications
        
        def voice_restore_status(self, message: str):
            '''Convert restore message to voice.'''
            # Use text-to-speech system
            self.tts.speak(message)
            
            # Log voice action
            with open("C:/IG/logs/companion_voice.log", "a") as f:
                f.write(f"[{datetime.now().isoformat()}] "
                        f"VOICED: {message}\\n")
    
    # In your main companion loop:
    monitor = CompanionRestoreMonitor()
    while companion_active:
        notifications = monitor.check_restore_notifications()
        for notification in notifications:
            monitor.voice_restore_status(notification)
        time.sleep(1)
    """
    print(companion_integration)


"""
EXAMPLE 5: Automated Restore Workflow
======================================
Chain restore with other operations (backup, archive, etc.)
"""

def example_automated_restore_workflow():
    """
    Automated workflow: Verify → Backup → Restore → Verify
    """

    workflow = """
    from restore_panel import RestorePanel, RestoreSource, RestoreStatus
    from recovery_dashboard import RecoveryDashboard
    
    class AutomatedRestoreWorkflow:
        def __init__(self):
            self.recovery = RecoveryDashboard()
            self.restore = RestorePanel()
        
        def run_full_recovery(self, source: RestoreSource):
            '''Execute: verify → create backup → restore → verify'''
            
            # Step 1: Verify current state
            print("[1/4] Verifying current state...")
            self.recovery.run_scan()
            
            # Step 2: Create backup of current state
            print("[2/4] Creating backup...")
            # Call backup system here
            
            # Step 3: Restore from source
            print("[3/4] Restoring from backup...")
            self.restore.source_combo.setCurrentText(source.name)
            self.restore.start_restore()
            
            # Wait for completion
            # (In real code, use signals/slots)
            
            # Step 4: Verify restored state
            print("[4/4] Verifying restored files...")
            self.recovery.verify_backups()
            
            print("✓ Full recovery workflow complete")
    
    workflow_runner = AutomatedRestoreWorkflow()
    workflow_runner.run_full_recovery(RestoreSource.SSD)
    """
    print(workflow)


"""
EXAMPLE 6: Error Handling and Rollback
========================================
Handle restore errors and trigger rollback if needed.
"""

def example_error_handling():
    """
    Comprehensive error handling for restore operations.
    """

    error_handler = """
    from restore_panel import RestoreReport, RestoreStatus
    import subprocess
    
    def handle_restore_error(report: RestoreReport) -> bool:
        '''Handle restore error and attempt rollback.'''
        
        if report.status == RestoreStatus.COMPLETE:
            return True  # Success
        
        if report.status == RestoreStatus.FAILED:
            print(f"❌ Restore failed: {len(report.errors)} errors")
            
            # Detailed error report
            for i, error in enumerate(report.errors, 1):
                print(f"  Error {i}: {error}")
            
            # Attempt rollback if snapshot available
            if report.snapshot_commit and report.rollback_point:
                if confirm_rollback():
                    rollback_to_commit(report.rollback_point)
                    return False  # Rolled back
            
            return False  # Failed, not rolled back
        
        elif report.status == RestoreStatus.ROLLED_BACK:
            print(f"⚠ Restore rolled back to {report.rollback_point}")
            return False
        
        return True
    
    def rollback_to_commit(commit_hash: str) -> bool:
        '''Rollback to a previous commit.'''
        try:
            result = subprocess.run(
                ["git", "-C", "C:/IG", "reset", "--hard", commit_hash],
                capture_output=True,
                timeout=60,
            )
            return result.returncode == 0
        except Exception as e:
            print(f"Rollback failed: {e}")
            return False
    
    def confirm_rollback() -> bool:
        '''Ask user to confirm rollback.'''
        # In GUI app, show QMessageBox
        # In CLI, ask input()
        return input("Rollback to previous commit? (y/n): ").lower() == "y"
    """
    print(error_handler)


"""
EXAMPLE 7: Performance Monitoring
==================================
Track restore performance metrics.
"""

def example_performance_monitoring():
    """
    Monitor restore performance and log metrics.
    """

    monitoring = """
    from restore_panel import RestoreReport
    from datetime import datetime, timedelta
    import json
    
    class RestorePerformanceMonitor:
        def __init__(self):
            self.metrics_file = Path("C:/IG/logs/restore_metrics.jsonl")
        
        def record_metrics(self, report: RestoreReport):
            '''Record restore performance metrics.'''
            
            # Calculate metrics
            duration = (datetime.now() - report.timestamp).total_seconds()
            files_per_sec = report.files_restored / duration if duration > 0 else 0
            
            metrics = {
                "timestamp": report.timestamp.isoformat(),
                "source": report.source.value,
                "duration_seconds": duration,
                "files_restored": report.files_restored,
                "files_per_second": files_per_sec,
                "integrity_check_passed": report.integrity_passed,
                "snapshot_created": report.snapshot_commit is not None,
            }
            
            self.metrics_file.parent.mkdir(parents=True, exist_ok=True)
            with open(self.metrics_file, "a") as f:
                f.write(json.dumps(metrics) + "\\n")
            
            return metrics
        
        def get_average_metrics(self) -> dict:
            '''Calculate average restore performance.'''
            if not self.metrics_file.exists():
                return {}
            
            metrics_list = []
            with open(self.metrics_file, "r") as f:
                for line in f:
                    metrics_list.append(json.loads(line))
            
            if not metrics_list:
                return {}
            
            avg_duration = sum(m["duration_seconds"] for m in metrics_list) / len(metrics_list)
            avg_throughput = sum(m["files_per_second"] for m in metrics_list) / len(metrics_list)
            
            return {
                "average_duration_seconds": avg_duration,
                "average_throughput_files_per_second": avg_throughput,
                "total_restores": len(metrics_list),
            }
    
    monitor = RestorePerformanceMonitor()
    # monitor.record_metrics(report)
    # stats = monitor.get_average_metrics()
    """
    print(monitoring)


if __name__ == "__main__":
    print("IG Restore Panel Integration Examples")
    print("=" * 60)
    print()
    print("1. Standalone Restore Panel")
    print("2. Recovery Dashboard Integration")
    print("3. Custom Report Handler")
    print("4. Guardian AI Integration")
    print("5. Automated Restore Workflow")
    print("6. Error Handling and Rollback")
    print("7. Performance Monitoring")
    print()
    print("Uncomment the example you want to see.")
    print()
    # example_handle_restore_report()
