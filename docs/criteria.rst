Scaling Criteria
===============

The adaptive-executor provides flexible scaling criteria to dynamically adjust worker counts based on various conditions.

Basic Criteria
--------------

TimeCriterion
~~~~~~~~~~~~~~~

Scale workers based on time of day.

See the :doc:`time-based example <examples/time_scaling>` for a complete implementation.

Parameters:
    * **workers** (int): Number of workers when time condition is met
    * **time_start** (int): Hour when scaling starts (0-23)
    * **time_end** (int): Hour when scaling ends (0-23)
    * **tz** (str): Timezone (default: "Asia/Kolkata")

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

See the :doc:`complex logic example <examples/complex_scaling>` for a complete implementation.

Parameters:
    * **criteria** (list): List of (criterion, workers) tuples
    * **logic** (str): "and" or "or" for combining conditions

Logic:
    * **"and"**: All conditions must be met, returns workers from first criterion
    * **"or"**: Any condition met, returns workers from matching criterion


ConditionalCriterion
~~~~~~~~~~~~~~~~~~

Apply different criteria based on conditions.

See the :doc:`conditional example <examples/conditional_scaling>` for a complete implementation.

Parameters:
    * **condition_criterion** (ScalingCriterion): Criterion that determines when to apply
    * **action_criterion** (ScalingCriterion): Criterion that provides fallback action
    * **workers** (int): Number of workers when condition is met

Returns **workers** when condition is met, otherwise returns **action_criterion.max_workers()**.


JSON Serialization
-----------------

All criteria support JSON serialization for configuration and persistence.

See the :doc:`configuration example <examples/config_management>` for a complete implementation.

Available Methods:
    * **to_dict()**: Convert to dictionary
    * **from_dict(data)**: Create from dictionary
    * **to_json()**: Convert to JSON string
    * **from_json(json_str)**: Create from JSON string


Usage Examples
--------------

For complete working examples, see the :doc:`examples documentation <examples>`.

Key Patterns:
~~~~~~~~~~~~~

* **Simple Time-based Scaling**: See :doc:`time scaling example <examples/time_scaling>`
* **Resource-based Scaling**: See :doc:`resource scaling example <examples/resource_scaling>`
* **Complex Logic**: See :doc:`complex scaling example <examples/complex_scaling>`
* **Configuration Management**: See :doc:`configuration example <examples/config_management>`
