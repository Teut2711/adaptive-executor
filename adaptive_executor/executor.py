
import threading
import queue
import time
import signal


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
            print(f"\n[AdaptiveExecutor] Signal {signum} received")
            self.shutdown()

        signal.signal(signal.SIGINT, handler)
        signal.signal(signal.SIGTERM, handler)

    def _set_limit(self, new_limit):
        new_limit = min(new_limit, self.max_workers)
        diff = new_limit - self.current_limit

        if diff > 0:
            for _ in range(diff):
                self.permits.release()
        elif diff < 0:
            for _ in range(-diff):
                self.permits.acquire()

        self.current_limit = new_limit
        print(f"[AdaptiveExecutor] concurrency={self.current_limit}")

    def _controller(self):
        while not self.shutdown_flag:
            target = self.policy.target_workers()
            if target != self.current_limit:
                self._set_limit(target)
            time.sleep(self.check_interval)

    def _worker(self):
        while not self.shutdown_flag:
            try:
                fn, args, kwargs = self.tasks.get(timeout=1)
            except queue.Empty:
                continue

            with self.permits:
                try:
                    fn(*args, **kwargs)
                finally:
                    self.tasks.task_done()

    def submit(self, fn, *args, **kwargs):
        self.tasks.put((fn, args, kwargs))

    def join(self):
        self.tasks.join()

    def shutdown(self):
        self.shutdown_flag = True
