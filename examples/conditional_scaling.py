"""
Conditional Scaling Example
========================

This example demonstrates ConditionalCriterion for applying different scaling
based on dynamic conditions.
"""

from adaptive_executor import AdaptiveExecutor
from adaptive_executor.criteria import TimeCriterion, MemoryCriterion, ConditionalCriterion


def main():
    # Create condition and action criteria
    # Condition: Check if memory usage is high
    memory_condition = MemoryCriterion(threshold=80.0, workers=2)
    
    # Action: Use time-based scaling when condition is met
    time_action = TimeCriterion(
        workers=4,
        time_start=20,  # 8PM
        time_end=6,     # 6AM
        tz="UTC"
    )
    
    # Conditional criterion
    # If memory > 80%, use time-based scaling (4 workers)
    # Otherwise, use memory criterion behavior (2 workers)
    conditional_policy = ConditionalCriterion(
        condition_criterion=memory_condition,
        action_criterion=time_action,
        workers=4
    )
    
    # Create executor with conditional scaling
    executor = AdaptiveExecutor(
        max_workers=6,
        policy=conditional_policy,
        check_interval=20
    )
    
    print("Conditional Scaling Example")
    print("=" * 40)
    print("Scenario: Dynamic scaling based on memory usage")
    print(f"Condition: Memory >= {memory_condition.threshold}%")
    print(f"If condition met: Use time-based scaling ({time_action.workers} workers)")
    print(f"If condition not met: Use memory scaling ({memory_condition.workers} workers)")
    print()
    
    # Submit tasks that demonstrate conditional behavior
    def conditional_task(task_id):
        current_workers = executor.current_workers
        
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
    
    # Run to see different conditional behaviors
    print("Running for 25 seconds to demonstrate conditional scaling...")
    import time
    time.sleep(25)
    
    print("\nShutting down...")
    executor.shutdown()


if __name__ == "__main__":
    main()
