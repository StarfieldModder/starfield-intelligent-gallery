# mission_controller/tests/test_director_async.py
import asyncio
import threading
import pytest

# Async stub for worker manager used only in tests
class AsyncWorkerManager:
    def __init__(self):
        self._dispatched = []
        self._running = True
        self._lock = threading.RLock()

    async def dispatch(self, mission_record):
        if not self._running:
            raise RuntimeError("shut down")
        # simulate async work
        await asyncio.sleep(0.001)
        dispatch_id = f"dispatch-{int(asyncio.get_event_loop().time() * 1000)}"
        with self._lock:
            self._dispatched.append((dispatch_id, mission_record))
        return dispatch_id

    async def shutdown(self):
        self._running = False

    def dispatched(self):
        with self._lock:
            return list(self._dispatched)

# Helper to run an async coroutine from synchronous code in a thread-safe way.
def run_coro_sync(coro):
    """
    Create a fresh event loop, run the coroutine to completion, then close the loop.
    Safe to call from tests and worker threads.
    """
    loop = asyncio.new_event_loop()
    try:
        asyncio.set_event_loop(loop)
        return loop.run_until_complete(coro)
    finally:
        try:
            loop.run_until_complete(loop.shutdown_asyncgens())
        except Exception:
            pass
        loop.close()
        asyncio.set_event_loop(None)

from mission_controller.director import MissionDirector

def test_async_worker_dispatch_called_directly_from_sync_code():
    """
    If MissionDirector is synchronous, call the async worker directly:
    - create mission with director
    - call the async worker's dispatch via run_coro_sync
    - assert dispatches recorded
    """
    async_worker = AsyncWorkerManager()
    director = MissionDirector(worker_manager=async_worker)

    mids = []
    for i in range(10):
        mid = director.create_mission(f"async-sync-{i}", {"i": i})
        mids.append(mid)
        # call the async worker dispatch directly in sync context
        # pass the mission record as the director would
        mission_record = director.get_status(mid)
        run_coro_sync(async_worker.dispatch(mission_record))

    dispatched = async_worker.dispatched()
    assert len(dispatched) == 10
    assert {r[1]["id"] for r in dispatched} == set(mids)

def test_async_worker_dispatch_from_threads():
    """
    Run async dispatches concurrently from multiple threads using run_coro_sync.
    This simulates multiple synchronous callers invoking the async worker.
    """
    async_worker = AsyncWorkerManager()
    director = MissionDirector(worker_manager=async_worker)

    created = []
    lock = threading.Lock()

    def create_and_dispatch(i):
        mid = director.create_mission(f"thread-async-{i}", {"i": i})
        mission_record = director.get_status(mid)
        # run the async dispatch in this thread
        run_coro_sync(async_worker.dispatch(mission_record))
        with lock:
            created.append(mid)

    threads = [threading.Thread(target=create_and_dispatch, args=(i,)) for i in range(20)]
    for t in threads:
        t.start()
    for t in threads:
        t.join(timeout=2.0)

    assert len(created) == 20
    dispatched = async_worker.dispatched()
    assert len(dispatched) == 20
    assert {r[1]["id"] for r in dispatched} == set(created)
