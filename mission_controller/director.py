# mission_controller/director.py
"""
MissionDirector test stub and lightweight implementation.

This module provides a small, thread-safe MissionDirector suitable for unit
and integration tests. Key behavior:
- create_mission always returns the generated mission id (string).
- start_mission will attempt to dispatch to a registered worker manager
  but will not let dispatch failures crash the caller (stub swallows dispatch
  exceptions to keep tests deterministic).
- stop_mission, get_status, list_missions, register_worker_manager, and
  shutdown provide minimal, test-friendly semantics.

Keep this file small and free of heavy top-level imports so test collection
and static analysis remain robust.
"""

from typing import Any, Dict, List, Optional
import threading
import uuid
import time


class MissionNotFoundError(Exception):
    """Raised when a mission id is not found in the director's store."""
    pass


class MissionDirector:
    """
    Lightweight MissionDirector.

    Parameters
    ----------
    db_client:
        Optional database client with an `insert(record)` method.
    worker_manager:
        Optional worker manager with `dispatch(record)` and optional `shutdown()`.
    """

    def __init__(self, db_client: Optional[Any] = None, worker_manager: Optional[Any] = None):
        self._db = db_client
        self._workers = worker_manager
        self._missions: Dict[str, Dict[str, Any]] = {}
        self._lock = threading.RLock()
        self._running = True

    def create_mission(self, name: str, payload: Dict[str, Any]) -> str:
        """
        Create a mission record and return the generated mission id (string).

        The method will attempt a best-effort DB insert if `db_client` is provided,
        but it always returns the generated `mid` string. If the DB insert raises,
        the exception is propagated so callers/tests can observe DB failures.
        """
        with self._lock:
            mid = str(uuid.uuid4())
            record = {
                "id": mid,
                "name": name,
                "payload": payload,
                "status": "created",
                "created_at": time.time(),
            }
            # store in-memory
            self._missions[mid] = record

            # best-effort persistence: do not use the DB return value as the mission id
            if self._db:
                try:
                    self._db.insert(record)
                except Exception:
                    # propagate DB errors so tests that expect failures can catch them
                    raise

            return mid

    def start_mission(self, mission_id: str) -> None:
        """
        Mark mission as running and dispatch to the worker manager if present.

        If the mission is missing, raise MissionNotFoundError. Dispatch errors
        are swallowed in this lightweight stub to keep tests deterministic.
        """
        with self._lock:
            if mission_id not in self._missions:
                raise MissionNotFoundError(mission_id)
            self._missions[mission_id]["status"] = "running"
            self._missions[mission_id]["started_at"] = time.time()

            if self._workers and hasattr(self._workers, "dispatch"):
                try:
                    self._workers.dispatch(self._missions[mission_id])
                except Exception:
                    # swallow dispatch exceptions in the stub
                    pass

    def stop_mission(self, mission_id: str, reason: Optional[str] = None) -> None:
        """Stop a mission and record an optional reason."""
        with self._lock:
            if mission_id not in self._missions:
                raise MissionNotFoundError(mission_id)
            self._missions[mission_id]["status"] = "stopped"
            self._missions[mission_id]["stopped_at"] = time.time()
            if reason:
                self._missions[mission_id]["stop_reason"] = reason

    def get_status(self, mission_id: str) -> Dict[str, Any]:
        """Return a copy of the mission record for the given id."""
        with self._lock:
            if mission_id not in self._missions:
                raise MissionNotFoundError(mission_id)
            return dict(self._missions[mission_id])

    def list_missions(self, status: Optional[str] = None) -> List[Dict[str, Any]]:
        """List missions, optionally filtering by status."""
        with self._lock:
            items = list(self._missions.values())
            if status:
                items = [m for m in items if m.get("status") == status]
            return [dict(m) for m in items]

    def register_worker_manager(self, worker_manager: Any) -> None:
        """Register or replace the worker manager used for dispatching missions."""
        with self._lock:
            self._workers = worker_manager

    def shutdown(self) -> None:
        """Shutdown the director and attempt to shutdown the worker manager if present."""
        with self._lock:
            self._running = False
            if self._workers and hasattr(self._workers, "shutdown"):
                try:
                    self._workers.shutdown()
                except Exception:
                    # swallow shutdown errors in the stub
                    pass


__all__ = ["MissionDirector", "MissionNotFoundError"]
