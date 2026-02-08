"""
Complex Scaling Example
====================

This example demonstrates advanced scaling with MultiCriterion using AND logic.
Perfect for applications that need multiple conditions to be met simultaneously.
"""

from adaptive_executor import AdaptiveExecutor
from adaptive_executor.criteria import TimeCriterion, MemoryCriterion, MultiCriterion


def main():
    # Create criteria for complex logic
    # Time criterion: 10PM-3AM window
    time_criterion = TimeCriterion(
        workers=2, time_start=22, time_end=3, tz="UTC"  # 10PM  # 3AM
    )

    # Memory criterion: >80% usage
    memory_criterion = MemoryCriterion(threshold=80.0, workers=2)

    # Multi-criterion with AND logic
    # BOTH time window AND memory threshold must be met to scale to 2 workers
    complex_policy = MultiCriterion(
        criteria=[(time_criterion, 2), (memory_criterion, 2)], logic="and"
    )

    # Create executor with complex scaling
    executor = AdaptiveExecutor(
        max_workers=6,
        policy=complex_policy,
        check_interval=10,  # Check frequently for complex conditions
    )

    print("Complex Scaling Example")
    print("=" * 40)
    print("Scenario: Scale to 2 workers ONLY when:")
    print(
        f"1. Time is between {time_criterion.time_start}:00-{time_criterion.time_end}:00"
    )
    print(f"2. Memory usage >= {memory_criterion.threshold}%")
    print(f"3. Logic: {complex_policy.logic} (all conditions must be met)")
    print()

    # Submit tasks that work differently based on conditions
    def adaptive_task(task_id):
        current_workers = executor.current_workers

        if current_workers == 2:
            task_type = "HIGH-PRIORITY (complex conditions met)"
        else:
            task_type = "NORMAL-PRIORITY (using fallback)"

        print(f"Task {task_id}: {task_type} (workers: {current_workers})")

    print("Submitting adaptive tasks...")
    for i in range(8):
        executor.submit(adaptive_task, i)

    # Run long enough to see different scaling behaviors
    print("Running for 30 seconds to demonstrate complex scaling...")
    import time

    time.sleep(30)

    print("\nShutting down...")
    executor.shutdown()


if __name__ == "__main__":
    main()
