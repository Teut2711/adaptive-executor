Adaptive Executor
================

Adaptive thread pool executor with dynamic scaling policies for optimal Python concurrency performance.

.. toctree::
   :maxdepth: 2
   :caption: Contents:

   installation
   quickstart
   api
   examples

**Adaptive Executor** is a high-performance Python library that intelligently scales thread pool concurrency based on real-time system resources and time-based policies. Perfect for applications that need to optimize performance while maintaining system stability.

**Key Benefits:**
* **Dynamic Scaling**: Automatically adjusts worker threads based on CPU usage, memory consumption, and time of day
* **Resource-Aware**: Prevents system overload by monitoring system resources in real-time
* **Flexible Policies**: Combine multiple scaling criteria for customized behavior
* **Production Ready**: Built with robust error handling and graceful shutdown mechanisms

**Perfect For:**
* Web scraping applications with time-based scheduling
* Data processing pipelines with resource constraints
* Background job processing with adaptive scaling
* Any application requiring intelligent thread management

Features
--------

* Time-based scaling for day/night optimization
* CPU & memory monitoring for resource-aware execution
* Multi-criterion aggregation for complex scaling policies
* Graceful shutdown with signal handling
* Thread-safe operations with semaphore-based control

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
