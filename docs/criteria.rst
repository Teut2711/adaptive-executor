Scaling Criteria
===============

The adaptive-executor provides flexible scaling criteria to dynamically adjust worker counts based on various conditions.

Basic Criteria
--------------

TimeCriterion
~~~~~~~~~~~~~~~

Scale workers based on time of day.

See the :doc:`time scaling example <../examples/time_scaling>` for a complete implementation.

Parameters:
    * **workers** (int): Number of workers when time condition is met
    * **start_time** (int or datetime.time): Starting time - either hour (0-23) or datetime.time object
    * **end_time** (int or datetime.time): Ending time - either hour (0-23) or datetime.time object  
    * **tz** (str): Timezone string (default: "UTC")

Examples:
    .. code-block:: python

        # Using integers (hours)
        TimeCriterion(workers=8, start_time=22, end_time=3)  # 10PM to 3AM
        
        # Using datetime.time objects
        from datetime import time
        TimeCriterion(workers=8, start_time=time(22, 0), end_time=time(3, 0))  # 10PM to 3AM
        
        # Use case: Peak processing window (April 13th 5:30PM to April 17th 5:20AM)
        # Scale to maximum workers during critical business hours
        TimeCriterion(workers=12, start_time=time(17, 30), end_time=time(5, 20))

The time range wraps around midnight. For example, start_time=22 and end_time=3 creates an active window from 10PM to 3AM.

Returns **workers** when current hour is between time_start and time_end, otherwise returns **1**.


CpuCriterion
~~~~~~~~~~~~

Scale workers based on CPU usage.

See the :doc:`resource-based example <examples/resource_scaling>` for a complete implementation.

Parameters:
    * **threshold** (float): CPU percentage threshold (0-100)
    * **workers** (int): Number of workers when threshold is met

Returns **workers** when CPU usage >= threshold, otherwise returns **1**.


MemoryCriterion
~~~~~~~~~~~~~~~

Scale workers based on memory usage.

See the :doc:`resource-based example <examples/resource_scaling>` for a complete implementation.

Parameters:
    * **threshold** (float): Memory percentage threshold (0-100)
    * **workers** (int): Number of workers when threshold is met

Returns **workers** when memory usage >= threshold, otherwise returns **1**.


Advanced Criteria
----------------

MultiCriterion
~~~~~~~~~~~~~~

Combine multiple criteria with AND/OR logic.

See the :doc:`complex logic example <../examples/complex_scaling>` for a complete implementation.

Parameters:
    * **criteria** (list): List of (criterion, workers) tuples
    * **logic** (str): "and" or "or" for combining conditions

Logic:
    * **"and"**: All conditions must be met, returns workers from first criterion
    * **"or"**: Any condition met, returns workers from matching criterion


ConditionalCriterion
~~~~~~~~~~~~~~~~~~

Apply different criteria based on conditions.

See the :doc:`conditional example <../examples/conditional_scaling>` for a complete implementation.

Parameters:
    * **condition_criterion** (ScalingCriterion): Criterion that determines when to apply
    * **action_criterion** (ScalingCriterion): Criterion that provides fallback action
    * **workers** (int): Number of workers when condition is met

Returns **workers** when condition is met, otherwise returns **action_criterion.max_workers()**.


JSON Serialization
-----------------

All criteria support JSON serialization for configuration and persistence.

See the :doc:`configuration example <../examples/config_management>` for a complete implementation.

Available Methods:
    * **to_dict()**: Convert to dictionary
    * **from_dict(data)**: Create from dictionary
    * **to_json()**: Convert to JSON string
    * **from_json(json_str)**: Create from JSON string


Usage Examples
--------------

For complete working examples, see the :doc:`examples documentation <../examples/>`.

Key Patterns
~~~~~~~~~~~~~

* **Simple Time-based Scaling**: See the :doc:`time scaling example <../examples/time_scaling>`
* **Resource-based Scaling**: See the :doc:`resource scaling example <../examples/resource_scaling>`
* **Complex Logic**: See the :doc:`complex scaling example <../examples/complex_scaling>`
* **Configuration Management**: See the :doc:`configuration example <../examples/config_management>`
