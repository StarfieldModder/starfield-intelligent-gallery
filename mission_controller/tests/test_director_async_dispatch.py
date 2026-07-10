# mission_controller/tests/test_director_async_dispatch.py
import threading
import asyncio

class AsyncWorker:
    def __init__(self):
        self._dispatched = []
        self._running = True
        self._lock = threading.RLock()

    async def dispatch(self, mission_record):
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

from mission_controller.director import MissionDirector

def run_coro_sync(coro):
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

def test_async_worker_used_via_run_coro_sync():
    async_worker = AsyncWorker()
    director = MissionDirector(worker_manager=async_worker)

    # wrap async dispatch so MissionDirector can call it synchronously
    async_dispatch = async_worker.dispatch
    def sync_dispatch(mission_record):
        return run_coro_sync(async_dispatch(mission_record))
    async_worker.dispatch = sync_dispatch

    mids = []
    for i in range(8):
        mid = director.create_mission(f"async-{i}", {"i": i})
        mids.append(mid)
        director.start_mission(mid)

    dispatched = async_worker.dispatched()
    assert len(dispatched) == 8
    assert {r[1]["id"] for r in dispatched} == set(mids)

def test_async_worker_dispatch_from_threads():
    async_worker = AsyncWorker()
    director = MissionDirector(worker_manager=async_worker)

    async_dispatch = async_worker.dispatch
    def run_coro_sync_local(coro):
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

    def sync_dispatch(mission_record):
        return run_coro_sync_local(async_dispatch(mission_record))
    async_worker.dispatch = sync_dispatch

    created = []
    lock = threading.Lock()

    def create_and_dispatch(i):
        mid = director.create_mission(f"thread-async-{i}", {"i": i})
        director.start_mission(mid)
        with lock:
            created.append(mid)

    threads = [threading.Thread(target=create_and_dispatch, args=(i,)) for i in range(16)]
    for t in threads:
        t.start()
    for t in threads:
        t.join(timeout=2.0)

    dispatched = async_worker.dispatched()
    assert len(dispatched) == 16
    assert {r[1]["id"] for r in dispatched} == set(created)
