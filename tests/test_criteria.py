import pytest
from adaptive_executor.criteria import (
    ScalingCriterion,
    TimeCriterion,
    CpuCriterion,
    MemoryCriterion,
)


class TestScalingCriterion:
    def test_base_class_raises_not_implemented(self):
        criterion = ScalingCriterion()
        with pytest.raises(NotImplementedError):
            criterion.max_workers()


class TestTimeCriterion:
    def test_default_initialization(self):
        criterion = TimeCriterion()
        assert criterion.day_workers == 2
        assert criterion.night_workers == 12
        assert criterion.night_start == 22
        assert criterion.night_end == 3
        assert criterion.tz.zone == "Asia/Kolkata"

    def test_custom_initialization(self):
        criterion = TimeCriterion(
            day_workers=5,
            night_workers=15,
            night_start=20,
            night_end=6,
            tz="UTC"
        )
        assert criterion.day_workers == 5
        assert criterion.night_workers == 15
        assert criterion.night_start == 20
        assert criterion.night_end == 6
        assert criterion.tz.zone == "UTC"

    @pytest.mark.parametrize("hour,expected", [
        (10, 2),   # Daytime
        (23, 12),  # Nighttime before midnight
        (2, 12),   # Nighttime after midnight
        (22, 12),  # Exactly night start
        (3, 12),   # Exactly night end
    ])
    def test_time_based_scaling(self, hour, expected):
        with pytest.MonkeyPatch() as mock_datetime:
            import datetime
            mock_now = datetime.datetime(2024, 1, 1, hour, 0, 0)
            mock_datetime.datetime.now.return_value = mock_now
            
            criterion = TimeCriterion()
            result = criterion.max_workers()
            assert result == expected

    @pytest.fixture
    def sample_criterion(self):
        return TimeCriterion(day_workers=3, night_workers=8)

    def test_with_fixture(self, sample_criterion):
        assert sample_criterion.day_workers == 3
        assert sample_criterion.night_workers == 8

    @pytest.mark.parametrize("hour,expected", [
        (23, 12),  # Nighttime before midnight
        (2, 12),   # Nighttime after midnight
        (22, 12),  # Exactly night start
        (3, 12),   # Exactly night end
    ])
    def test_nighttime_scenarios_before_midnight(self, hour, expected):
        with pytest.MonkeyPatch() as mock_datetime:
            import datetime
            mock_now = datetime.datetime(2024, 1, 1, hour, 0, 0)
            mock_datetime.datetime.now.return_value = mock_now
            
            criterion = TimeCriterion()
            result = criterion.max_workers()
            assert result == expected

    @pytest.mark.parametrize("hour,expected", [
        (10, 2),   # Daytime
        (23, 12),  # Nighttime before midnight
        (2, 12),   # Nighttime after midnight
        (22, 12),  # Exactly night start
        (3, 12),   # Exactly night end
    ])
    def test_edge_cases(self, hour, expected):
        with pytest.MonkeyPatch() as mock_datetime:
            import datetime
            mock_now = datetime.datetime(2024, 1, 1, hour, 0, 0)
            mock_datetime.datetime.now.return_value = mock_now
            
            criterion = TimeCriterion()
            result = criterion.max_workers()
            assert result == expected


class TestCpuCriterion:
    def test_default_initialization(self):
        criterion = CpuCriterion()
        assert criterion.threshold == 75

    def test_custom_initialization(self):
        criterion = CpuCriterion(threshold=80)
        assert criterion.threshold == 80

    @patch('adaptive_executor.criteria.psutil.cpu_percent')
    def test_high_cpu_usage(self, mock_cpu_percent):
        mock_cpu_percent.return_value = 80
        criterion = CpuCriterion(threshold=75)
        assert criterion.max_workers() == 2

    @patch('adaptive_executor.criteria.psutil.cpu_percent')
    def test_low_cpu_usage(self, mock_cpu_percent):
        mock_cpu_percent.return_value = 50
        criterion = CpuCriterion(threshold=75)
        assert criterion.max_workers() == 12

    @pytest.mark.parametrize("cpu_percent,expected", [
        (50, 12),  # Low CPU
        (75, 12),  # At threshold
        (80, 2),   # Above threshold
        (90, 2),   # High CPU
    ])
    def test_cpu_based_scaling(self, cpu_percent, expected):
        with pytest.MonkeyPatch() as mock_psutil:
            mock_psutil.cpu_percent.return_value = cpu_percent
            
            import sys
            sys.modules['psutil'] = mock_psutil
            
            criterion = CpuCriterion()
            result = criterion.max_workers()
            assert result == expected


class TestMemoryCriterion:
    def test_default_initialization(self):
        criterion = MemoryCriterion()
        assert criterion.threshold == 80

    def test_custom_initialization(self):
        criterion = MemoryCriterion(threshold=85)
        assert criterion.threshold == 85

    @patch('adaptive_executor.criteria.psutil.virtual_memory')
    def test_high_memory_usage(self, mock_virtual_memory):
        mock_memory = MagicMock()
        mock_memory.percent = 85
        mock_virtual_memory.return_value = mock_memory
        
        criterion = MemoryCriterion(threshold=80)
        assert criterion.max_workers() == 2

    @patch('adaptive_executor.criteria.psutil.virtual_memory')
    def test_low_memory_usage(self, mock_virtual_memory):
        mock_memory = MagicMock()
        mock_memory.percent = 60
        mock_virtual_memory.return_value = mock_memory
        
        criterion = MemoryCriterion(threshold=80)
        assert criterion.max_workers() == 12

    @patch('adaptive_executor.criteria.psutil.virtual_memory')
    def test_threshold_exact(self, mock_virtual_memory):
        mock_memory = MagicMock()
        mock_memory.percent = 80
        mock_virtual_memory.return_value = mock_memory
        
        criterion = MemoryCriterion(threshold=80)
        assert criterion.max_workers() == 12
