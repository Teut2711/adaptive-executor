import time
import threading
import signal
from unittest.mock import MagicMock, patch

from adaptive_executor.executor import AdaptiveExecutor
from adaptive_executor.policies import MultiCriterionPolicy


class TestAdaptiveExecutor:
    def test_initialization(self):
        mock_policy = MagicMock(spec=MultiCriterionPolicy)
        mock_policy.target_workers.return_value = 5

        executor = AdaptiveExecutor(max_workers=10, policy=mock_policy)

        try:
            assert executor.max_workers == 10
            assert executor.policy == mock_policy
            assert executor.check_interval == 60
            assert executor.current_limit == 5
            assert executor.shutdown_flag is False
        finally:
            executor.shutdown()
            executor.join()

    def test_initialization_with_custom_check_interval(self):
        mock_policy = MagicMock(spec=MultiCriterionPolicy)
        mock_policy.target_workers.return_value = 3

        executor = AdaptiveExecutor(
            max_workers=8, policy=mock_policy, check_interval=30
        )

        try:
            assert executor.check_interval == 30
        finally:
            executor.shutdown()
            executor.join()

    def test_set_limit_increase(self):
        mock_policy = MagicMock(spec=MultiCriterionPolicy)
        mock_policy.target_workers.return_value = 3

        executor = AdaptiveExecutor(max_workers=10, policy=mock_policy)

        try:
            executor._set_limit(7)
            assert executor.current_limit == 7
        finally:
            executor.shutdown()
            executor.join()

    def test_set_limit_decrease(self):
        mock_policy = MagicMock(spec=MultiCriterionPolicy)
        mock_policy.target_workers.return_value = 7

        executor = AdaptiveExecutor(max_workers=10, policy=mock_policy)

        try:
            executor._set_limit(3)
            assert executor.current_limit == 3
        finally:
            executor.shutdown()
            executor.join()

    def test_set_limit_respects_max_workers(self):
        mock_policy = MagicMock(spec=MultiCriterionPolicy)
        mock_policy.target_workers.return_value = 5

        executor = AdaptiveExecutor(max_workers=10, policy=mock_policy)

        try:
            executor._set_limit(15)
            assert executor.current_limit == 10
        finally:
            executor.shutdown()
            executor.join()

    def test_submit_task(self):
        mock_policy = MagicMock(spec=MultiCriterionPolicy)
        mock_policy.target_workers.return_value = 2

        executor = AdaptiveExecutor(max_workers=5, policy=mock_policy)

        try:
            task_executed = threading.Event()

            def test_task():
                task_executed.set()

            executor.submit(test_task)

            # Wait for task to complete with timeout
            assert task_executed.wait(timeout=2), "Task did not execute within timeout"
        finally:
            executor.shutdown()
            executor.join()

    def test_submit_multiple_tasks(self):
        mock_policy = MagicMock(spec=MultiCriterionPolicy)
        mock_policy.target_workers.return_value = 3

        executor = AdaptiveExecutor(max_workers=5, policy=mock_policy)

        try:
            executed_tasks = []
            lock = threading.Lock()

            def test_task(task_id):
                with lock:
                    executed_tasks.append(task_id)

            for i in range(3):
                executor.submit(test_task, i)

            # Wait for all tasks to complete
            timeout = time.time() + 2
            while True:
                with lock:
                    if len(executed_tasks) >= 3:
                        break
                if time.time() > timeout:
                    break
                time.sleep(0.1)

            with lock:
                assert len(executed_tasks) == 3
                assert set(executed_tasks) == {0, 1, 2}
        finally:
            executor.shutdown()
            executor.join()

    def test_join_waits_for_tasks(self):
        mock_policy = MagicMock(spec=MultiCriterionPolicy)
        mock_policy.target_workers.return_value = 2

        executor = AdaptiveExecutor(max_workers=5, policy=mock_policy)

        try:
            task_started = threading.Event()
            task_completed = threading.Event()

            def slow_task():
                task_started.set()
                time.sleep(0.5)
                task_completed.set()

            executor.submit(slow_task)

            # Wait for task to start
            assert task_started.wait(timeout=1), "Task did not start within timeout"

            # Task should not be completed yet
            assert not task_completed.is_set()

            # Join should wait for task completion
            executor.join()

            assert task_completed.is_set()
        finally:
            executor.shutdown()
            executor.join()

    def test_shutdown(self):
        mock_policy = MagicMock(spec=MultiCriterionPolicy)
        mock_policy.target_workers.return_value = 2

        executor = AdaptiveExecutor(max_workers=5, policy=mock_policy)

        try:
            assert executor.shutdown_flag is False

            executor.shutdown()

            assert executor.shutdown_flag is True
        finally:
            # Ensure cleanup even if shutdown() was already called
            executor.join()

    @patch("adaptive_executor.executor.signal.signal")
    def test_signal_handlers_registered(self, mock_signal):
        mock_policy = MagicMock(spec=MultiCriterionPolicy)
        mock_policy.target_workers.return_value = 2
        
        executor = AdaptiveExecutor(max_workers=5, policy=mock_policy)
        
        try:
            # Check that SIGINT was registered (available on all platforms)
            assert mock_signal.call_count >= 1
            assert any(
                call_args[0][0] == signal.SIGINT
                for call_args in mock_signal.call_args_list
            ), "Signal SIGINT not found in calls"
            
            # Check that SIGTERM was registered if available (not on Windows)
            if hasattr(signal, 'SIGTERM'):
                assert mock_signal.call_count >= 2
                assert any(
                    call_args[0][0] == signal.SIGTERM
                    for call_args in mock_signal.call_args_list
                ), "Signal SIGTERM not found in calls"
        finally:
            executor.shutdown()
            executor.join()

    def test_controller_updates_limit(self):
        mock_policy = MagicMock(spec=MultiCriterionPolicy)
        mock_policy.target_workers.side_effect = [3, 5, 7]

        executor = AdaptiveExecutor(
            max_workers=10, policy=mock_policy, check_interval=0.1
        )

        try:
            initial_limit = executor.current_limit

            # Wait for at least one controller update
            time.sleep(0.25)

            # The limit should have changed from the initial value
            assert executor.current_limit != initial_limit
        finally:
            executor.shutdown()
            executor.join()

    def test_task_with_kwargs(self):
        mock_policy = MagicMock(spec=MultiCriterionPolicy)
        mock_policy.target_workers.return_value = 2

        executor = AdaptiveExecutor(max_workers=5, policy=mock_policy)

        try:
            result = {}
            lock = threading.Lock()
            task_done = threading.Event()

            def test_task(key, value):
                with lock:
                    result[key] = value
                task_done.set()

            executor.submit(test_task, key="test", value="success")

            # Wait for task to complete
            assert task_done.wait(timeout=2), "Task did not complete within timeout"

            with lock:
                assert result["test"] == "success"
        finally:
            executor.shutdown()
            executor.join()
