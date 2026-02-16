"""
Datetime-based Scaling Example
==============================

This example demonstrates how to use DateTimeCriterion to scale workers
for a specific timestamp window.
"""

import datetime
import logging
import threading
import time

from adaptive_executor import (
    AdaptiveExecutor,
    DateTimeCriterion,
    MultiCriterionPolicy,
    setup_logger,
)

setup_logger(level=logging.INFO)
logger = logging.getLogger("example.datetime_scaling")


def process_task(task_id: int) -> str:
    logger.info("Running task %d", task_id)
    time.sleep(1)
    return f"task-{task_id}-done"


def main() -> int:
    # Scale up between Jan 8, 2026 22:00 and Jan 9, 2026 03:00 (UTC).
    criterion = DateTimeCriterion(
        worker_count=6,
        active_start=datetime.datetime(2026, 1, 8, 22, 0, 0),
        active_end=datetime.datetime(2026, 1, 9, 3, 0, 0),
        timezone="UTC",
    )
    policy = MultiCriterionPolicy(criteria=[criterion], hard_cap=10)
    executor = AdaptiveExecutor(max_workers=10, policy=policy, check_interval=60)

    done = threading.Event()
    executor.submit(done.set)
    for i in range(3):
        executor.submit(process_task, i)

    executor.join(timeout=5)
    logger.info("Controller-selected worker limit: %d", executor.current_limit)
    logger.info("Control task completed: %s", done.is_set())

    executor.shutdown()
    executor.join()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
