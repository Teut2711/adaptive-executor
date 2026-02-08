
# Adaptive Executor

Adaptive thread pool executor that scales concurrency based on policies.

## Features
- Time-based scaling
- CPU & memory criteria
- Multi-criterion aggregation
- Graceful shutdown

## Installation

**Minimal Installation (Core Only)**
```bash
pip install adaptive-executor
```

**Feature-Specific Installations**
```bash
# Time-based scaling only
pip install adaptive-executor[time]

# CPU/Memory monitoring only
pip install adaptive-executor[cpu]

# Complete feature set (recommended)
pip install adaptive-executor[standard]

# Development with all tools
pip install adaptive-executor[dev]
```

## Quick Start

```python
from adaptive_executor import AdaptiveExecutor, MultiCriterionPolicy
from adaptive_executor.criteria import TimeCriterion, CpuCriterion

# Create scaling criteria
time_policy = TimeCriterion(day_workers=2, night_workers=8)
cpu_policy = CpuCriterion(threshold=75)

# Combine criteria
policy = MultiCriterionPolicy([time_policy, cpu_policy], hard_cap=10)

# Create and use executor
executor = AdaptiveExecutor(max_workers=15, policy=policy)

# Submit tasks
def my_task(task_id):
    print(f"Processing task {task_id}")

for i in range(5):
    executor.submit(my_task, i)

executor.join()
executor.shutdown()
```

## Development Setup

```bash
git clone https://github.com/Teut2711/adaptive-executor.git
cd adaptive-executor
uv venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -e ".[dev]"
```

## Documentation

Full documentation is available at [https://Teut2711.github.io/adaptive-executor](https://Teut2711.github.io/adaptive-executor)

## License

MIT License - see [LICENSE](LICENSE) file for details.
