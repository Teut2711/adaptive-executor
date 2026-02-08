import pytest
from adaptive_executor.criteria import (
    ScalingCriterion,
    TimeCriterion,
    CpuCriterion,
    MemoryCriterion,
    MultiCriterion,
    ConditionalCriterion,
)


def test_scaling_base_class_raises_not_implemented():
    criterion = ScalingCriterion()
    with pytest.raises(NotImplementedError):
        criterion.max_workers()


def test_time_criterion_initialization():
    import datetime
    criterion = TimeCriterion(
        worker_count=8, 
        active_start=datetime.datetime(2024, 1, 1, 22, 0), 
        active_end=datetime.datetime(2024, 1, 1, 3, 0), 
        timezone="UTC"
    )
    assert criterion.worker_count == 8
    assert criterion.time_start == 22
    assert criterion.time_end == 3
    assert criterion.tz.zone == "UTC"


def test_time_criterion_with_datetime_objects():
    import datetime
    criterion = TimeCriterion(
        worker_count=8, 
        active_start=datetime.datetime(2024, 1, 1, 22, 30),  # 10:30 PM
        active_end=datetime.datetime(2024, 1, 1, 3, 30),     # 3:30 AM
        timezone="UTC"
    )
    assert criterion.worker_count == 8
    assert criterion.time_start == 22  # Extracted hour
    assert criterion.time_end == 3     # Extracted hour
    assert criterion.tz.zone == "UTC"


def test_time_criterion_validation():
    import datetime
    
    # Test invalid types - must be datetime instances
    with pytest.raises(TypeError, match="active_start must be a datetime.datetime instance"):
        TimeCriterion(worker_count=8, active_start=22, active_end=datetime.datetime(2024, 1, 1, 3, 0))
    
    with pytest.raises(TypeError, match="active_end must be a datetime.datetime instance"):
        TimeCriterion(worker_count=8, active_start=datetime.datetime(2024, 1, 1, 22, 0), active_end=3)
    
    with pytest.raises(TypeError, match="active_start must be a datetime.datetime instance"):
        TimeCriterion(worker_count=8, active_start="22", active_end=datetime.datetime(2024, 1, 1, 3, 0))
    
    with pytest.raises(TypeError, match="active_end must be a datetime.datetime instance"):
        TimeCriterion(worker_count=8, active_start=datetime.datetime(2024, 1, 1, 22, 0), active_end="3")
    
    # Test invalid workers
    with pytest.raises(ValueError, match="worker_count must be at least 1"):
        TimeCriterion(worker_count=0, active_start=datetime.datetime(2024, 1, 1, 22, 0), active_end=datetime.datetime(2024, 1, 1, 3, 0))
    
    # Test invalid hour values
    with pytest.raises(ValueError, match="active_start hour must be between 0 and 23"):
        TimeCriterion(worker_count=8, active_start=datetime.datetime(2024, 1, 1, 25, 0), active_end=datetime.datetime(2024, 1, 1, 3, 0))
    
    with pytest.raises(ValueError, match="active_end hour must be between 0 and 23"):
        TimeCriterion(worker_count=8, active_start=datetime.datetime(2024, 1, 1, 22, 0), active_end=datetime.datetime(2024, 1, 1, 24, 0))


def test_time_criterion_missing_pytz():
    import sys
    import importlib
    import datetime
    
    # Store original modules
    original_modules = sys.modules.copy()
    
    # Remove pytz and criteria module
    sys.modules.pop('pytz', None)
    sys.modules.pop('adaptive_executor.criteria', None)
    
    try:
        # Mock importlib.util.find_spec to return None for pytz
        import importlib.util
        original_find_spec = importlib.util.find_spec
        
        def mock_find_spec(name):
            if name == 'pytz':
                return None
            return original_find_spec(name)
        
        importlib.util.find_spec = mock_find_spec
        
        # Reimport the module
        import adaptive_executor.criteria as criteria_module
        
        with pytest.raises(ImportError, match="TimeCriterion requires 'pytz' package"):
            criteria_module.TimeCriterion(
                worker_count=8, 
                active_start=datetime.datetime(2024, 1, 1, 22, 0), 
                active_end=datetime.datetime(2024, 1, 1, 3, 0)
            )
    finally:
        # Restore everything
        importlib.util.find_spec = original_find_spec
        sys.modules.clear()
        sys.modules.update(original_modules)


