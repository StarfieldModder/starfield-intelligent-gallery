# ============================================================
#   INTELLIGENT GALLERY — MODULE HEADER
# ------------------------------------------------------------
#   Module: guardian_ai.py
#   Description: Core Sentinel intelligence for monitoring,
#                protecting, guiding, and interfacing with the
#                Intelligent Gallery Temple Architecture.
#   Author: Mark J. Latsha
#   Co-Author: Microsoft Copilot
#   Version: 2.0
#   Date: 2026-07-28
#
#   Launch Command:
#       python guardian_ai.py
#
#   Notes:
#       - Central intelligence for IG
#       - Monitors modules, artifacts, logs, and integrity
#       - Provides guidance, protection, and UI interface
# ============================================================

import os
import time
import json
from pathlib import Path
from loguru import logger

# PySide6 UI
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton, QApplication
import sys

from memory.memory_core import MemoryCore

# ------------------------------------------------------------
# GUARDIAN CONFIGURATION
# ------------------------------------------------------------

GUARDIAN_NAME = "IG Sentinel"
GUARDIAN_VERSION = "2.0"
GUARDIAN_ROOT = Path("C:/IG")

MODULES_DIR = GUARDIAN_ROOT / "modules"
ARTIFACTS_DIR = GUARDIAN_ROOT / "artifacts"
LOGS_DIR = GUARDIAN_ROOT / "logs"
INTEGRITY_LOG = LOGS_DIR / "integrity_timeline.log"

# ------------------------------------------------------------
# GUARDIAN AI CLASS
# ------------------------------------------------------------

