import time
import random
from datetime import time as dt_time

from adaptive_executor import AdaptiveExecutor, MultiCriterionPolicy
from adaptive_executor.criteria import TimeCriterion, CpuCriterion, MemoryCriterion


def background_task(task_id, duration):
    """Simulate a background task with variable workload."""
    print(f"Task {task_id} started (duration: {duration:.1f}s)")

    # Simulate mixed workload
    for i in range(int(duration * 10)):
        # CPU work
        _ = sum(range(50))
        time.sleep(0.1)

    print(f"Task {task_id} completed")
    return f"Task {task_id} result"


def main():
    print("=== Multi-Criteria Scaling Example ===")

    # Create multiple scaling criteria
    time_policy = TimeCriterion(
        worker_count=12,  # More workers at night
        active_start=dt_time(20, 0),  # 8 PM to 6 AM
        active_end=dt_time(6, 0),
        timezone="UTC",
    )

    cpu_policy = CpuCriterion(threshold=75, workers=3)
    memory_policy = MemoryCriterion(threshold=80, workers=3)

    # Combine all criteria
    policy = MultiCriterionPolicy([time_policy, cpu_policy, memory_policy], hard_cap=15)

    executor = AdaptiveExecutor(
        max_workers=20, policy=policy, check_interval=45  # Check every 45 seconds
    )

    print(f"Initial worker limit: {executor.current_limit}")
    print("Policy combines: Time + CPU + Memory criteria")

    # Generate tasks with varying workloads
    tasks = []
    for i in range(15):
        duration = random.uniform(1.0, 5.0)
        tasks.append((i, duration))

    print(f"Submitting {len(tasks)} tasks with varying workloads...")

    start_time = time.time()

    # Submit tasks
    for task_id, duration in tasks:
        executor.submit(background_task, task_id, duration)

    # Monitor scaling during execution
    print("\nMonitoring worker scaling:")
    for _ in range(3):
        time.sleep(2)
        print(f"  Current workers: {executor.current_limit}")

    # Wait for completion
    print("\nWaiting for all tasks to complete...")
    executor.join()

    total_time = time.time() - start_time
    avg_task_time = sum(duration for _, duration in tasks) / len(tasks)

    print(f"\nAll tasks completed in {total_time:.2f} seconds")
    print(f"Average task duration: {avg_task_time:.2f}s")
    print(f"Final worker limit: {executor.current_limit}")

    executor.shutdown()


if __name__ == "__main__":
    main()