@pytest.mark.parametrize("hour,expected", [
    (10, 1),   # Daytime (outside range)
    (23, 8),   # Nighttime (in range)
    (2, 8),    # After midnight (in range)
    (22, 8),   # Exactly at start
    (3, 1),    # Exactly at end (exclusive)
])
def test_time_criterion_scaling(hour, expected, mocker):
    import datetime
    import pytz
    
    # Create a timezone-aware datetime
    tz = pytz.UTC
    mock_now = datetime.datetime(2024, 1, 1, hour, 0, 0, tzinfo=tz)
    
    # Mock datetime.datetime.now to return timezone-aware datetime
    mock_datetime_module = mocker.MagicMock()
    mock_datetime_module.now.return_value = mock_now
    mocker.patch('adaptive_executor.criteria.datetime', mock_datetime_module)
    
    criterion = TimeCriterion(
        worker_count=8, 
        active_start=datetime.datetime(2024, 1, 1, 22, 0), 
        active_end=datetime.datetime(2024, 1, 1, 3, 0)
    )
    result = criterion.max_workers()
    assert result == expected


def test_cpu_criterion_initialization():
    criterion = CpuCriterion(threshold=80.0, workers=4)
    assert criterion.threshold == 80.0
    assert criterion.workers == 4


def test_cpu_criterion_missing_psutil():
    import sys
    import importlib
    
    # Store original modules
    original_modules = sys.modules.copy()
    
    # Remove psutil and criteria module
    sys.modules.pop('psutil', None)
    sys.modules.pop('adaptive_executor.criteria', None)
    
    try:
        # Mock importlib.util.find_spec to return None for psutil
        import importlib.util
        original_find_spec = importlib.util.find_spec
        
        def mock_find_spec(name):
            if name == 'psutil':
                return None
            return original_find_spec(name)
        
        importlib.util.find_spec = mock_find_spec
        
        # Reimport the module
        import adaptive_executor.criteria as criteria_module
        
        with pytest.raises(ImportError, match="CpuCriterion requires 'psutil' package"):
            criteria_module.CpuCriterion(threshold=80.0, workers=4)
    finally:
        # Restore everything
        importlib.util.find_spec = original_find_spec
        sys.modules.clear()
        sys.modules.update(original_modules)


@pytest.mark.parametrize("cpu_percent,expected", [
    (50.0, 1),  # Below threshold
    (75.0, 4),  # At threshold
    (80.0, 4),  # Above threshold
    (90.0, 4),  # High CPU
])
def test_cpu_criterion_scaling(cpu_percent, expected, mocker):
    # Mock psutil module
    mock_psutil = mocker.MagicMock()
    mock_psutil.cpu_percent.return_value = cpu_percent
    mocker.patch.dict('sys.modules', {'psutil': mock_psutil})
    
    # Mock find_spec to return a valid spec for psutil
    mock_spec = mocker.MagicMock()
    mocker.patch('importlib.util.find_spec', return_value=mock_spec)
    
    criterion = CpuCriterion(threshold=75.0, workers=4)
    
    # Patch psutil in the criteria module
    mocker.patch('adaptive_executor.criteria.psutil', mock_psutil)
    
    result = criterion.max_workers()
    assert result == expected


def test_memory_criterion_initialization():
    criterion = MemoryCriterion(threshold=85.0, workers=6)
    assert criterion.threshold == 85.0
    assert criterion.workers == 6


def test_memory_criterion_missing_psutil():
    import sys
    import importlib
    
    # Store original modules
    original_modules = sys.modules.copy()
    
    # Remove psutil and criteria module
    sys.modules.pop('psutil', None)
    sys.modules.pop('adaptive_executor.criteria', None)
    
    try:
        # Mock importlib.util.find_spec to return None for psutil
        import importlib.util
        original_find_spec = importlib.util.find_spec
        
        def mock_find_spec(name):
            if name == 'psutil':
                return None
            return original_find_spec(name)
        
        importlib.util.find_spec = mock_find_spec
        
        # Reimport the module
        import adaptive_executor.criteria as criteria_module
        
        with pytest.raises(ImportError, match="MemoryCriterion requires 'psutil' package"):
            criteria_module.MemoryCriterion(threshold=80.0, workers=6)
    finally:
        # Restore everything
        importlib.util.find_spec = original_find_spec
        sys.modules.clear()
        sys.modules.update(original_modules)


@pytest.mark.parametrize("memory_percent,expected", [
    (60.0, 1),  # Below threshold
    (80.0, 6),  # At threshold
    (85.0, 6),  # Above threshold
    (95.0, 6),  # High memory
])
def test_memory_criterion_scaling(memory_percent, expected, mocker):
    # Mock psutil module
    mock_memory = mocker.MagicMock()
    mock_memory.percent = memory_percent
    
    mock_psutil = mocker.MagicMock()
    mock_psutil.virtual_memory.return_value = mock_memory
    mocker.patch.dict('sys.modules', {'psutil': mock_psutil})
    
    # Mock find_spec to return a valid spec for psutil
    mock_spec = mocker.MagicMock()
    mocker.patch('importlib.util.find_spec', return_value=mock_spec)
    
    criterion = MemoryCriterion(threshold=80.0, workers=6)
    
    # Patch psutil in the criteria module
    mocker.patch('adaptive_executor.criteria.psutil', mock_psutil)
    
    result = criterion.max_workers()
    assert result == expected


