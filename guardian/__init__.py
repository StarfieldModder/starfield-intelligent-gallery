###############################################################################
#  INTELLIGENT GALLERY — GUARDIAN PACKAGE INITIALIZER
#  Module: guardian/__init__.py
#
#  Project: Starfield Intelligent Gallery (SIG)
#  Purpose:
#      Marks the guardian directory as a Python package and exports
#      the GuardianAI module for system-wide access.
#
#  Author: Mark J. Latsha (Games)
#  Co‑Author: Microsoft Copilot (AI Development Assistant)
#
#  Version: 1.0
#  Created: July 2026
#
#  Notes:
#      The Guardian AI provides 24/7 monitoring, anomaly detection,
#      predictive analysis, and artifact protection for the IG.
###############################################################################

from .guardian_ai import (
    GuardianAI,
    GuardianMonitor,
    AnomalyDetector,
    PredictiveAnalyzer,
    AnomalyReport,
    AnomalyType,
    IntegritySnapshot,
    HealthStatus,
    
)

self.memory_core = MemoryCore()
self.memory_core.record_event("guardian_event", event, {"source": "GuardianAI"})


__all__ = [
    "GuardianAI",
    "GuardianMonitor",
    "AnomalyDetector",
    "PredictiveAnalyzer",
    "AnomalyReport",
    "AnomalyType",
    "IntegritySnapshot",
    "HealthStatus",
]
