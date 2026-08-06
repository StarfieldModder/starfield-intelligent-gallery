# guardian/__init__.py
import importlib, logging
logger = logging.getLogger(__name__)

_expected = [
    "GuardianAI","GuardianMonitor","AnomalyDetector","PredictiveAnalyzer",
    "AnomalyReport","AnomalyType","IntegritySnapshot","GuardianBridge",
    "GuardianPulse","GuardianVoice","GuardianSeverity",
]

try:
    _mod = importlib.import_module(".guardian_ai", package=__package__)
except Exception:
    logger.exception("Failed to import guardian.guardian_ai")
    raise

__all__ = []
for name in _expected:
    if hasattr(_mod, name):
        globals()[name] = getattr(_mod, name)
        __all__.append(name)
    else:
        logger.warning("guardian.guardian_ai missing expected symbol: %s", name)

guardian_ai = _mod

