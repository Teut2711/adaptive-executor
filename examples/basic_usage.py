"""Basic usage example for adaptive-executor with enhanced logging."""
import logging
import time
from datetime import datetime

from adaptive_executor import (
    AdaptiveExecutor,
    TimeCriterion,
    MultiCriterionPolicy,
    setup_logger,
)

# Configure logging for the example
setup_logger(level=logging.DEBUG)
logger = logging.getLogger("example.basic_usage")


def simple_task(task_id):
    """A simple task that simulates work."""
    logger.debug("Processing task %s", task_id)
    time.sleep(1)
    return f"Completed task {task_id}"


def main():
    """Main function demonstrating basic usage of the adaptive executor."""
    logger.info("Starting basic usage example")
    
    try:
        # Create time-based criteria for different times of day
        logger.debug("Creating time-based criteria")
        day_criterion = TimeCriterion(
            worker_count=8,  # More workers during the day
            active_start=datetime(2026, 1, 8, 22, 0),  # 9 AM
            active_end=datetime(2026, 1, 8, 23, 0),  # 5 PM
            timezone="Asia/Kolkata"
        )
        logger.debug("Created day criterion: %s", day_criterion)
        
        night_criterion = TimeCriterion(
            worker_count=2,  # Fewer workers at night
            active_start=datetime(2026, 1, 9, 22, 0),  # 5 PM
            active_end=datetime(2026, 1, 9, 23, 0),  # 9 AM
            timezone="Asia/Kolkata"
        )
        logger.debug("Created night criterion: %s", night_criterion)

        # Create a policy that combines the criteria
        logger.debug("Creating MultiCriterionPolicy")
        policy = MultiCriterionPolicy(
            criteria=[day_criterion, night_criterion],
            hard_cap=10
        )
        logger.info("Policy created: %s", policy)

        # Create the executor with our policy
        logger.debug("Creating AdaptiveExecutor with max_workers=10, check_interval=5")
        executor = AdaptiveExecutor(
            max_workers=10,
            policy=policy,
            check_interval=5  # Check every 5 seconds
        )
        logger.info("Executor created and running")

        # Submit some tasks
        logger.info("Submitting tasks...")
        tasks = []
        for i in range(5):
            task = executor.submit(simple_task, i)
            tasks.append(task)
            logger.debug("Submitted task %d", i)
        
        # Wait for tasks to complete
        logger.info("Waiting for tasks to complete...")
        for i, task in enumerate(tasks):
            try:
                result = task.result()
                logger.info("Task %d completed: %s", i, result)
            except Exception as e:
                logger.error("Task %d failed: %s", i, str(e), exc_info=True)
        
        logger.info("All tasks completed! Current worker limit: %d", 
                   executor.current_limit)
        
        # Clean up
        logger.debug("Shutting down executor")
        executor.shutdown()
        return 0
    except Exception as e:
        logger.critical("Error in main execution: %s", str(e), exc_info=True)
        return 1


if __name__ == "__main__":
    try:
        exit_code = main()
        exit(exit_code)
    except KeyboardInterrupt:
        logger.info("Example interrupted by user")
        exit(1)
    except Exception as e:
        logger.critical("Unexpected error: %s", str(e), exc_info=True)
        exit(1)
