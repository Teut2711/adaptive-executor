Installation
============

Get started with Adaptive Executor in minutes. This comprehensive guide covers installation methods, dependency management, and development setup for optimal Python concurrency performance.

Installation Options
--------------------

Adaptive Executor offers flexible installation options to suit your needs:

**Minimal Installation (Core Only)**

.. code-block:: bash

   pip install adaptive-executor

This installs only the core library without any optional dependencies.

**Feature-Specific Installations**

.. code-block:: bash

   # Time-based scaling only
   pip install adaptive-executor[time]

   # CPU/Memory monitoring only  
   pip install adaptive-executor[cpu]

   # Both time and CPU/memory features
   pip install adaptive-executor[time,cpu]

   # Complete feature set (recommended)
   pip install adaptive-executor[standard]

**Development Installation**

.. code-block:: bash

   pip install adaptive-executor[dev]

**All Features**

.. code-block:: bash

   pip install adaptive-executor[all]

Feature Dependencies
-------------------

**Core Package**

No dependencies - provides the base AdaptiveExecutor and MultiCriterionPolicy classes.

**Time Feature (`[time]`)**

* **pytz >= 2023.3**: Required for TimeCriterion for timezone-aware scheduling

**CPU/Memory Feature (`[cpu]`)**

* **psutil >= 5.9.0**: Required for CpuCriterion and MemoryCriterion for system monitoring

**Standard Feature (`[standard]`)**

* Includes both `time` and `cpu` features
* **Recommended for most users**

**Development Features (`[dev]`)**

All standard features plus:

* **pytest >= 7.0.0**: Testing framework with async support
* **pytest-cov >= 4.0.0**: Coverage reporting for test quality
* **black >= 23.0.0**: Code formatting for consistent style
* **isort >= 5.12.0**: Import sorting for clean imports
* **flake8 >= 6.0.0**: Linting for code quality
* **mypy >= 1.0.0**: Static type checking for robust code
* **pre-commit >= 3.0.0**: Pre-commit hooks for code quality

From source
-----------

Install directly from the GitHub repository for the latest features:

.. code-block:: bash

   git clone https://github.com/Teut2711/adaptive-executor.git
   cd adaptive-executor
   pip install -e .

For feature-specific installations from source:

.. code-block:: bash

   # Install with specific features
   pip install -e ".[time,cpu]"
   pip install -e ".[standard]"
   pip install -e ".[dev]"

The `-e` flag installs in editable mode, allowing you to modify the source code and see changes immediately.

Development setup
-----------------

For contributors or advanced users who want to modify the library:

.. code-block:: bash

   git clone https://github.com/Teut2711/adaptive-executor.git
   cd adaptive-executor
   uv venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   pip install -e ".[dev]"

Usage Examples by Installation Type
----------------------------------

**Minimal Installation**
Only provides the base classes - you'll need to create your own criteria:

.. code-block:: python

   from adaptive_executor import AdaptiveExecutor, MultiCriterionPolicy
   from adaptive_executor.criteria import ScalingCriterion

   class CustomCriterion(ScalingCriterion):
       def max_workers(self):
           return 5  # Your custom logic here

   policy = MultiCriterionPolicy([CustomCriterion()], hard_cap=10)
   executor = AdaptiveExecutor(max_workers=15, policy=policy)

**Time Feature Installation**
Enables time-based scaling:

.. code-block:: python

   from adaptive_executor.criteria import TimeCriterion
   
   time_crit = TimeCriterion(day_workers=2, night_workers=8)
   policy = MultiCriterionPolicy([time_crit], hard_cap=10)
   executor = AdaptiveExecutor(max_workers=15, policy=policy)

**CPU/Memory Feature Installation**
Enables resource-aware scaling:

.. code-block:: python

   from adaptive_executor.criteria import CpuCriterion, MemoryCriterion
   
   cpu_crit = CpuCriterion(threshold=75)
   mem_crit = MemoryCriterion(threshold=80)
   policy = MultiCriterionPolicy([cpu_crit, mem_crit], hard_cap=10)
   executor = AdaptiveExecutor(max_workers=15, policy=policy)

**Standard Installation**
Combines all features for maximum flexibility:

.. code-block:: python

   from adaptive_executor.criteria import TimeCriterion, CpuCriterion, MemoryCriterion
   
   time_crit = TimeCriterion(day_workers=2, night_workers=8)
   cpu_crit = CpuCriterion(threshold=75)
   mem_crit = MemoryCriterion(threshold=80)
   
   policy = MultiCriterionPolicy([time_crit, cpu_crit, mem_crit], hard_cap=15)
   executor = AdaptiveExecutor(max_workers=20, policy=policy)

Verification
------------

Verify your installation and available features:

.. code-block:: python

   from adaptive_executor import AdaptiveExecutor, MultiCriterionPolicy
   print("Core Adaptive Executor imported successfully!")

   # Test time feature (if installed)
   try:
       from adaptive_executor.criteria import TimeCriterion
       print("TimeCriterion available")
   except ImportError as e:
       print(f"TimeCriterion not available: {e}")

   # Test CPU feature (if installed)
   try:
       from adaptive_executor.criteria import CpuCriterion, MemoryCriterion
       print("CpuCriterion and MemoryCriterion available")
   except ImportError as e:
       print(f"CPU/Memory criteria not available: {e}")

This will show which features are available based on your installation choice.

System Requirements
-------------------

* **Python 3.9+**: Modern Python features and performance improvements
* **Operating System**: Cross-platform (Windows, macOS, Linux)
* **Memory**: Minimal overhead for core package
* **Dependencies**: Vary based on selected features (see above)

Troubleshooting
---------------

**ImportError for TimeCriterion**

.. code-block:: bash

   pip install adaptive-executor[time]

**ImportError for CpuCriterion/MemoryCriterion**

.. code-block:: bash

   pip install adaptive-executor[cpu]

**Multiple features needed**

.. code-block:: bash

   pip install adaptive-executor[time,cpu]
   # or
   pip install adaptive-executor[standard]
