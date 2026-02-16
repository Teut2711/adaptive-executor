"""
Resource-based Scaling Example
===========================

This example demonstrates how to use CpuCriterion and MemoryCriterion to scale workers
based on system resource usage. Perfect for resource-intensive applications.
"""

from adaptive_executor import AdaptiveExecutor, MultiCriterionPolicy
from adaptive_executor.criteria import CpuCriterion, MemoryCriterion, MultiCriterion
import random


def main():
    # Create resource-based criteria
    # Scale to 4 workers when CPU >= 80%
    cpu_criterion = CpuCriterion(threshold=80.0, workers=4)

    # Scale to 6 workers when memory >= 85%
    memory_criterion = MemoryCriterion(threshold=85.0, workers=6)

    # Combine criteria with OR logic (scale if either resource is high)
    resource_criterion = MultiCriterion(
        criteria=[(cpu_criterion, 4), (memory_criterion, 6)], logic="or"
    )
    resource_policy = MultiCriterionPolicy(criteria=[resource_criterion], hard_cap=8)

    # Create executor with resource-based scaling
    executor = AdaptiveExecutor(
        max_workers=8,
        policy=resource_policy,
        check_interval=15,  # Check every 15 seconds for resources
    )

    print("Resource-based Scaling Example")
    print("=" * 40)
    print(
        f"CPU threshold: {cpu_criterion.threshold}% -> {cpu_criterion.workers} workers"
    )
    print(
        f"Memory threshold: {memory_criterion.threshold}% -> {memory_criterion.workers} workers"
    )
    print(f"Logic: {resource_criterion.logic} (any condition met)")
    print()

    # Submit some CPU-intensive tasks
    def cpu_intensive_task(task_id):
        # Simulate CPU work
        for _ in range(1000000):
            _ = random.random() ** 2
        print(f"CPU task {task_id} completed with {executor.current_limit} workers")

    def memory_intensive_task(task_id):
        # Simulate memory work
        data = [random.random() for _ in range(100000)]
        _ = sum(data)
        print(
            f"Memory task {task_id} completed with {executor.current_limit} workers"
        )

    print("Submitting CPU and memory intensive tasks...")
    for i in range(3):
        executor.submit(cpu_intensive_task, f"cpu_{i}")
        executor.submit(memory_intensive_task, f"mem_{i}")

    executor.join()

    print("\nShutting down...")
    executor.shutdown()


if __name__ == "__main__":
    main()