def test_time_criterion_serialization():
    import datetime
    
    # Test with datetime objects
    criterion = TimeCriterion(
        worker_count=8, 
        active_start=datetime.datetime(2024, 1, 1, 22, 0), 
        active_end=datetime.datetime(2024, 1, 1, 3, 0), 
        timezone="UTC"
    )
    
    # Test to_dict
    data = criterion.to_dict()
    expected = {
        "type": "TimeCriterion",
        "worker_count": 8,
        "active_start": 22,
        "active_end": 3,
        "timezone": "UTC"
    }
    assert data == expected
    
    # Test from_dict - note that from_dict still accepts integers in the dict
    restored = TimeCriterion.from_dict(data)
    assert restored.worker_count == 8
    assert restored.time_start == 22
    assert restored.time_end == 3
    assert restored.tz.zone == "UTC"
    
    # Test with datetime objects with minutes
    criterion_dt = TimeCriterion(
        worker_count=8, 
        active_start=datetime.datetime(2024, 1, 1, 22, 30), 
        active_end=datetime.datetime(2024, 1, 1, 3, 30), 
        timezone="UTC"
    )
    
    data_dt = criterion_dt.to_dict()
    # Should still store as integers (hours only)
    assert data_dt["active_start"] == 22
    assert data_dt["active_end"] == 3
    
    # Test JSON serialization
    json_str = criterion.to_json()
    restored_from_json = TimeCriterion.from_json(json_str)
    assert restored_from_json.worker_count == 8


def test_multi_criterion_validation():
    import datetime
    
    time_crit = TimeCriterion(
        worker_count=2, 
        active_start=datetime.datetime(2024, 1, 1, 22, 0), 
        active_end=datetime.datetime(2024, 1, 1, 3, 0)
    )
    
    # Test invalid logic
    with pytest.raises(ValueError, match="logic must be 'and' or 'or'"):
        MultiCriterion(criteria=[(time_crit, 2)], logic="invalid")
    
    # Test empty criteria
    with pytest.raises(ValueError, match="criteria cannot be empty"):
        MultiCriterion(criteria=[], logic="and")
    
    # Test invalid criterion type
    with pytest.raises(TypeError, match="All criteria must be ScalingCriterion instances"):
        MultiCriterion(criteria=[("not_a_criterion", 2)], logic="and")
    
    # Test invalid workers
    with pytest.raises(ValueError, match="workers must be a positive integer"):
        MultiCriterion(criteria=[(time_crit, 0)], logic="and")
    
    with pytest.raises(ValueError, match="workers must be a positive integer"):
        MultiCriterion(criteria=[(time_crit, "not_an_int")], logic="and")


def test_multi_criterion_and_logic(mocker):
    import datetime
    
    # Mock find_spec for both pytz and psutil
    mock_spec = mocker.MagicMock()
    mocker.patch('importlib.util.find_spec', return_value=mock_spec)
    
    time_crit = TimeCriterion(
        worker_count=4, 
        active_start=datetime.datetime(2024, 1, 1, 22, 0), 
        active_end=datetime.datetime(2024, 1, 1, 3, 0)
    )
    memory_crit = MemoryCriterion(threshold=80.0, workers=6)
    
    # Multi-criterion with AND logic - should return max workers when all conditions met
    multi = MultiCriterion(criteria=[(time_crit, 4), (memory_crit, 6)], logic="and")
    
    # Mock time in range and memory above threshold
    import pytz
    
    tz = pytz.UTC
    mock_now = datetime.datetime(2024, 1, 1, 23, 0, 0, tzinfo=tz)
    
    mock_datetime_module = mocker.MagicMock()
    mock_datetime_module.now.return_value = mock_now
    mocker.patch('adaptive_executor.criteria.datetime', mock_datetime_module)
    
    mock_memory = mocker.MagicMock()
    mock_memory.percent = 85.0
    
    mock_psutil = mocker.MagicMock()
    mock_psutil.virtual_memory.return_value = mock_memory
    mocker.patch('adaptive_executor.criteria.psutil', mock_psutil)
    
    result = multi.max_workers()
    # Both conditions met, should return max(4, 6) = 6
    assert result == 6