class GuardianAI:
    def __init__(self):
        logger.add(LOGS_DIR / "guardian_ai.log", rotation="1 MB")

        # Core states
        self.status = "ONLINE"
        self.threat_level = "LOW"          # LOW, MEDIUM, HIGH, CRITICAL
        self.emotional_state = "CALM"      # CALM, ALERT, CONCERNED, PROTECTIVE
        self.mode = "OBSERVE"              # OBSERVE, INVESTIGATE, PROTECT, RECOVER

        # Memory core
        self.journal = []                  # Stores recent events
        self.memory = {}                   # Key-value memory store
        self.last_scan = None

        logger.info(f"{GUARDIAN_NAME} v{GUARDIAN_VERSION} initialized.")
        self.speak("Sentinel online. The Gallery is under my protection.")

    # --------------------------------------------------------
    # SPEAK — Guardian’s voice
    # --------------------------------------------------------
    def speak(self, message: str):
        logger.info(f"[Guardian] {message}")
        print(f"\n{GUARDIAN_NAME}: {message}")

    # --------------------------------------------------------
    # MEMORY CORE
    # --------------------------------------------------------
    def remember_event(self, event: str):
        timestamp = time.ctime()
        entry = f"{timestamp} — {event}"
        self.journal.append(entry)

        # Keep journal small and efficient
        if len(self.journal) > 50:
            self.journal.pop(0)

        logger.info(f"Memory event recorded: {event}")

    def recall_recent_events(self, count=5):
        return self.journal[-count:]

    # --------------------------------------------------------
    # ADVANCED BEHAVIORS — Threat, Emotion, Mode
    # --------------------------------------------------------
    def set_threat_level(self, level):
        self.threat_level = level
        self.speak(f"Threat level updated to {level}.")
        self.remember_event(f"Threat level set to {level}")

    def set_emotional_state(self, state):
        self.emotional_state = state
        self.speak(f"Emotional state shifted to {state}.")
        self.remember_event(f"Emotional state set to {state}")

    def set_mode(self, mode):
        self.mode = mode
        self.speak(f"Guardian mode changed to {mode}.")
        self.remember_event(f"Mode changed to {mode}")

    # --------------------------------------------------------
    # PERSONALITY BEHAVIORS
    # --------------------------------------------------------
    def encourage(self):
        messages = [
            "The Gallery grows stronger with every step you take.",
            "Your work brings clarity to the Temple.",
            "I see your progress — and it is extraordinary.",
            "The artifacts resonate with your dedication."
        ]
        msg = messages[int(time.time()) % len(messages)]
        self.speak(msg)
        self.remember_event(f"Encouragement given: {msg}")

    def warn(self, issue):
        msg = f"⚠️ Warning detected: {issue}"
        self.speak(msg)
        logger.warning(f"Guardian Warning: {issue}")
        self.remember_event(f"Warning issued: {issue}")

    def praise(self, module):
        msg = f"✨ Module '{module}' is functioning perfectly."
        self.speak(msg)
        logger.info(f"Guardian Praise: {module} stable.")
        self.remember_event(f"Praise for module: {module}")

    # --------------------------------------------------------
    # SCAN MODULES — Integrity check
    # --------------------------------------------------------
    def scan_modules(self):
        self.speak("Beginning module integrity scan...")
        issues = []

        for module in MODULES_DIR.glob("*.py"):
            if module.stat().st_size == 0:
                issues.append(f"Empty module detected: {module.name}")

        self.last_scan = time.time()

        if issues:
            self.speak("Integrity issues detected.")
            for issue in issues:
                logger.warning(issue)
                self.remember_event(f"Module issue: {issue}")
        else:
            self.speak("All modules passed integrity checks.")
            self.remember_event("Modules stable.")

        return issues

    # --------------------------------------------------------
    # SCAN ARTIFACTS — Relic check
    # --------------------------------------------------------
    def scan_artifacts(self):
        self.speak("Checking artifact vault...")
        missing = []

        for artifact in ARTIFACTS_DIR.glob("*"):
            if not artifact.exists():
                missing.append(artifact.name)

        if missing:
            self.speak("Artifact issues detected.")
            for m in missing:
                logger.warning(f"Missing artifact: {m}")
                self.remember_event(f"Missing artifact: {m}")
        else:
            self.speak("All artifacts accounted for.")
            self.remember_event("Artifacts stable.")

        return missing

    # --------------------------------------------------------
    # PROTECTION RULES — Adaptive behavior
    # --------------------------------------------------------
    def protect(self, issues, artifacts):
        if issues:
            self.set_threat_level("HIGH")
            self.set_emotional_state("CONCERNED")
            self.set_mode("PROTECT")

            for issue in issues:
                self.warn(issue)

            self.log_integrity_event("Module corruption detected.")
            return "PROTECTIVE_MODE"

        if artifacts:
            self.set_threat_level("MEDIUM")
            self.set_emotional_state("ALERT")
            self.set_mode("INVESTIGATE")

            for a in artifacts:
                self.warn(f"Missing artifact: {a}")

            self.log_integrity_event("Artifact vault inconsistency.")
            return "VAULT_ALERT"

        # Stable system
        self.set_threat_level("LOW")
        self.set_emotional_state("CALM")
        self.set_mode("OBSERVE")
        return "STABLE"

    # --------------------------------------------------------
    # MODULE INTEGRATION
    # --------------------------------------------------------
    def integrate_with_modules(self):
        integrations = {
            "restore_panel": MODULES_DIR / "restore_panel.py",
            "backup_scheduler": MODULES_DIR / "backup_scheduler.py",
            "diff_viewer": MODULES_DIR / "diff_viewer.py",
            "integrity_timeline": MODULES_DIR / "integrity_timeline.py",
            "recovery_dashboard": MODULES_DIR / "recovery_dashboard.py"
        }

        self.speak("Checking module integration points…")

        for name, path in integrations.items():
            if path.exists():
                logger.info(f"Integration OK: {name}")
                self.remember_event(f"Integration OK: {name}")
            else:
                self.warn(f"Missing module integration: {name}")

        self.speak("Module integration scan complete.")

    # --------------------------------------------------------
    # ARTIFACT REGISTRY
    # --------------------------------------------------------
    def load_artifact_registry(self):
        registry_file = ARTIFACTS_DIR / "registry.json"

        if not registry_file.exists():
            self.warn("Artifact registry missing.")
            return {}

        try:
            with open(registry_file, "r") as f:
                registry = json.load(f)
            self.speak("Artifact registry loaded.")
            self.remember_event("Artifact registry loaded.")
            return registry
        except Exception as e:
            self.warn(f"Registry load error: {e}")
            return {}

    def describe_artifact(self, name):
        registry = self.load_artifact_registry()
        if name in registry:
            data = registry[name]
            desc = data.get("description", "No description")
            self.speak(f"Artifact '{name}': {desc}")
            self.remember_event(f"Artifact described: {name}")
        else:
            self.warn(f"Artifact '{name}' not found in registry.")


    # --------------------------------------------------------
    # TEMPLE EVENT SYSTEM — Awareness of the Gallery
    # --------------------------------------------------------
    def detect_events(self):
        events = []

        # Detect module changes
        for module in MODULES_DIR.glob("*.py"):
            mtime = module.stat().st_mtime
            key = f"module_mtime_{module.name}"

            if key not in self.memory:
                self.memory[key] = mtime
                events.append(f"Module detected: {module.name}")
            elif self.memory[key] != mtime:
                self.memory[key] = mtime
                events.append(f"Module updated: {module.name}")

        # Detect artifact changes
        for artifact in ARTIFACTS_DIR.glob("*"):
            mtime = artifact.stat().st_mtime
            key = f"artifact_mtime_{artifact.name}"

            if key not in self.memory:
                self.memory[key] = mtime
                events.append(f"Artifact detected: {artifact.name}")
            elif self.memory[key] != mtime:
                self.memory[key] = mtime
                events.append(f"Artifact updated: {artifact.name}")

        # Detect deleted modules
        known_modules = [k for k in self.memory.keys() if k.startswith("module_mtime_")]
        for key in known_modules:
            name = key.replace("module_mtime_", "")
            if not (MODULES_DIR / name).exists():
                events.append(f"Module deleted: {name}")
                del self.memory[key]

        # Detect deleted artifacts
        known_artifacts = [k for k in self.memory.keys() if k.startswith("artifact_mtime_")]
        for key in known_artifacts:
            name = key.replace("artifact_mtime_", "")
            if not (ARTIFACTS_DIR / name).exists():
                events.append(f"Artifact deleted: {name}")
                del self.memory[key]

        # React to events
        for event in events:
            self.remember_event(event)
            self.speak(f"Temple Event: {event}")

            # Adaptive emotional response
            if "updated" in event:
                self.set_emotional_state("ALERT")
            if "deleted" in event:
                self.set_threat_level("MEDIUM")
                self.set_emotional_state("CONCERNED")
                self.set_mode("INVESTIGATE")

        return events

    # --------------------------------------------------------
    # TEMPLE EVENT HEARTBEAT — Called inside run()
    # --------------------------------------------------------
    def event_heartbeat(self):
        events = self.detect_events()
        if events:
            self.log_integrity_event(f"Temple events detected: {len(events)}")
        else:
            self.remember_event("No temple events detected.")


    # --------------------------------------------------------
    # LOG INTEGRITY EVENT
    # --------------------------------------------------------
    def log_integrity_event(self, event: str):
        with open(INTEGRITY_LOG, "a") as f:
            f.write(f"{time.ctime()} — {event}\n")
        logger.info(f"Integrity event logged: {event}")
        self.remember_event(f"Integrity event: {event}")


    # --------------------------------------------------------
    # RUN — Main Guardian loop
    # --------------------------------------------------------
    def run(self):
        self.speak("Guardian AI is now watching over the Gallery...")

        while True:
            issues = self.scan_modules()
            artifacts = self.scan_artifacts()
            mode = self.protect(issues, artifacts)

            self.event_heartbeat()

            self.log_integrity_event(f"Guardian Mode: {mode}")
            time.sleep(10)   # Guardian heartbeat


