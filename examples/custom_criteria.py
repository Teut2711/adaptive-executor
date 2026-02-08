import time
import random
from adaptive_executor import AdaptiveExecutor, MultiCriterionPolicy
from adaptive_executor.criteria import ScalingCriterion


class LoadBasedCriterion(ScalingCriterion):
    """Custom scaling criterion based on current task load."""

    def __init__(self, low_threshold=5, high_threshold=15):
        self.low_threshold = low_threshold
        self.high_threshold = high_threshold
        self.pending_tasks = 0
        self.completed_tasks = 0

    def update_metrics(self, pending, completed):
        """Update internal metrics for scaling decisions."""
        self.pending_tasks = pending
        self.completed_tasks = completed

    def max_workers(self):
        """Calculate optimal workers based on current load."""
        if self.pending_tasks == 0:
            return 2  # Minimum workers when no work

        load_ratio = self.pending_tasks / max(self.completed_tasks, 1)

        if load_ratio > 3.0:  # High load
            return min(self.high_threshold, self.pending_tasks + 2)
        elif load_ratio > 1.5:  # Medium load
            return max(6, self.pending_tasks)
        else:  # Low load
            return max(3, self.low_threshold)


class TimeOfDayCriterion(ScalingCriterion):
    """Custom time-based criterion with more granular control."""

    def __init__(self, timezone="UTC"):
        from datetime import datetime
        import pytz

        self.tz = pytz.timezone(timezone)

    def max_workers(self):
        """Calculate optimal workers based on current load."""
        from datetime import datetime

        hour = datetime.now(self.tz).hour

        # More granular time-based scaling
        if 6 <= hour < 9:  # Early morning
            return 4
        elif 9 <= hour < 12:  # Late morning
            return 8
        elif 12 <= hour < 17:  # Afternoon
            return 12
        elif 17 <= hour < 21:  # Evening
            return 6
        else:  # Night
            return 3


def variable_task(task_id, complexity):
    """Task with variable complexity and duration."""
    print(f"Task {task_id} started (complexity: {complexity})")

    # Simulate work based on complexity
    work_units = complexity * 100
    for _ in range(work_units):
        _ = sum(range(10))
        time.sleep(0.01)

    print(f"Task {task_id} completed")
    return f"Task {task_id} result (complexity {complexity})"


def main():
    print("=== Custom Scaling Criteria Example ===")

    # Create custom criteria
    load_criterion = LoadBasedCriterion(low_threshold=4, high_threshold=12)

    time_criterion = TimeOfDayCriterion("America/New_York")

    # Combine custom criteria
    policy = MultiCriterionPolicy([load_criterion, time_criterion], hard_cap=15)

    executor = AdaptiveExecutor(
        max_workers=20, policy=policy, check_interval=20  # Check every 20 seconds
    )

    print(f"Initial worker limit: {executor.current_limit}")
    print("Using custom criteria: Load-based + Time-of-day")

    # Simulate variable workload
    tasks = []
    for i in range(20):
        complexity = random.choice([1, 2, 3, 4, 5])
        tasks.append((i, complexity))

        # Update load criterion metrics
        if i > 0:
            load_criterion.update_metrics(pending=len(tasks) - i, completed=i - 1)

    print(f"Submitting {len(tasks)} tasks with varying complexity...")

    start_time = time.time()

    # Submit tasks in batches to show scaling
    batch_size = 5
    for i in range(0, len(tasks), batch_size):
        batch = tasks[i : i + batch_size]
        print(f"\nSubmitting batch {i//batch_size + 1}: {len(batch)} tasks")

        for task_id, complexity in batch:
            executor.submit(variable_task, task_id, complexity)

        # Wait a bit to see scaling effect
        time.sleep(2)

        # Update load metrics
        load_criterion.update_metrics(
            pending=len(tasks) - i - batch_size, completed=i + batch_size
        )

    # Wait for completion
    executor.join()

    total_time = time.time() - start_time
    avg_complexity = sum(complexity for _, complexity in tasks) / len(tasks)

    print(f"\nAll tasks completed in {total_time:.2f} seconds")
    print(f"Average complexity: {avg_complexity:.1f}")
    print(f"Final worker limit: {executor.current_limit}")

    executor.shutdown()


if __name__ == "__main__":
    main()
