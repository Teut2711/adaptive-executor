Examples
========

This section contains practical examples of using Adaptive Executor in various scenarios.

.. toctree::
   :maxdepth: 2

   examples/time_scaling
   examples/resource_scaling
   examples/complex_scaling
   examples/conditional_scaling
   examples/config_management
   examples/basic_usage
   examples/web_scraping
   examples/data_processing
   examples/multi_criteria
   examples/custom_criteria

Time-based Scaling
------------------

.. literalinclude:: ../examples/time_scaling.py
   :language: python
   :lines: 1-30

Scale workers based on time of day. Perfect for applications that should be more aggressive during off-peak hours.

Resource-based Scaling
---------------------

.. literalinclude:: ../examples/resource_scaling.py
   :language: python
   :lines: 1-35

Scale workers based on CPU and memory usage. Ideal for resource-intensive applications.

Complex Logic
-------------

.. literalinclude:: ../examples/complex_scaling.py
   :language: python
   :lines: 1-35

Combine multiple criteria with AND logic. Perfect for applications that need multiple conditions met simultaneously.

Conditional Scaling
------------------

.. literalinclude:: ../examples/conditional_scaling.py
   :language: python
   :lines: 1-35

Apply different scaling based on dynamic conditions. Great for adaptive behavior.

Configuration Management
----------------------

.. literalinclude:: ../examples/config_management.py
   :language: python
   :lines: 1-35

Save and load scaling configurations using JSON serialization. Essential for production deployments.

Legacy Examples
---------------

.. literalinclude:: ../examples/basic_usage.py
   :language: python
   :lines: 1-30

Web Scraping with Time-Based Scaling
-----------------------------------

.. literalinclude:: ../examples/web_scraping.py
   :language: python
   :lines: 1-25

Data Processing with Resource Awareness
------------------------------------

.. literalinclude:: ../examples/data_processing.py
   :language: python
   :lines: 1-30

Multi-Criteria Scaling
---------------------

.. literalinclude:: ../examples/multi_criteria.py
   :language: python
   :lines: 1-35

Custom Scaling Criteria
---------------------

.. literalinclude:: ../examples/custom_criteria.py
   :language: python
   :lines: 1-45

Running Examples
----------------

1. Install Adaptive Executor with all features:

.. code-block:: bash

   pip install adaptive-executor[standard]

2. Run any example:

.. code-block:: bash

   python examples/basic_usage.py

For more examples and details, see the :doc:`examples directory <../examples/>`.
