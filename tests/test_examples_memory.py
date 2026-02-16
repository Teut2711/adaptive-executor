import importlib.util
import sys
import threading
from types import SimpleNamespace

import pytest

from adaptive_executor import AdaptiveExecutor, MultiCriterionPolicy
from adaptive_executor.criteria import MemoryCriterion


def _mock_psutil(monkeypatch, memory_percent, cpu_percent=20.0):
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
    "memory_percent,expected_limit",
    [
        (92.0, 6),  # 92 >= 90 -> MemoryCriterion returns 6
        (35.0, 1),  # 35 < 90 -> MemoryCriterion returns 1
    ],
)
def test_memory_criterion_drives_executor_limit(
    monkeypatch, memory_percent, expected_limit
):
    _mock_psutil(monkeypatch, memory_percent=memory_percent)

    policy = MultiCriterionPolicy(
        criteria=[MemoryCriterion(threshold=90.0, workers=6)],
        hard_cap=10,
    )
    executor = AdaptiveExecutor(max_workers=10, policy=policy, check_interval=60)

    done = threading.Event()
    executor.submit(done.set)
    executor.join(timeout=2)

    assert done.is_set()
    assert executor.current_limit == expected_limit

    executor.shutdown()
    executor.join()
