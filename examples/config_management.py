"""
Configuration Management Example
=============================

This example demonstrates how to save and load scaling criteria configurations
using JSON serialization. Perfect for production deployments.
"""

import json
from pathlib import Path
from adaptive_executor import AdaptiveExecutor
from adaptive_executor.criteria import TimeCriterion, CpuCriterion, MemoryCriterion


def save_configuration(criteria, config_file):
    """Save criteria configuration to JSON file"""
    config = {
        "criteria": [criterion.to_dict() for criterion in criteria],
        "metadata": {
            "version": "1.0",
            "created_at": "2024-01-01T00:00:00Z"
        }
    }
    
    with open(config_file, 'w') as f:
        json.dump(config, f, indent=2)
    
    print(f"Configuration saved to {config_file}")


def load_configuration(config_file):
    """Load criteria configuration from JSON file"""
    with open(config_file, 'r') as f:
        config = json.load(f)
    
    # Recreate criteria from saved configuration
    criteria = []
    for criterion_data in config["criteria"]:
        criterion_type = criterion_data["type"]
        
        if criterion_type == "TimeCriterion":
            criterion = TimeCriterion.from_dict(criterion_data)
        elif criterion_type == "CpuCriterion":
            criterion = CpuCriterion.from_dict(criterion_data)
        elif criterion_type == "MemoryCriterion":
            criterion = MemoryCriterion.from_dict(criterion_data)
        else:
            raise ValueError(f"Unknown criterion type: {criterion_type}")
        
        criteria.append(criterion)
    
    print(f"Configuration loaded from {config_file}")
    return criteria


def main():
    config_file = "scaling_config.json"
    
    # Define criteria for configuration
    time_criterion = TimeCriterion(
        workers=8,
        time_start=22,  # 10PM
        time_end=6,     # 6AM
        tz="America/New_York"
    )
    
    cpu_criterion = CpuCriterion(threshold=75.0, workers=4)
    memory_criterion = MemoryCriterion(threshold=85.0, workers=6)
    
    criteria = [time_criterion, cpu_criterion, memory_criterion]
    
    # Save configuration
    print("Saving configuration...")
    save_configuration(criteria, config_file)
    
    # Load configuration
    print("\nLoading configuration...")
    loaded_criteria = load_configuration(config_file)
    
    # Create executor with loaded configuration
    # Use the first criterion for this example
    executor = AdaptiveExecutor(
        max_workers=10,
        policy=loaded_criteria[0],
        check_interval=30
    )
    
    print("\nConfiguration Management Example")
    print("=" * 40)
    print(f"Loaded {len(loaded_criteria)} criteria from configuration")
    print(f"Using criterion: {type(loaded_criteria[0]).__name__}")
    print()
    
    # Submit some tasks
    def config_task(task_id):
        print(f"Task {task_id} completed with {executor.current_workers} workers")
    
    print("Submitting tasks...")
    for i in range(3):
        executor.submit(config_task, i)
    
    # Run briefly to demonstrate
    import time
    time.sleep(5)
    
    print("\nShutting down...")
    executor.shutdown()


if __name__ == "__main__":
    main()
