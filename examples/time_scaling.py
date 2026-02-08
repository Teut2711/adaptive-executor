"""
Time-based Scaling Example
=========================

This example demonstrates how to use TimeCriterion to scale workers based on time of day.
Perfect for applications that should be more aggressive during off-peak hours.
"""

import datetime
import logging
from datetime import time as dt_time

from adaptive_executor import (
    AdaptiveExecutor,
    TimeCriterion,
    MultiCriterionPolicy,
    setup_logger,
)

# Configure logging for the example
setup_logger(level=logging.DEBUG)
logger = logging.getLogger("example.time_scaling")

def process_task(task_id: int, executor_name: str):
    """Simulate a task that runs for some time."""
    logger.debug("Starting task %d for %s", task_id, executor_name)
    start_time = datetime.datetime.now()
    
    try:
        # Simulate work
        import time
        time.sleep(2)  # Simulate 2 seconds of work
        
        duration = (datetime.datetime.now() - start_time).total_seconds()
        logger.info("Task %d completed in %.2f seconds", task_id, duration)
        return f"Task {task_id} completed by {executor_name}"
    except Exception as e:
        logger.error("Task %d failed: %s", task_id, str(e), exc_info=True)
        raise

def main():
    """Demonstrate time-based scaling with different timezones."""
    logger.info("Starting time-based scaling example")
    
    try:
        # Example 1: Night shift in New York timezone (10PM-3AM)
        logger.debug("Creating New York night shift policy")
        ny_shift_start = dt_time(22, 0)  # 10PM
        ny_shift_end = dt_time(3, 0)     # 3AM next day
        
        ny_policy = TimeCriterion(
            worker_count=8,
            active_start=ny_shift_start,
            active_end=ny_shift_end,
            timezone="America/New_York"
        )
        logger.debug("Created NY policy: %s", ny_policy)
        
        # Example 2: Day shift in India timezone (9AM-6PM)
        logger.debug("Creating India day shift policy")
        in_shift_start = dt_time(9, 0)   # 9AM
        in_shift_end = dt_time(18, 0)    # 6PM
        
        in_policy = TimeCriterion(
            worker_count=6,
            active_start=in_shift_start,
            active_end=in_shift_end,
            timezone="Asia/Kolkata"
        )
        logger.debug("Created India policy: %s", in_policy)
        
        # Create a combined policy
        combined_policy = MultiCriterionPolicy(
            criteria=[ny_policy, in_policy],
            hard_cap=10
        )
        
        # Create executor with the combined policy
        logger.info("Creating executor with combined time-based policies")
        executor = AdaptiveExecutor(
            max_workers=10,
            policy=combined_policy,
            check_interval=5  # Check every 5 seconds
        )
        
        # Log configuration
        logger.info("\nTime-based Scaling Examples")
        logger.info("=" * 40)
        
        logger.info("\nNew York Office (Night Shift):")
        logger.info("-" * 30)
        logger.info("Timezone: America/New_York")
        logger.info("Active window: %s - %s (next day)", 
                   ny_shift_start.strftime('%H:%M'), 
                   ny_shift_end.strftime('%H:%M'))
        logger.info("Workers during active window: %d", ny_policy.worker_count)
        
        logger.info("\nIndia Office (Day Shift):")
        logger.info("-" * 30)
        logger.info("Timezone: Asia/Kolkata")
        logger.info("Active window: %s - %s", 
                   in_shift_start.strftime('%H:%M'), 
                   in_shift_end.strftime('%H:%M'))
        logger.info("Workers during active window: %d\n", in_policy.worker_count)
        
        # Submit tasks to the executor
        logger.info("Submitting tasks...")
        tasks = []
        for i in range(5):
            task = executor.submit(process_task, i, "time_scaling")
            tasks.append(task)
            logger.debug("Submitted task %d", i)
        
        # Monitor task completion
        logger.info("Monitoring tasks for 30 seconds (press Ctrl+C to exit early)...")
        start_time = datetime.datetime.now()
        
        try:
            while (datetime.datetime.now() - start_time).total_seconds() < 30:
                completed = sum(1 for t in tasks if t.done())
                logger.info("Progress: %d/%d tasks completed", completed, len(tasks))
                
                if completed == len(tasks):
                    logger.info("All tasks completed!")
                    break
                    
                time.sleep(5)  # Check every 5 seconds
                
        except KeyboardInterrupt:
            logger.info("\nReceived keyboard interrupt, shutting down...")
        
        # Log final status
        logger.info("\nFinal worker limit: %d", executor.current_limit)
        logger.info("Shutting down executor...")
        
        return 0
        
    except Exception as e:
        logger.critical("Error in time scaling example: %s", str(e), exc_info=True)
        return 1


if __name__ == "__main__":
    try:
        import time
        exit_code = main()
        exit(exit_code)
    except KeyboardInterrupt:
        logger.info("Example interrupted by user")
        exit(1)
    except Exception as e:
        logger.critical("Unexpected error: %s", str(e), exc_info=True)
        exit(1)
