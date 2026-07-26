# core/diagnostic_reporter.py
# Minimal stub to satisfy imports and provide safe runtime logging.
# Save as UTF-8 without BOM at C:\SIG\core\diagnostic_reporter.py

import os
import sys
import traceback
from datetime import datetime
from typing import Any, Optional

_LOG_DIR = os.path.join(os.getenv("LOCALAPPDATA", os.path.expanduser("~")), "SIG", "logs")
os.makedirs(_LOG_DIR, exist_ok=True)
_LOG_FILE = os.path.join(_LOG_DIR, "diagnostic_reporter.log")


def _safe_write(text: str) -> None:
    try:
        with open(_LOG_FILE, "a", encoding="utf-8") as f:
            f.write(text + "\n")
    except Exception:
        # Best effort only; never raise from the reporter
        try:
            print(text, file=sys.stderr)
        except Exception:
            pass


def record_error(module: str,
                 function: str,
                 code: int,
                 exc_type: str,
                 message: str,
                 severity: str = "error",
                 exc: Optional[BaseException] = None) -> None:
    """
    Minimal error recorder used by other modules.

    Parameters
    - module: module name string (e.g., "fragment_orchestrator")
    - function: function name string (e.g., "update")
    - code: numeric code (user code in original project)
    - exc_type: exception class name or type string
    - message: human readable message
    - severity: severity string like "warning" or "critical"
    - exc: optional exception instance for traceback
    """
    ts = datetime.utcnow().isoformat() + "Z"
    tb = ""
    if exc is not None:
        try:
            tb = "".join(traceback.format_exception(type(exc), exc, exc.__traceback__))
        except Exception:
            tb = "Traceback unavailable"

    entry = f"{ts} | {severity.upper()} | {module}.{function} | code={code} | type={exc_type} | msg={message} | tb={tb}"
    _safe_write(entry)
