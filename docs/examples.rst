Examples
========

Web Scraping with Time-based Scaling
------------------------------------

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

   # Night-time scraping (more workers when load is lower)
   time_policy = TimeCriterion(
       day_workers=2,      # Conservative during day
       night_workers=15,    # Aggressive during night
       night_start=22,
       night_end=6,
       tz="America/New_York"
   )

   policy = MultiCriterionPolicy([time_policy], hard_cap=20)
   executor = AdaptiveExecutor(max_workers=25, policy=policy, check_interval=60)

   urls = [f"https://example.com/page/{i}" for i in range(100)]

   start_time = time.time()
   for url in urls:
       executor.submit(scrape_url, url)

   executor.join()
   print(f"Completed in {time.time() - start_time:.2f} seconds")
   executor.shutdown()

Data Processing with Resource-aware Scaling
--------------------------------------------

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

   # Scale down when resources are constrained
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

Multi-criteria Hybrid Scaling
------------------------------

.. code-block:: python

   from adaptive_executor import AdaptiveExecutor, MultiCriterionPolicy
   from adaptive_executor.criteria import TimeCriterion, CpuCriterion, MemoryCriterion

   def background_task(task_id, duration):
       import time
       time.sleep(duration)
       print(f"Task {task_id} completed after {duration}s")

   # Combine multiple scaling factors
   time_policy = TimeCriterion(
       day_workers=3, night_workers=8,
       night_start=20, night_end=6
   )
   cpu_policy = CpuCriterion(threshold=75)
   memory_policy = MemoryCriterion(threshold=80)

   policy = MultiCriterionPolicy(
       [time_policy, cpu_policy, memory_policy],
       hard_cap=10
   )

   executor = AdaptiveExecutor(
       max_workers=15,
       policy=policy,
       check_interval=45
   )

   # Submit varied workload
   import random
   for i in range(30):
       duration = random.uniform(0.5, 3.0)
       executor.submit(background_task, i, duration)

   executor.join()
   executor.shutdown()
