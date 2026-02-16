import importlib.util
import sys
import threading
from types import SimpleNamespace

import pytest

from adaptive_executor import AdaptiveExecutor, MultiCriterionPolicy
from adaptive_executor.criteria import CpuCriterion


def _mock_psutil(monkeypatch, cpu_percent, memory_percent=50.0):
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
    "cpu_percent,expected_limit",
    [
        (85.0, 4),  # 85 >= 80 -> CpuCriterion returns 4
        (30.0, 1),  # 30 < 80 -> CpuCriterion returns 1
    ],
)
def test_cpu_criterion_drives_executor_limit(monkeypatch, cpu_percent, expected_limit):
    _mock_psutil(monkeypatch, cpu_percent=cpu_percent)

    policy = MultiCriterionPolicy(
        criteria=[CpuCriterion(threshold=80.0, workers=4)],
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
