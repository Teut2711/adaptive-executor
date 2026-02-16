import threading
from datetime import time

import pytest

from adaptive_executor import AdaptiveExecutor, MultiCriterionPolicy, TimeCriterion


@pytest.mark.integration
@pytest.mark.parametrize(
    "frozen_time,expected_limit",
    [
        # Time is frozen in UTC and each criterion is evaluated in timezone="UTC".
        # At 10:30 UTC:
        # - C1 (09:00-17:00) -> 8
        # - C2 (10:00-12:00) -> 5
        # - C3 (00:00-23:59) -> 7
        # Policy math: min(8, 5, 7) = 5
        ("2026-01-08 10:30:00", 5),
        # At 15:00 UTC:
        # - C1 (09:00-17:00) -> 8
        # - C2 (10:00-12:00) -> 1 (inactive criteria return 1)
        # - C3 (00:00-23:59) -> 7
        # Policy math: min(8, 1, 7) = 1
        ("2026-01-08 15:00:00", 1),
    ],
)
def test_time_criteria_choose_expected_executor_limit(frozen_time, expected_limit):
    freezegun = pytest.importorskip("freezegun")

    criteria = [
        TimeCriterion(
            worker_count=8,
            active_start=time(9, 0),
            active_end=time(17, 0),
            timezone="UTC",
        ),
        TimeCriterion(
            worker_count=5,
            active_start=time(10, 0),
            active_end=time(12, 0),
            timezone="UTC",
        ),
        TimeCriterion(
            worker_count=7,
            active_start=time(0, 0),
            active_end=time(23, 59),
            timezone="UTC",
        ),
    ]
    policy = MultiCriterionPolicy(criteria=criteria, hard_cap=10)

    with freezegun.freeze_time(frozen_time):
        executor = AdaptiveExecutor(
            max_workers=10,
            policy=policy,
            check_interval=60,
        )

        done = threading.Event()
        executor.submit(done.set)
        executor.join(timeout=2)

        assert done.is_set()
        assert executor.current_limit == expected_limit

        executor.shutdown()
        executor.join()
