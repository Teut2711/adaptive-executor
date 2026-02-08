from adaptive_executor import AdaptiveExecutor, MultiCriterionPolicy
from adaptive_executor.criteria import TimeCriterion, CpuCriterion
import time

def simple_task(task_id):
    print(f"Processing task {task_id}")
    time.sleep(1)
    return f"Completed task {task_id}"

def main():
    print("=== Adaptive Executor Basic Usage Example ===")
    
    # Create scaling criteria
    time_policy = TimeCriterion(
        day_workers=2,      # Conservative during day
        night_workers=8,      # More workers at night
        night_start=22,       # 10 PM
        night_end=6,          # 6 AM
        tz="UTC"
    )
    
    cpu_policy = CpuCriterion(threshold=75)
    
    # Combine criteria with policy
    policy = MultiCriterionPolicy(
        [time_policy, cpu_policy],
        hard_cap=10
    )
    
    # Create executor
    executor = AdaptiveExecutor(
        max_workers=15,
        policy=policy,
        check_interval=30  # Check every 30 seconds
    )
    
    print(f"Initial worker limit: {executor.current_limit}")
    print("Submitting 10 tasks...")
    
    # Submit tasks
    for i in range(10):
        executor.submit(simple_task, i)
    
    # Wait for completion
    print("Waiting for tasks to complete...")
    executor.join()
    
    print("All tasks completed!")
    executor.shutdown()

if __name__ == "__main__":
    main()
