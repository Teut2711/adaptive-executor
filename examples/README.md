# Adaptive Executor Examples

This directory contains practical examples of using Adaptive Executor in various scenarios.

## Examples

### [Basic Usage](./basic_usage.py)
Simple example showing basic Adaptive Executor setup with time and CPU-based scaling.

### [Web Scraping](./web_scraping.py)
Demonstrates time-based scaling for web scraping applications that should be more aggressive during off-peak hours.

### [Data Processing](./data_processing.py)
Shows resource-aware scaling for CPU and memory-intensive data processing tasks.

### [Multi-criteria Scaling](./multi_criteria.py)
Advanced example combining time, CPU, and memory criteria for intelligent scaling.

### [Custom Criteria](./custom_criteria.py)
Example of creating custom scaling criteria for your specific use case.

## Running Examples

1. Install Adaptive Executor with all features:
   ```bash
   pip install adaptive-executor[standard]
   ```

2. Run any example:
   ```bash
   python examples/basic_usage.py
   ```

## Contributing

Have a great example? Please add it! Examples should:
- Be self-contained and runnable
- Include clear comments explaining the approach
- Demonstrate specific Adaptive Executor features
- Follow the project's coding standards
