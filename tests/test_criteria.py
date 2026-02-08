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
    criterion = TimeCriterion(workers=8, time_start=22, time_end=3, tz="UTC")
    assert criterion.workers == 8
    assert criterion.time_start == 22
    assert criterion.time_end == 3
    assert criterion.tz.zone == "UTC"


def test_time_criterion_validation():
    # Test invalid time ranges
    with pytest.raises(ValueError, match="time_start and time_end must be between 0 and 23"):
        TimeCriterion(workers=8, time_start=25, time_end=3)
    
    with pytest.raises(ValueError, match="time_start and time_end must be between 0 and 23"):
        TimeCriterion(workers=8, time_start=22, time_end=-1)
    
    # Test invalid workers
    with pytest.raises(ValueError, match="workers must be at least 1"):
        TimeCriterion(workers=0, time_start=22, time_end=3)


def test_time_criterion_missing_pytz():
    import sys
    original_modules = sys.modules.copy()
    
    # Remove pytz from modules to simulate missing dependency
    if 'pytz' in sys.modules:
        del sys.modules['pytz']
    if 'adaptive_executor.criteria' in sys.modules:
        del sys.modules['adaptive_executor.criteria']
    
    # Mock importlib.util.find_spec to return None
    with pytest.mock.patch('importlib.util.find_spec') as mock_find_spec:
        mock_find_spec.return_value = None
        
        with pytest.raises(ImportError, match="TimeCriterion requires 'pytz' package"):
            TimeCriterion(workers=8, time_start=22, time_end=3)
    
    # Restore modules
    sys.modules.update(original_modules)


@pytest.mark.parametrize("hour,expected", [
    (10, 1),   # Daytime (outside range)
    (23, 8),  # Nighttime (in range)
    (2, 8),   # After midnight (in range)
    (22, 8),  # Exactly at start
    (3, 8),   # Exactly at end
])
def test_time_criterion_scaling(hour, expected, mocker):
    import datetime
    mock_now = datetime.datetime(2024, 1, 1, hour, 0, 0)
    with mocker.patch('datetime.datetime.now') as mock_datetime:
        mock_datetime.return_value = mock_now
        
        criterion = TimeCriterion(workers=8, time_start=22, time_end=3)
        result = criterion.max_workers()
        assert result == expected


def test_cpu_criterion_initialization():
    criterion = CpuCriterion(threshold=80.0, workers=4)
    assert criterion.threshold == 80.0
    assert criterion.workers == 4


def test_cpu_criterion_missing_psutil():
    with pytest.mock.patch('importlib.util.find_spec') as mock_find_spec:
        mock_find_spec.return_value = None
        
        with pytest.raises(ImportError, match="CpuCriterion requires 'psutil' package"):
            CpuCriterion(threshold=80.0, workers=4)


@pytest.mark.parametrize("cpu_percent,expected", [
    (50.0, 1),  # Below threshold
    (75.0, 1),  # At threshold
    (80.0, 4),  # Above threshold
    (90.0, 4),  # High CPU
])
def test_cpu_criterion_scaling(cpu_percent, expected, mocker):
    mocker.patch('adaptive_executor.criteria.psutil').cpu_percent.return_value = cpu_percent
    
    criterion = CpuCriterion(threshold=75.0, workers=4)
    result = criterion.max_workers()
    assert result == expected


def test_memory_criterion_initialization():
    criterion = MemoryCriterion(threshold=85.0, workers=6)
    assert criterion.threshold == 85.0
    assert criterion.workers == 6


def test_memory_criterion_missing_psutil():
    with pytest.mock.patch('importlib.util.find_spec') as mock_find_spec:
        mock_find_spec.return_value = None
        
        with pytest.raises(ImportError, match="MemoryCriterion requires 'psutil' package"):
            MemoryCriterion(threshold=80.0, workers=6)


@pytest.mark.parametrize("memory_percent,expected", [
    (60.0, 1),  # Below threshold
    (80.0, 1),  # At threshold
    (85.0, 6),  # Above threshold
    (95.0, 6),  # High memory
])
def test_memory_criterion_scaling(memory_percent, expected, mocker):
    mock_memory = mocker.MagicMock()
    mock_memory.percent = memory_percent
    mocker.patch('adaptive_executor.criteria.psutil.virtual_memory', return_value=mock_memory)
    
    criterion = MemoryCriterion(threshold=80.0, workers=6)
    result = criterion.max_workers()
    assert result == expected


