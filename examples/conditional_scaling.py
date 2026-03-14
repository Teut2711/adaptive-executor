"""
Conditional Scaling Example
========================

This example demonstrates ConditionalCriterion for applying different scaling
based on dynamic conditions.
"""

from datetime import time as dt_time

from adaptive_executor import AdaptiveExecutor, MultiCriterionPolicy
from adaptive_executor.criteria import (
    TimeCriterion,
    MemoryCriterion,
    ConditionalCriterion,
)


def main():
    # Create condition and action criteria
    # Condition: Check if memory usage is high
    memory_condition = MemoryCriterion(threshold=80.0, workers=2)

    # Action: Use time-based scaling when condition is met
    time_action = TimeCriterion(
        worker_count=4,
        active_start=dt_time(20, 0),
        active_end=dt_time(6, 0),
        timezone="UTC",
    )

    # Conditional criterion
    # If memory > 80%, use time-based scaling (4 workers)
    # Otherwise, use memory criterion behavior (2 workers)
    conditional_policy = ConditionalCriterion(
        condition_criterion=memory_condition, action_criterion=time_action, workers=4
    )
    policy = MultiCriterionPolicy(criteria=[conditional_policy], hard_cap=6)

    # Create executor with conditional scaling
    executor = AdaptiveExecutor(max_workers=6, policy=policy, check_interval=20)

    print("Conditional Scaling Example")
    print("=" * 40)
    print("Scenario: Dynamic scaling based on memory usage")
    print(f"Condition: Memory >= {memory_condition.threshold}%")
    print(
        f"If condition met: Use time-based scaling ({time_action.worker_count} workers)"
    )
    print(
        f"If condition not met: Use memory scaling ({memory_condition.workers} workers)"
    )
    print()

    # Submit tasks that demonstrate conditional behavior
    def conditional_task(task_id):
        current_workers = executor.current_limit

        if current_workers == 4:
            reason = "Memory high + time window active"
        elif current_workers == 2:
            reason = "Memory high but time window inactive"
        else:
            reason = "Memory normal, using fallback"

        print(f"Task {task_id}: {reason} (workers: {current_workers})")

    print("Submitting conditional tasks...")
    for i in range(6):
        executor.submit(conditional_task, i)

    executor.join()

    print("\nShutting down...")
    executor.shutdown()


if __name__ == "__main__":
    main()
