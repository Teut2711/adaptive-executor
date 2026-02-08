import time
import threading
import signal
from unittest.mock import patch

import pytest

from adaptive_executor.executor import AdaptiveExecutor
from adaptive_executor.policies import MultiCriterionPolicy


def test_initialization(mocker):
    mock_policy = mocker.MagicMock(spec=MultiCriterionPolicy)
    mock_policy.target_workers.return_value = 5

    executor = AdaptiveExecutor(max_workers=10, policy=mock_policy)

    assert executor.max_workers == 10
    assert executor.policy == mock_policy
    assert executor.check_interval == 60
    assert executor.current_limit == 5
    assert executor.shutdown_flag is False

    executor.shutdown()
    executor.join()


def test_initialization_with_custom_check_interval(mocker):
    mock_policy = mocker.MagicMock(spec=MultiCriterionPolicy)
    mock_policy.target_workers.return_value = 3

    executor = AdaptiveExecutor(
        max_workers=8, policy=mock_policy, check_interval=30
    )

    assert executor.check_interval == 30

    executor.shutdown()
    executor.join()


def test_set_limit_increase(mocker):
    mock_policy = mocker.MagicMock(spec=MultiCriterionPolicy)
    mock_policy.target_workers.return_value = 3

    executor = AdaptiveExecutor(max_workers=10, policy=mock_policy)

    executor._set_limit(7)
    assert executor.current_limit == 7

    executor.shutdown()
    executor.join()


def test_set_limit_decrease(mocker):
    mock_policy = mocker.MagicMock(spec=MultiCriterionPolicy)
    mock_policy.target_workers.return_value = 7

    executor = AdaptiveExecutor(max_workers=10, policy=mock_policy)

    executor._set_limit(3)
    assert executor.current_limit == 3

    executor.shutdown()
    executor.join()


def test_set_limit_respects_max_workers(mocker):
    mock_policy = mocker.MagicMock(spec=MultiCriterionPolicy)
    mock_policy.target_workers.return_value = 5

    executor = AdaptiveExecutor(max_workers=10, policy=mock_policy)

    executor._set_limit(15)
    assert executor.current_limit == 10

    executor.shutdown()
    executor.join()


def test_submit_task(mocker):
    mock_policy = mocker.MagicMock(spec=MultiCriterionPolicy)
    mock_policy.target_workers.return_value = 2

    executor = AdaptiveExecutor(max_workers=5, policy=mock_policy)

    task_executed = threading.Event()

    def test_task():
        task_executed.set()

    executor.submit(test_task)

    assert task_executed.wait(timeout=2)

    executor.shutdown()
    executor.join()


def test_submit_multiple_tasks(mocker):
    mock_policy = mocker.MagicMock(spec=MultiCriterionPolicy)
    mock_policy.target_workers.return_value = 3

    executor = AdaptiveExecutor(max_workers=5, policy=mock_policy)

    executed = set()
    lock = threading.Lock()
    done = threading.Event()

    def task(i):
        with lock:
            executed.add(i)
            if len(executed) == 3:
                done.set()

    for i in range(3):
        executor.submit(task, i)

    assert done.wait(timeout=2)
    assert executed == {0, 1, 2}

    executor.shutdown()
    executor.join()


def test_join_waits_for_tasks(mocker):
    mock_policy = mocker.MagicMock(spec=MultiCriterionPolicy)
    mock_policy.target_workers.return_value = 2

    executor = AdaptiveExecutor(max_workers=5, policy=mock_policy)

    started = threading.Event()
    completed = threading.Event()

    def slow_task():
        started.set()
        time.sleep(0.3)
        completed.set()

    executor.submit(slow_task)

    assert started.wait(timeout=1)
    assert not completed.is_set()

    executor.join()
    assert completed.is_set()

    executor.shutdown()


def test_shutdown(mocker):
    mock_policy = mocker.MagicMock(spec=MultiCriterionPolicy)
    mock_policy.target_workers.return_value = 2

    executor = AdaptiveExecutor(max_workers=5, policy=mock_policy)

    executor.shutdown()
    assert executor.shutdown_flag is True

    executor.join()


@patch("adaptive_executor.executor.signal.signal")
def test_signal_handlers_registered(mock_signal, mocker):
    mock_policy = mocker.MagicMock(spec=MultiCriterionPolicy)
    mock_policy.target_workers.return_value = 2

    executor = AdaptiveExecutor(max_workers=5, policy=mock_policy)

    signals = [call.args[0] for call in mock_signal.call_args_list]

    assert signal.SIGINT in signals
    if hasattr(signal, "SIGTERM"):
        assert signal.SIGTERM in signals

    executor.shutdown()
    executor.join()


def test_controller_updates_limit(mocker):
    mock_policy = mocker.MagicMock(spec=MultiCriterionPolicy)
    mock_policy.target_workers.side_effect = [3, 5, 7]

    executor = AdaptiveExecutor(
        max_workers=10,
        policy=mock_policy,
        check_interval=0.05,
    )

    initial = executor.current_limit
    time.sleep(0.15)

    assert executor.current_limit != initial

    executor.shutdown()
    executor.join()


def test_task_with_kwargs(mocker):
    mock_policy = mocker.MagicMock(spec=MultiCriterionPolicy)
    mock_policy.target_workers.return_value = 2

    executor = AdaptiveExecutor(max_workers=5, policy=mock_policy)

    result = {}
    done = threading.Event()

    def task(key, value):
        result[key] = value
        done.set()

    executor.submit(task, key="test", value="success")

    assert done.wait(timeout=2)
    assert result["test"] == "success"

    executor.shutdown()
    executor.join()
