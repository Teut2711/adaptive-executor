"""Adaptive executor implementation with dynamic worker scaling."""

import queue
import signal
import threading
import time
from typing import Callable

from .utils import get_logger

logger = get_logger(__name__)


class AdaptiveExecutor:
    def __init__(self, max_workers, policy, check_interval=60):
        self.max_workers = max_workers
        self.policy = policy
        self.check_interval = check_interval

        self.tasks = queue.Queue()
        self.shutdown_flag = False

        self.permits = threading.Semaphore(0)
        self.current_limit = 0

        self._set_limit(self.policy.target_workers())

        for _ in range(max_workers):
            threading.Thread(target=self._worker, daemon=True).start()

        threading.Thread(target=self._controller, daemon=True).start()

        self._register_signal_handlers()

    def _register_signal_handlers(self):
        def handler(signum, frame):
            signame = (
                signal.Signals(signum).name
                if hasattr(signal, "Signals")
                else str(signum)
            )
            logger.info("Received signal %s, shutting down...", signame)
            self.shutdown()

        # Register SIGINT (available on all platforms)
        try:
            signal.signal(signal.SIGINT, handler)
            logger.debug("Registered signal handler for SIGINT")
        except (ValueError, AttributeError) as e:
            logger.warning("Failed to register signal handler for SIGINT: %s", e)

        # Register SIGTERM (not available on Windows)
        if hasattr(signal, "SIGTERM"):
            try:
                signal.signal(signal.SIGTERM, handler)
                logger.debug("Registered signal handler for SIGTERM")
            except (ValueError, AttributeError) as e:
                logger.warning("Failed to register signal handler for SIGTERM: %s", e)

    def _set_limit(self, new_limit):
        new_limit = min(new_limit, self.max_workers)
        diff = new_limit - self.current_limit

        if diff > 0:
            for _ in range(diff):
                self.permits.release()
        elif diff < 0:
            for _ in range(-diff):
                self.permits.acquire()

        old_limit = self.current_limit
        self.current_limit = new_limit
        if old_limit != new_limit:
            logger.info(
                "Adjusted worker concurrency: %d -> %d (max: %d)",
                old_limit,
                new_limit,
                self.max_workers,
            )

    def _controller(self):
        while not self.shutdown_flag:
            target = self.policy.target_workers()
            if target != self.current_limit:
                self._set_limit(target)
            time.sleep(self.check_interval)

    def _worker(self):
        thread_name = threading.current_thread().name
        logger.debug("Worker %s started", thread_name)

        while not self.shutdown_flag:
            try:
                fn, args, kwargs = self.tasks.get(timeout=1)
                task_name = fn.__name__ if hasattr(fn, "__name__") else "anonymous"
                logger.debug("Worker %s starting task: %s", thread_name, task_name)

                try:
                    # Acquire a permit so active task concurrency follows current_limit.
                    self.permits.acquire()
                    start_time = time.monotonic()
                    fn(*args, **kwargs)
                    duration = time.monotonic() - start_time

                    logger.debug(
                        "Worker %s completed task %s in %.3f seconds",
                        thread_name,
                        task_name,
                        duration,
                    )
                except Exception as e:
                    logger.error(
                        "Error in worker %s while executing task %s: %s",
                        thread_name,
                        task_name,
                        str(e),
                        exc_info=True,
                    )
                    raise
                finally:
                    self.permits.release()
                    self.tasks.task_done()

            except queue.Empty:
                continue

        logger.debug("Worker %s shutting down", thread_name)

    def submit(self, fn: Callable, *args, **kwargs) -> None:
        """Submit a task to be executed by the worker pool.

        Args:
            fn: The function to execute
            *args: Positional arguments to pass to the function
            **kwargs: Keyword arguments to pass to the function
        """
        task_name = fn.__name__ if hasattr(fn, "__name__") else "anonymous"
        logger.debug("Submitting task: %s", task_name)
        self.tasks.put((fn, args, kwargs))
        logger.debug(
            "Task %s submitted to queue (queue size: %d)", task_name, self.tasks.qsize()
        )

    def join(self, timeout: float = None) -> bool:
        """Wait until all tasks in the queue are processed.

        Args:
            timeout: Maximum time to wait in seconds

        Returns:
            bool: True if all tasks completed, False if timed out
        """
        logger.info("Waiting for all tasks to complete...")
        try:
            if timeout is not None:
                # Use unfinished_tasks so we wait for execution completion,
                # not just for the queue to be dequeued.
                end_time = time.monotonic() + timeout
                while self.tasks.unfinished_tasks > 0 and time.monotonic() < end_time:
                    time.sleep(0.1)
                return self.tasks.unfinished_tasks == 0
            else:
                self.tasks.join()
                return True
        except KeyboardInterrupt:
            logger.warning("Join interrupted by user")
            return False

    def shutdown(self) -> None:
        """Shut down the executor and all worker threads."""
        if self.shutdown_flag:
            return

        logger.info("Shutting down executor...")
        self.shutdown_flag = True

        # Clear any pending tasks
        while not self.tasks.empty():
            try:
                self.tasks.get_nowait()
                self.tasks.task_done()
            except queue.Empty:
                break

        logger.debug("Executor shutdown complete")
