import importlib.util
import sys
import threading
from datetime import time
from types import SimpleNamespace

import pytest

from adaptive_executor import AdaptiveExecutor, MultiCriterionPolicy
from adaptive_executor.criteria import CpuCriterion, MemoryCriterion, TimeCriterion


def _mock_psutil(monkeypatch, cpu_percent, memory_percent):
    fake_psutil = SimpleNamespace(
        cpu_percent=lambda interval=0.1: cpu_percent,
        virtual_memory=lambda: SimpleNamespace(percent=memory_percent),
    )
    monkeypatch.setitem(sys.modules, "psutil", fake_psutil)

    original_find_spec = importlib.util.find_spec

    def fake_find_spec(name, *args, **kwargs):
        if name == "psutil":
            return object()
        return original_find_spec(name, *args, **kwargs)

    monkeypatch.setattr(importlib.util, "find_spec", fake_find_spec)


@pytest.mark.integration
@pytest.mark.parametrize(
    "frozen_utc,cpu_percent,memory_percent,expected_limit",
    [
        # Time criterion timezone is Asia/Kolkata (UTC+5:30).
        # 2026-01-08 09:00 UTC = 14:30 IST, within 14:00-16:00 -> TimeCriterion = 6
        # CpuCriterion: 85 >= 80 -> 4
        # MemoryCriterion: 95 >= 90 -> 3
        # Policy math: min(6, 4, 3) = 3
        ("2026-01-08 09:00:00", 85.0, 95.0, 3),
        # 2026-01-08 20:00 UTC = 01:30 IST (next day), outside 14:00-16:00 -> 1
        # CpuCriterion: 85 >= 80 -> 4
        # MemoryCriterion: 95 >= 90 -> 3
        # Policy math: min(1, 4, 3) = 1
        ("2026-01-08 20:00:00", 85.0, 95.0, 1),
    ],
)
def test_mixed_criteria_choose_expected_limit(
    monkeypatch, frozen_utc, cpu_percent, memory_percent, expected_limit
):
    freezegun = pytest.importorskip("freezegun")
    _mock_psutil(monkeypatch, cpu_percent=cpu_percent, memory_percent=memory_percent)

    criteria = [
        TimeCriterion(
            worker_count=6,
            active_start=time(14, 0),
            active_end=time(16, 0),
            timezone="Asia/Kolkata",
        ),
        CpuCriterion(threshold=80.0, workers=4),
        MemoryCriterion(threshold=90.0, workers=3),
    ]
    policy = MultiCriterionPolicy(criteria=criteria, hard_cap=10)

    with freezegun.freeze_time(frozen_utc):
        executor = AdaptiveExecutor(max_workers=10, policy=policy, check_interval=60)

        done = threading.Event()
        executor.submit(done.set)
        executor.join(timeout=2)

        assert done.is_set()
        assert executor.current_limit == expected_limit

        executor.shutdown()
        executor.join()
