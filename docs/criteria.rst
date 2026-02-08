Scaling Criteria
===============

The adaptive-executor provides flexible scaling criteria to dynamically adjust worker counts based on various conditions.

Basic Criteria
--------------

TimeCriterion
~~~~~~~~~~~~~~~

Scale workers based on time of day using datetime.time objects for daily recurring schedules.

See :doc:`time scaling example <../examples/time_scaling>` for a complete implementation.

Parameters:
    * **worker_count** (int): Number of workers during active time window (must be ≥ 1)
    * **active_start** (datetime.time): Start time of active window (time of day)
    * **active_end** (datetime.time): End time of active window (time of day)
    * **timezone** (str): Timezone string (e.g., "America/New_York", "Asia/Kolkata") (default: "UTC")

Raises:
    * **TypeError**: If active_start or active_end are not datetime.time objects
    * **ValueError**: If worker_count is less than 1
    * **ImportError**: If pytz package is not installed

Examples:
    .. code-block:: python

        from datetime import time
        
        # Night shift (10PM to 3AM next day)
        TimeCriterion(
            worker_count=8,
            active_start=time(22, 0),  # 10PM
            active_end=time(3, 0),     # 3AM next day
            timezone="America/New_York"
        )
        
        # Day shift (9AM to 6PM)
        TimeCriterion(
            worker_count=6,
            active_start=time(9, 0),   # 9AM
            active_end=time(18, 0),    # 6PM
            timezone="Asia/Kolkata"
        )

The time range wraps around midnight. For example, 22:00 to 03:00 creates an active window from 10PM to 3AM.

Returns **worker_count** when current time is within active window (inclusive of start time, exclusive of end time), otherwise returns **1**.


DateTimeCriterion
~~~~~~~~~~~~~~~~~

Scale workers based on specific datetime objects for precise timestamp scheduling.

See :doc:`datetime scaling example <../examples/datetime_scaling>` for a complete implementation.

Parameters:
    * **worker_count** (int): Number of workers during active time window (must be ≥ 1)
    * **active_start** (datetime.datetime): Start timestamp of active window
    * **active_end** (datetime.datetime): End timestamp of active window
    * **timezone** (str): Timezone string (e.g., "America/New_York", "Asia/Kolkata") (default: "UTC")

Raises:
    * **TypeError**: If active_start or active_end are not datetime.datetime objects
    * **ValueError**: If worker_count is less than 1
    * **ImportError**: If pytz package is not installed

Examples:
    .. code-block:: python

        from datetime import datetime
        
        # Specific maintenance window
        DateTimeCriterion(
            worker_count=2,
            active_start=datetime(2024, 1, 15, 2, 0),  # Jan 15, 2024 2AM
            active_end=datetime(2024, 1, 15, 4, 0),    # Jan 15, 2024 4AM
            timezone="UTC"
        )
        
        # Date-specific promotional period
        DateTimeCriterion(
            worker_count=12,
            active_start=datetime(2024, 11, 24, 0, 0),  # Black Friday start
            active_end=datetime(2024, 11, 24, 23, 59), # Black Friday end
            timezone="America/New_York"
        )

Returns **worker_count** when current timestamp is within the specified datetime range, otherwise returns **1**.


CpuCriterion
~~~~~~~~~~~~~

Scale workers based on CPU usage.

See :doc:`resource-based example <../examples/resource_scaling>` for a complete implementation.

Parameters:
    * **threshold** (float): CPU percentage threshold (0-100)
    * **workers** (int): Number of workers when threshold is met

Returns **workers** when CPU usage >= threshold, otherwise returns **1**.


MemoryCriterion
~~~~~~~~~~~~~~~

Scale workers based on memory usage.

See :doc:`resource-based example <../examples/resource_scaling>` for a complete implementation.

Parameters:
    * **threshold** (float): Memory percentage threshold (0-100)
    * **workers** (int): Number of workers when threshold is met

Returns **workers** when memory usage >= threshold, otherwise returns **1**.


Advanced Criteria
----------------

MultiCriterion
~~~~~~~~~~~~~~

Combine multiple criteria with AND/OR logic.

See :doc:`complex logic example <../examples/complex_scaling>` for a complete implementation.

Parameters:
    * **criteria** (list): List of (criterion, workers) tuples
    * **logic** (str): "and" or "or" for combining conditions

Logic:
    * **"and"**: All conditions must be met, returns workers from first criterion
    * **"or"**: Any condition met, returns workers from matching criterion

ConditionalCriterion
~~~~~~~~~~~~~~~~~~

Apply different criteria based on conditions.

See :doc:`conditional example <../examples/conditional_scaling>` for a complete implementation.

Parameters:
    * **condition_criterion** (ScalingCriterion): Criterion that determines when to apply
    * **action_criterion** (ScalingCriterion): Criterion that provides fallback action
    * **workers** (int): Number of workers when condition is met

Returns **workers** when condition is met, otherwise returns **action_criterion.max_workers()**.


JSON Serialization
-----------------

All criteria support JSON serialization for configuration and persistence.

See :doc:`configuration example <../examples/config_management>` for a complete implementation.

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

* **Daily Time-based Scaling**: Use :class:`TimeCriterion` for recurring daily schedules
* **Specific DateTime Scaling**: Use :class:`DateTimeCriterion` for one-time or date-specific scheduling
* **Resource-based Scaling**: See :doc:`resource scaling example <../examples/resource_scaling>`
* **Complex Logic**: See :doc:`complex scaling example <../examples/complex_scaling>`
* **Configuration Management**: See :doc:`configuration example <../examples/config_management>`