def test_time_criterion_serialization():
    criterion = TimeCriterion(workers=8, time_start=22, time_end=3, tz="UTC")
    
    # Test to_dict
    data = criterion.to_dict()
    expected = {
        "type": "TimeCriterion",
        "workers": 8,
        "time_start": 22,
        "time_end": 3,
        "tz": "UTC"
    }
    assert data == expected
    
    # Test from_dict
    restored = TimeCriterion.from_dict(data)
    assert restored.workers == 8
    assert restored.time_start == 22
    assert restored.time_end == 3
    assert restored.tz.zone == "UTC"
    
    # Test JSON serialization
    json_str = criterion.to_json()
    restored_from_json = TimeCriterion.from_json(json_str)
    assert restored_from_json.workers == 8


def test_multi_criterion_validation():
    time_crit = TimeCriterion(workers=2, time_start=22, time_end=3)
    
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


def test_multi_criterion_and_logic():
    time_crit = TimeCriterion(workers=4, time_start=22, time_end=3)
    memory_crit = MemoryCriterion(threshold=80.0, workers=6)
    
    # Multi-criterion with AND logic - should return max workers when all conditions met
    multi = MultiCriterion(criteria=[(time_crit, 4), (memory_crit, 6)], logic="and")
    
    # Mock time in range and memory above threshold
    import datetime
    mock_now = datetime.datetime(2024, 1, 1, 23, 0, 0)
    
    with pytest.mock.patch('datetime.datetime.now') as mock_datetime:
        mock_datetime.return_value = mock_now
        
        mock_memory = pytest.mock.MagicMock()
        mock_memory.percent = 85.0
        
        with pytest.mock.patch('adaptive_executor.criteria.psutil') as mock_psutil:
            mock_psutil.virtual_memory.return_value = mock_memory
            
            result = multi.max_workers()
            # Both conditions met, should return max(4, 6) = 6
            assert result == 6


def test_multi_criterion_or_logic():
    time_crit = TimeCriterion(workers=4, time_start=22, time_end=3)
    memory_crit = MemoryCriterion(threshold=80.0, workers=6)
    
    # Multi-criterion with OR logic - should return workers from first satisfied criterion
    multi = MultiCriterion(criteria=[(time_crit, 4), (memory_crit, 6)], logic="or")
    
    # Mock time in range but memory below threshold
    import datetime
    mock_now = datetime.datetime(2024, 1, 1, 23, 0, 0)
    
    with pytest.mock.patch('datetime.datetime.now') as mock_datetime:
        mock_datetime.return_value = mock_now
        
        mock_memory = pytest.mock.MagicMock()
        mock_memory.percent = 70.0
        
        with pytest.mock.patch('adaptive_executor.criteria.psutil') as mock_psutil:
            mock_psutil.virtual_memory.return_value = mock_memory
            
            result = multi.max_workers()
            # Time condition met, should return 4
            assert result == 4


@pytest.mark.integration
def test_complex_scenario_between_time_and_memory():
    """Test: Between 10PM-3AM if memory > 80% then 2 workers"""
    
    # Time criterion for 10PM-3AM
    time_crit = TimeCriterion(workers=2, time_start=22, time_end=3)
    
    # Memory criterion for >80%
    memory_crit = MemoryCriterion(threshold=80.0, workers=2)
    
    # Multi-criterion with AND logic
    multi = MultiCriterion(criteria=[(time_crit, 2), (memory_crit, 2)], logic="and")
    
    # Mock time in range (11PM)
    import datetime
    mock_now = datetime.datetime(2024, 1, 1, 23, 0, 0)
    
    with pytest.mock.patch('datetime.datetime.now') as mock_datetime:
        mock_datetime.return_value = mock_now
        
        # Mock memory > 80%
        mock_memory = pytest.mock.MagicMock()
        mock_memory.percent = 85.0
        
        with pytest.mock.patch('adaptive_executor.criteria.psutil') as mock_psutil:
            mock_psutil.virtual_memory.return_value = mock_memory
            
            result = multi.max_workers()
            # Both conditions met, should return 2
            assert result == 2


def test_serialization_error_handling():
    # Test missing required fields
    with pytest.raises(KeyError):
        TimeCriterion.from_dict({"workers": 8})  # Missing time_start, time_end, tz
    
    # Test invalid JSON
    with pytest.raises(Exception):  # Could be JSONDecodeError or other
        TimeCriterion.from_json("invalid json")


def test_conditional_criterion_serialization():
    time_crit = TimeCriterion(workers=8, time_start=22, time_end=3)
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