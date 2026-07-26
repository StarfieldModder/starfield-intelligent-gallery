import json
from pathlib import Path
from datetime import datetime
import traceback as tb

DIAG_DB_PATH = Path(r"C:\SIG\diagnostics\program_error_database.json")


def record_error(
    module: str,
    function: str,
    line: int,
    error_type: str,
    message: str,
    severity: str = "error",
    exc: Exception | None = None,
) -> None:
    """
    Append a single error event to program_error_database.json.
    Safe: never raises, even if diagnostics are broken.
    """
    DIAG_DB_PATH.parent.mkdir(parents=True, exist_ok=True)

    try:
        if DIAG_DB_PATH.exists():
            with open(DIAG_DB_PATH, "r", encoding="utf-8") as f:
                db = json.load(f)
        else:
            db = {"errors": []}
    except Exception:
        db = {"errors": []}

    entry = {
        "timestamp": datetime.now().isoformat(timespec="seconds"),
        "module": module,
        "function": function,
        "line": line,
        "error_type": error_type,
        "message": message,
        "severity": severity,
    }

    if exc is not None:
        entry["traceback"] = "".join(tb.format_exception(type(exc), exc, exc.__traceback__))

    db.setdefault("errors", []).append(entry)

    try:
        with open(DIAG_DB_PATH, "w", encoding="utf-8") as f:
            json.dump(db, f, indent=2)
    except Exception:
        # Last‑ditch: swallow errors so diagnostics never crash SIG
        pass
