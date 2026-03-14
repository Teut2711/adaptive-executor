import threading
import time

import pytest

from adaptive_executor import AdaptiveExecutor


class FixedPolicy:
    def __init__(self, workers):
        self.workers = workers

    def target_workers(self):
        return self.workers


def _run_io_batch(worker_limit, task_count=12, sleep_s=0.08):
    executor = AdaptiveExecutor(
        max_workers=12,
        policy=FixedPolicy(worker_limit),
        check_interval=60,
    )
    try:
        started = time.perf_counter()
        for _ in range(task_count):
            executor.submit(time.sleep, sleep_s)

        assert executor.join(timeout=10)
        return time.perf_counter() - started
    finally:
        executor.shutdown()
        executor.join()


@pytest.mark.integration
def test_executor_respects_real_runtime_concurrency_limit():
    limit = 3
    task_count = 15
    executor = AdaptiveExecutor(
        max_workers=8,
        policy=FixedPolicy(limit),
        check_interval=60,
    )

    active = 0
    max_active = 0
    lock = threading.Lock()

    def io_task():
        nonlocal active, max_active
        with lock:
            active += 1
            max_active = max(max_active, active)
        time.sleep(0.06)
        with lock:
            active -= 1

    try:
        for _ in range(task_count):
            executor.submit(io_task)

        assert executor.join(timeout=10)
        assert max_active == limit
    finally:
        executor.shutdown()
        executor.join()


@pytest.mark.integration
def test_executor_parallel_io_is_faster_than_single_worker():
    # With I/O-bound sleep tasks, 4 workers should finish significantly faster than 1.
    # Expected ratio is near 4x in ideal conditions; we keep a conservative bound for CI
    # noise.
    single_worker_time = _run_io_batch(worker_limit=1)
    four_worker_time = _run_io_batch(worker_limit=4)

    assert four_worker_time < single_worker_time * 0.65
