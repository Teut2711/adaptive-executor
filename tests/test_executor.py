import time
import threading
import signal
from unittest.mock import MagicMock, patch, ANY, call

from adaptive_executor.executor import AdaptiveExecutor
from adaptive_executor.policies import MultiCriterionPolicy


class TestAdaptiveExecutor:
    def test_initialization(self):
        mock_policy = MagicMock(spec=MultiCriterionPolicy)
        mock_policy.target_workers.return_value = 5
        
        executor = AdaptiveExecutor(max_workers=10, policy=mock_policy)
        
        assert executor.max_workers == 10
        assert executor.policy == mock_policy
        assert executor.check_interval == 60
        assert executor.current_limit == 5
        assert executor.shutdown_flag is False

    def test_initialization_with_custom_check_interval(self):
        mock_policy = MagicMock(spec=MultiCriterionPolicy)
        mock_policy.target_workers.return_value = 3
        
        executor = AdaptiveExecutor(max_workers=8, policy=mock_policy, check_interval=30)
        
        assert executor.check_interval == 30

    def test_set_limit_increase(self):
        mock_policy = MagicMock(spec=MultiCriterionPolicy)
        mock_policy.target_workers.return_value = 3
        
        executor = AdaptiveExecutor(max_workers=10, policy=mock_policy)
        executor._set_limit(7)
        
        assert executor.current_limit == 7

    def test_set_limit_decrease(self):
        mock_policy = MagicMock(spec=MultiCriterionPolicy)
        mock_policy.target_workers.return_value = 7
        
        executor = AdaptiveExecutor(max_workers=10, policy=mock_policy)
        executor._set_limit(3)
        
        assert executor.current_limit == 3

    def test_set_limit_respects_max_workers(self):
        mock_policy = MagicMock(spec=MultiCriterionPolicy)
        mock_policy.target_workers.return_value = 5
        
        executor = AdaptiveExecutor(max_workers=10, policy=mock_policy)
        executor._set_limit(15)
        
        assert executor.current_limit == 10

    def test_submit_task(self):
        mock_policy = MagicMock(spec=MultiCriterionPolicy)
        mock_policy.target_workers.return_value = 2
        
        executor = AdaptiveExecutor(max_workers=5, policy=mock_policy)
        
        task_executed = threading.Event()
        
        def test_task():
            task_executed.set()
        
        executor.submit(test_task)
        
        timeout = time.time() + 2
        while not task_executed.is_set() and time.time() < timeout:
            time.sleep(0.1)
        
        assert task_executed.is_set()

    def test_submit_multiple_tasks(self):
        mock_policy = MagicMock(spec=MultiCriterionPolicy)
        mock_policy.target_workers.return_value = 3
        
        executor = AdaptiveExecutor(max_workers=5, policy=mock_policy)
        
        executed_tasks = []
        
        def test_task(task_id):
            executed_tasks.append(task_id)
        
        for i in range(3):
            executor.submit(test_task, i)
        
        timeout = time.time() + 2
        while len(executed_tasks) < 3 and time.time() < timeout:
            time.sleep(0.1)
        
        assert len(executed_tasks) == 3
        assert set(executed_tasks) == {0, 1, 2}

    def test_join_waits_for_tasks(self):
        mock_policy = MagicMock(spec=MultiCriterionPolicy)
        mock_policy.target_workers.return_value = 2
        
        executor = AdaptiveExecutor(max_workers=5, policy=mock_policy)
        
        task_started = threading.Event()
        task_completed = threading.Event()
        
        def slow_task():
            task_started.set()
            time.sleep(0.5)
            task_completed.set()
        
        executor.submit(slow_task)
        
        assert not task_started.is_set()
        
        timeout = time.time() + 1
        while not task_started.is_set() and time.time() < timeout:
            time.sleep(0.1)
        
        assert task_started.is_set()
        assert not task_completed.is_set()
        
        executor.join()
        
        assert task_completed.is_set()

    def test_shutdown(self):
        mock_policy = MagicMock(spec=MultiCriterionPolicy)
        mock_policy.target_workers.return_value = 2
        
        executor = AdaptiveExecutor(max_workers=5, policy=mock_policy)
        
        assert executor.shutdown_flag is False
        
        executor.shutdown()
        
        assert executor.shutdown_flag is True

    @patch('adaptive_executor.executor.signal.signal')
    def test_signal_handlers_registered(self, mock_signal):
        mock_policy = MagicMock(spec=MultiCriterionPolicy)
        mock_policy.target_workers.return_value = 2
        
        AdaptiveExecutor(max_workers=5, policy=mock_policy)
        
        assert mock_signal.call_count == 2
        
        # Check that signal was called with SIGINT and SIGTERM
        expected_signals = [signal.SIGINT, signal.SIGTERM]
        actual_signals = [call_args[0][0] for call_args in mock_signal.call_args_list]
        
        for expected_signal in expected_signals:
            assert expected_signal in actual_signals, \
                f"Signal {expected_signal} not found in {actual_signals}"

    def test_controller_updates_limit(self):
        mock_policy = MagicMock(spec=MultiCriterionPolicy)
        mock_policy.target_workers.side_effect = [3, 5, 7]
        
        executor = AdaptiveExecutor(max_workers=10, policy=mock_policy, check_interval=0.1)
        
        initial_limit = executor.current_limit
        
        time.sleep(0.15)
        
        assert executor.current_limit != initial_limit

    def test_task_with_kwargs(self):
        mock_policy = MagicMock(spec=MultiCriterionPolicy)
        mock_policy.target_workers.return_value = 2
        
        executor = AdaptiveExecutor(max_workers=5, policy=mock_policy)
        
        result = {}
        
        def test_task(key, value):
            result[key] = value
        
        executor.submit(test_task, key="test", value="success")
        
        timeout = time.time() + 2
        while "test" not in result and time.time() < timeout:
            time.sleep(0.1)
        
        assert result["test"] == "success"