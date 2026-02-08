"""
Time-based Scaling Example
=========================

This example demonstrates how to use TimeCriterion to scale workers based on time of day.
Perfect for applications that should be more aggressive during off-peak hours.
"""

import datetime
from adaptive_executor import AdaptiveExecutor
from adaptive_executor.criteria import TimeCriterion

def main():
    # Example 1: Night shift in New York timezone (10PM-3AM)
    ny_shift_start = datetime.datetime(2024, 1, 1, 22, 0)  # 10PM
    ny_shift_end = datetime.datetime(2024, 1, 2, 3, 0)     # 3AM next day
    
    ny_policy = TimeCriterion(
        worker_count=8,
        active_start=ny_shift_start,
        active_end=ny_shift_end,
        timezone="America/New_York"
    )
    
    # Example 2: Day shift in India timezone (9AM-6PM)
    in_shift_start = datetime.datetime(2024, 1, 1, 9, 0)  # 9AM
    in_shift_end = datetime.datetime(2024, 1, 1, 18, 0)   # 6PM
    
    in_policy = TimeCriterion(
        worker_count=6,
        active_start=in_shift_start,
        active_end=in_shift_end,
        timezone="Asia/Kolkata"
    )
    
    # Create executors for both policies
    ny_executor = AdaptiveExecutor(
        max_workers=10,
        policy=ny_policy,
        check_interval=30
    )
    
    
    # Print configuration
    print("Time-based Scaling Examples")
    print("=" * 40)
    
    print("\nNew York Office (Night Shift):")
    print("-" * 30)
    print("Timezone: America/New_York")
    print(f"Active window: {ny_shift_start.strftime('%H:%M')} - {ny_shift_end.strftime('%H:%M')} (next day)")
    print(f"Workers during active window: {ny_policy.worker_count}")
    print("Workers outside active window: 1")
    
    print("\nIndia Office (Day Shift):")
    print("-" * 30)
    print("Timezone: Asia/Kolkata")
    print(f"Active window: {in_shift_start.strftime('%H:%M')} - {in_shift_end.strftime('%H:%M')}")
    print(f"Workers during active window: {in_policy.worker_count}")
    print("Workers outside active window: 1")
    print()
    
    # Example of how to use the executors
    def process_task(executor_name, task_id):
        import time
        time.sleep(1)
        print(f"{executor_name} - Task {task_id} completed with {executor.current_workers} workers")
    
    # Use ny_executor for demonstration
    executor = ny_executor
    
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
