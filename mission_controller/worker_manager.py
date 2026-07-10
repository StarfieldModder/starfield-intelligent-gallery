# mission_controller/worker_manager.py
from typing import Any, Dict
import threading
import time

class WorkerDispatchError(Exception):
    pass

class WorkerManager:
    """
    Minimal worker manager stub for tests.
    - dispatch accepts a mission record and returns a dispatch id
    - supports shutdown for graceful stop
    """
    def __init__(self):
        self._dispatched = []
        self._lock = threading.RLock()
        self._running = True

    def dispatch(self, mission_record: Dict[str, Any]) -> str:
        with self._lock:
            if not self._running:
                raise WorkerDispatchError("worker manager is shut down")
            dispatch_id = f"dispatch-{int(time.time() * 1000)}"
            self._dispatched.append((dispatch_id, mission_record))
            return dispatch_id

    def shutdown(self) -> None:
        with self._lock:
            self._running = False

    def dispatched(self):
        with self._lock:
            return list(self._dispatched)
