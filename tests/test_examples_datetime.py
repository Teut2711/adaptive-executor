import threading
import datetime

import pytest

from adaptive_executor import AdaptiveExecutor, MultiCriterionPolicy, DateTimeCriterion


@pytest.mark.integration
@pytest.mark.parametrize(
    "frozen_time,expected_limit",
    [
        ("2026-01-08 23:00:00", 6),  # Inside active datetime window
        ("2026-01-09 04:00:00", 1),  # Outside active datetime window
    ],
)
def test_datetime_criterion_drives_executor_limit(frozen_time, expected_limit):
    freezegun = pytest.importorskip("freezegun")

    criterion = DateTimeCriterion(
        worker_count=6,
        active_start=datetime.datetime(2026, 1, 8, 22, 0, 0),
        active_end=datetime.datetime(2026, 1, 9, 3, 0, 0),
        timezone="UTC",
    )
    policy = MultiCriterionPolicy(criteria=[criterion], hard_cap=10)

    with freezegun.freeze_time(frozen_time):
        executor = AdaptiveExecutor(max_workers=10, policy=policy, check_interval=60)

        done = threading.Event()
        executor.submit(done.set)
        executor.join(timeout=2)

        assert done.is_set()
        assert executor.current_limit == expected_limit

        executor.shutdown()
        executor.join()
