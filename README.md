
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

## Logging Configuration

The adaptive-executor provides comprehensive logging that can be configured to suit your needs. By default, it logs to the console with INFO level.

### Basic Logging Control

```python
from adaptive_executor import setup_logger

# Disable all logging
setup_logger(level=logging.CRITICAL)

# Or set a specific log level
import logging
setup_logger(level=logging.WARNING)  # Only show warnings and above
```

### Advanced Logging Configuration

You can also configure file logging with rotation:

```python
# Configure file logging with rotation (10MB per file, keep 5 backups)
setup_logger(
    level=logging.DEBUG,
    log_file="/var/log/adaptive_executor.log",
    max_bytes=10*1024*1024,  # 10MB
    backup_count=5
)
```

### Environment Variables

You can control logging via environment variables:

```bash
# Set log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
ADAPTIVE_EXECUTOR_LOG_LEVEL=WARNING

# Enable file logging
ADAPTIVE_EXECUTOR_LOG_FILE=/path/to/logfile.log

# Set max log file size (in bytes)
ADAPTIVE_EXECUTOR_LOG_MAX_BYTES=10485760  # 10MB

# Set number of backup files to keep
ADAPTIVE_EXECUTOR_LOG_BACKUP_COUNT=5
```

### Disabling Logging Completely

To completely disable all logging:

```python
import logging
logging.getLogger('adaptive_executor').addHandler(logging.NullHandler())
logging.getLogger('adaptive_executor').propagate = False
```

## Documentation

Full documentation is available at [https://Teut2711.github.io/adaptive-executor](https://Teut2711.github.io/adaptive-executor)

## License

MIT License - see [LICENSE](LICENSE) file for details.