def test_multi_criterion_or_logic(mocker):
    import datetime
    
    # Mock find_spec for both pytz and psutil
    mock_spec = mocker.MagicMock()
    mocker.patch('importlib.util.find_spec', return_value=mock_spec)
    
    time_crit = TimeCriterion(
        worker_count=4, 
        active_start=datetime.datetime(2024, 1, 1, 22, 0), 
        active_end=datetime.datetime(2024, 1, 1, 3, 0)
    )
    memory_crit = MemoryCriterion(threshold=80.0, workers=6)
    
    # Multi-criterion with OR logic - should return workers from first satisfied criterion
    multi = MultiCriterion(criteria=[(time_crit, 4), (memory_crit, 6)], logic="or")
    
    # Mock time in range but memory below threshold
    import pytz
    
    tz = pytz.UTC
    mock_now = datetime.datetime(2024, 1, 1, 23, 0, 0, tzinfo=tz)
    
    mock_datetime_module = mocker.MagicMock()
    mock_datetime_module.now.return_value = mock_now
    mocker.patch('adaptive_executor.criteria.datetime', mock_datetime_module)
    
    mock_memory = mocker.MagicMock()
    mock_memory.percent = 70.0
    
    mock_psutil = mocker.MagicMock()
    mock_psutil.virtual_memory.return_value = mock_memory
    mocker.patch('adaptive_executor.criteria.psutil', mock_psutil)
    
    result = multi.max_workers()
    # Time condition met, should return 4
    assert result == 4


@pytest.mark.integration
def test_complex_scenario_between_time_and_memory(mocker):
    """Test: Between 10PM-3AM if memory > 80% then 2 workers"""
    
    import datetime
    
    # Mock find_spec for both pytz and psutil
    mock_spec = mocker.MagicMock()
    mocker.patch('importlib.util.find_spec', return_value=mock_spec)
    
    # Time criterion for 10PM-3AM
    time_crit = TimeCriterion(
        worker_count=2, 
        active_start=datetime.datetime(2024, 1, 1, 22, 0), 
        active_end=datetime.datetime(2024, 1, 1, 3, 0)
    )
    
    # Memory criterion for >80%
    memory_crit = MemoryCriterion(threshold=80.0, workers=2)
    
    # Multi-criterion with AND logic
    multi = MultiCriterion(criteria=[(time_crit, 2), (memory_crit, 2)], logic="and")
    
    # Mock time in range (11PM)
    import pytz
    
    tz = pytz.UTC
    mock_now = datetime.datetime(2024, 1, 1, 23, 0, 0, tzinfo=tz)
    
    mock_datetime_module = mocker.MagicMock()
    mock_datetime_module.now.return_value = mock_now
    mocker.patch('adaptive_executor.criteria.datetime', mock_datetime_module)
    
    # Mock memory > 80%
    mock_memory = mocker.MagicMock()
    mock_memory.percent = 85.0
    
    mock_psutil = mocker.MagicMock()
    mock_psutil.virtual_memory.return_value = mock_memory
    mocker.patch('adaptive_executor.criteria.psutil', mock_psutil)
    
    result = multi.max_workers()
    # Both conditions met, should return 2
    assert result == 2


def test_serialization_error_handling():
    # Test missing required fields
    with pytest.raises(KeyError):
        TimeCriterion.from_dict({"worker_count": 8})  # Missing active_start, active_end, timezone
    
    # Test invalid JSON
    with pytest.raises(Exception):  # Could be JSONDecodeError or other
        TimeCriterion.from_json("invalid json")


def test_conditional_criterion_serialization(mocker):
    import datetime
    
    # Mock find_spec for both pytz and psutil
    mock_spec = mocker.MagicMock()
    mocker.patch('importlib.util.find_spec', return_value=mock_spec)
    
    time_crit = TimeCriterion(
        worker_count=8, 
        active_start=datetime.datetime(2024, 1, 1, 22, 0), 
        active_end=datetime.datetime(2024, 1, 1, 3, 0)
    )
    memory_crit = MemoryCriterion(threshold=80.0, workers=4)
    
    conditional = ConditionalCriterion(
        condition_criterion=time_crit,
        action_criterion=memory_crit,
        workers=6
    )
    
    # Test serialization
    data = conditional.to_dict()
    assert data["type"] == "ConditionalCriterion"
    assert data["workers"] == 6
    
    # Test deserialization
    restored = ConditionalCriterion.from_dict(data)
    assert restored.workers == 6
    assert isinstance(restored.condition_criterion, TimeCriterion)
    assert isinstance(restored.action_criterion, MemoryCriterion)