Scaling Criteria
===============

The adaptive-executor provides flexible scaling criteria to dynamically adjust worker counts based on various conditions.

Basic Criteria
--------------

TimeCriterion
~~~~~~~~~~~~~~~

Scale workers based on time of day using datetime objects for precise time window specification.

See the :doc:`time scaling example <../examples/time_scaling>` for a complete implementation.

Parameters:
    * **worker_count** (int): Number of workers during active time window (must be ≥ 1)
    * **active_start** (datetime.datetime): Start time of active window (only hour and minute are used)
    * **active_end** (datetime.datetime): End time of active window (only hour and minute are used)
    * **timezone** (str): Timezone string (e.g., "America/New_York", "Asia/Kolkata") (default: "UTC")

Raises:
    * **TypeError**: If active_start or active_end are not datetime.datetime objects
    * **ValueError**: If worker_count is less than 1 or hours are not in 0-23 range
    * **ImportError**: If pytz package is not installed

Examples:
    .. code-block:: python

        from datetime import datetime
        
        # Night shift (10PM to 3AM next day)
        TimeCriterion(
            worker_count=8,
            active_start=datetime(2024, 1, 1, 22, 0),  # 10PM
            active_end=datetime(2024, 1, 2, 3, 0),     # 3AM next day
            timezone="America/New_York"
        )
        
        # Day shift (9AM to 6PM)
        TimeCriterion(
            worker_count=6,
            active_start=datetime(2024, 1, 1, 9, 0),   # 9AM
            active_end=datetime(2024, 1, 1, 18, 0),    # 6PM
            timezone="Asia/Kolkata"
        )

The time range wraps around midnight. For example, 22:00 to 03:00 creates an active window from 10PM to 3AM.

Returns **worker_count** when current time is within the active window (inclusive of start time, exclusive of end time), otherwise returns **1**.


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
