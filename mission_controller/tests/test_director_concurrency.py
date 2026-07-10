# mission_controller/tests/test_director_concurrency.py
import threading
import time
import pytest

def test_concurrent_create_and_start(director_with_sync_worker):
    director, wm = director_with_sync_worker

    created = []
    lock = threading.Lock()

    def create_and_start(i):
        mid = director.create_mission(f"concurrent-{i}", {"i": i})
        time.sleep(0.002 * (i % 5))
        director.start_mission(mid)
        with lock:
            created.append(mid)

    threads = [threading.Thread(target=create_and_start, args=(i,)) for i in range(30)]
    for t in threads:
        t.start()
    for t in threads:
        t.join(timeout=2.0)

    assert len(created) == 30
    dispatched = wm.dispatched()
    assert len(dispatched) == 30
    dispatched_ids = {rec[1]["id"] for rec in dispatched}
    assert dispatched_ids == set(created)

def test_concurrent_start_ordering_and_integrity(director_with_sync_worker):
    director, wm = director_with_sync_worker

    mids = [director.create_mission(f"order-{i}", {"i": i}) for i in range(10)]

    def start(mid):
        director.start_mission(mid)

    threads = [threading.Thread(target=start, args=(mid,)) for mid in reversed(mids)]
    for t in threads:
        t.start()
    for t in threads:
        t.join(timeout=1.0)

    dispatched = wm.dispatched()
    assert len(dispatched) == 10
    assert {r[1]["id"] for r in dispatched} == set(mids)
