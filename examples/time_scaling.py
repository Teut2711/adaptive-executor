"""
Time-based Scaling Example
========================

This example demonstrates how to use TimeCriterion to scale workers based on time of day.
Perfect for applications that should be more aggressive during off-peak hours.
"""

from adaptive_executor import AdaptiveExecutor
from adaptive_executor.criteria import TimeCriterion


def main():
    # Create time-based criterion for night scaling
    # Scale to 8 workers between 10PM-3AM, 1 worker otherwise
    
    # Option 1: Using integers (simpler)
    night_criterion = TimeCriterion(
        workers=8,
        start_time=22,  # 10PM
        end_time=3,     # 3AM
        tz="America/New_York"
    )
    
    # Create executor with time-based scaling
    executor = AdaptiveExecutor(
        max_workers=10,
        policy=night_criterion,
        check_interval=30  # Check every 30 seconds
    )
    
    print("Time-based Scaling Example")
    print("=" * 40)
    print("Timezone: America/New_York")
    print("Active hours: " + str(night_criterion.time_start) + ":00 - " + str(night_criterion.time_end) + ":00")
    print("Workers during active hours: " + str(night_criterion.workers))
    print("Workers outside active hours: 1")
    print()
    
    # Submit some example tasks
    def process_task(task_id):
        import time
        time.sleep(1)
        print("Task " + str(task_id) + " completed with " + str(executor.current_workers) + " workers")
    
    print("Submitting tasks...")
    for i in range(5):
        executor.submit(process_task, i)
    
    # Let it run for a bit to show scaling
    print("Running for 10 seconds to demonstrate scaling...")
    import time
    time.sleep(10)
    
    print("\nShutting down...")
    executor.shutdown()


if __name__ == "__main__":
    main()