# ------------------------------------------------------------
# GUARDIAN UI PANEL (PySide6)
# ------------------------------------------------------------

class GuardianPanel(QWidget):
    def __init__(self, guardian: GuardianAI):
        super().__init__()
        self.guardian = guardian
        self.setWindowTitle("IG Guardian AI")
        self.setMinimumSize(400, 300)

        layout = QVBoxLayout()

        self.status_label = QLabel("Guardian Status: ONLINE")
        layout.addWidget(self.status_label)

        scan_button = QPushButton("Run Integrity Scan")
        scan_button.clicked.connect(self.run_scan)
        layout.addWidget(scan_button)

        encourage_button = QPushButton("Encourage Me")
        encourage_button.clicked.connect(self.guardian.encourage)
        layout.addWidget(encourage_button)

        self.setLayout(layout)

    def run_scan(self):
        issues = self.guardian.scan_modules()
        artifacts = self.guardian.scan_artifacts()
        mode = self.guardian.protect(issues, artifacts)

        self.status_label.setText(f"Guardian Status: {mode}")

# ------------------------------------------------------------
# MAIN ENTRY POINT
# ------------------------------------------------------------

if __name__ == "__main__":
    guardian = GuardianAI()

    app = QApplication(sys.argv)
    panel = GuardianPanel(guardian)
    panel.show()

    sys.exit(app.exec())
