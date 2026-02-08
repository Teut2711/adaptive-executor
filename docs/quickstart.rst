Quick Start
===========

Get up and running with Adaptive Executor in minutes. This guide will show you how to create intelligent thread pools that automatically scale based on system resources and time-based policies.

Basic Usage
-----------

The simplest way to use Adaptive Executor is with a basic scaling policy:

.. code-block:: python

   from adaptive_executor import AdaptiveExecutor, MultiCriterionPolicy
   from adaptive_executor.criteria import TimeCriterion, CpuCriterion

   # Create criteria for scaling
   time_criteria = TimeCriterion(workers=8, time_start=22, time_end=3)
   cpu_criteria = CpuCriterion(threshold=75.0, workers=4)

   # Combine criteria with a policy
   policy = MultiCriterionPolicy([time_criteria, cpu_criteria], hard_cap=10)

   # Create and use the executor
   executor = AdaptiveExecutor(max_workers=15, policy=policy, check_interval=30)

   # Submit tasks
   def my_task(task_id):
       print(f"Processing task {task_id}")

   for i in range(5):
       executor.submit(my_task, i)

   # Wait for all tasks to complete
   executor.join()
   executor.shutdown()

This example creates an executor that:
* Uses 8 workers between 10PM-3AM, 1 worker otherwise
* Scales to 4 workers when CPU usage >= 75%
* Never exceeds 10 workers (hard cap)
* Checks scaling conditions every 30 seconds

Scaling Criteria
----------------

Time-based scaling
~~~~~~~~~~~~~~~~~~

Optimize performance based on time of day - perfect for applications that should be more aggressive during off-peak hours:

.. code-block:: python

   from adaptive_executor.criteria import TimeCriterion

   # Scale based on time of day
   time_crit = TimeCriterion(
       day_workers=2,      # Conservative during business hours
       night_workers=10,   # Aggressive during off-peak hours  
       night_start=22,     # 10 PM start of night period
       night_end=6,        # 6 AM end of night period
       tz="America/New_York"  # Your timezone
   )

   # Use with executor
   policy = MultiCriterionPolicy([time_crit], hard_cap=12)
   executor = AdaptiveExecutor(max_workers=20, policy=policy)

**Use cases:**
* Web scraping (more aggressive when target servers are less busy)
* Data processing (batch jobs during off-peak hours)
* Background maintenance tasks

CPU-based scaling
~~~~~~~~~~~~~~~~~

Automatically reduce concurrency when system resources are constrained:

.. code-block:: python

   from adaptive_executor.criteria import CpuCriterion

   # Scale based on CPU usage
   cpu_crit = CpuCriterion(threshold=80)
   # Uses 2 workers when CPU > 80%, otherwise 12 workers

   policy = MultiCriterionPolicy([cpu_crit], hard_cap=15)
   executor = AdaptiveExecutor(max_workers=20, policy=policy)

**Benefits:**
* Prevents CPU overload during intensive tasks
* Maintains system responsiveness
* Automatically adapts to varying workloads

Memory-based scaling
~~~~~~~~~~~~~~~~~~~~

Protect your system from memory exhaustion during data-intensive operations:

.. code-block:: python

   from adaptive_executor.criteria import MemoryCriterion

   # Scale based on memory usage
   mem_crit = MemoryCriterion(threshold=85)
   # Uses 2 workers when memory > 85%, otherwise 12 workers

   policy = MultiCriterionPolicy([mem_crit], hard_cap=15)
   executor = AdaptiveExecutor(max_workers=20, policy=policy)

**Ideal for:**
* Large file processing
* Data analysis pipelines
* Image/video processing workflows

Advanced Configuration
----------------------

Multi-criteria Scaling
~~~~~~~~~~~~~~~~~~~~~

Combine multiple criteria for sophisticated scaling behavior:

