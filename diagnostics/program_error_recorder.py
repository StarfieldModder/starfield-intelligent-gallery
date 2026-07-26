import json
from pathlib import Path
from datetime import datetime
import traceback as tb

DB_PATH = Path(r"C:\SIG\diagnostics\program_error_database.json")


def _load_db():
    if DB_PATH.exists():
        try:
            with open(DB_PATH, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            # If DB is corrupted, start fresh
            return {"errors": []}
    return {"errors": []}


def _save_db(db):
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(DB_PATH, "w", encoding="utf-8") as f:
        json.dump(db, f, indent=2)


def record_error(
    module: str,
    function: str,
    line: int,
    error_type: str,
    message: str,
    traceback: str | None = None,
    severity: str = "error",
):
    db = _load_db()

    entry = {
        "timestamp": datetime.now().isoformat(timespec="seconds"),
        "module": module,
        "function": function,
        "line": line,
        "error_type": error_type,
        "message": message,
        "traceback": traceback,
        "severity": severity,
    }

    db.setdefault("errors", []).append(entry)
    _save_db(db)

    print("[SIG Diagnostics] Recorded error:")
    print(f"  {entry['timestamp']} | {module}:{line} | {error_type} — {message}")


def record_exception(module: str, function: str, line: int, exc: Exception, severity: str = "error"):
    tb_str = "".join(tb.format_exception(type(exc), exc, exc.__traceback__))
    record_error(
        module=module,
        function=function,
        line=line,
        error_type=type(exc).__name__,
        message=str(exc),
        traceback=tb_str,
        severity=severity,
    )