.. code-block:: python

   from adaptive_executor import AdaptiveExecutor, MultiCriterionPolicy
   from adaptive_executor.criteria import TimeCriterion, CpuCriterion, MemoryCriterion

   # Create multiple scaling criteria
   time_policy = TimeCriterion(
       day_workers=3, night_workers=12,
       night_start=20, night_end=6,
       tz="UTC"
   )
   cpu_policy = CpuCriterion(threshold=75)
   memory_policy = MemoryCriterion(threshold=80)

   # Combine all criteria
   policy = MultiCriterionPolicy(
       [time_policy, cpu_policy, memory_policy],
       hard_cap=15
   )

   # Create executor with frequent checking
   executor = AdaptiveExecutor(
       max_workers=20,
       policy=policy,
       check_interval=45  # Check every 45 seconds
   )

This creates an intelligent executor that:
* Uses time-based scaling as the baseline
* Reduces workers when CPU or memory are constrained
* Never exceeds 15 workers regardless of conditions
* Monitors system state every 45 seconds

Real-world Examples
-------------------

Web Scraping with Time Optimization
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   import time
   from adaptive_executor import AdaptiveExecutor, MultiCriterionPolicy
   from adaptive_executor.criteria import TimeCriterion
   import requests

   def scrape_url(url):
       try:
           response = requests.get(url, timeout=10)
           print(f"Scraped {url}: {len(response.content)} bytes")
           return len(response.content)
       except Exception as e:
           print(f"Error scraping {url}: {e}")
           return 0

   # Aggressive scraping during off-peak hours
   time_policy = TimeCriterion(
       day_workers=2,      # Respectful during business hours
       night_workers=20,    # Aggressive during night
       night_start=22, night_end=6,
       tz="America/New_York"
   )

   policy = MultiCriterionPolicy([time_policy], hard_cap=25)
   executor = AdaptiveExecutor(max_workers=30, policy=policy, check_interval=60)

   urls = [f"https://example.com/page/{i}" for i in range(100)]

   start_time = time.time()
   for url in urls:
       executor.submit(scrape_url, url)

   executor.join()
   print(f"Completed in {time.time() - start_time:.2f} seconds")
   executor.shutdown()

Data Processing with Resource Awareness
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   import pandas as pd
   from adaptive_executor import AdaptiveExecutor, MultiCriterionPolicy
   from adaptive_executor.criteria import CpuCriterion, MemoryCriterion

   def process_chunk(chunk_file):
       try:
           df = pd.read_csv(chunk_file)
           processed = df.groupby('category').agg({'value': ['sum', 'mean']})
           output_file = chunk_file.replace('.csv', '_processed.csv')
           processed.to_csv(output_file)
           print(f"Processed {chunk_file} -> {output_file}")
           return len(df)
       except Exception as e:
           print(f"Error processing {chunk_file}: {e}")
           return 0

   # Conservative scaling to protect system resources
   cpu_policy = CpuCriterion(threshold=70)
   memory_policy = MemoryCriterion(threshold=75)

   policy = MultiCriterionPolicy([cpu_policy, memory_policy], hard_cap=8)
   executor = AdaptiveExecutor(max_workers=12, policy=policy, check_interval=30)

   chunk_files = [f"data/chunk_{i}.csv" for i in range(50)]

   total_rows = 0
   for chunk_file in chunk_files:
       executor.submit(process_chunk, chunk_file)

   executor.join()
   print(f"Processed {total_rows} total rows")
   executor.shutdown()

Best Practices
--------------

* **Start conservative**: Begin with lower worker counts and monitor performance
* **Set appropriate check intervals**: Too frequent checking adds overhead, too infrequent misses opportunities
* **Use hard caps**: Always set a reasonable maximum to prevent system overload
* **Monitor system metrics**: Use tools like `htop` or Activity Monitor to understand scaling behavior
* **Test different thresholds**: Optimize CPU/memory thresholds for your specific workload

Next Steps
----------

Now that you understand the basics, explore these topics:

* :doc:`api` - Detailed API reference
* :doc:`examples` - More advanced usage patterns
* :doc:`installation` - Development setup and contributing
