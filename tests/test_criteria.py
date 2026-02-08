import pytest
from unittest.mock import patch, MagicMock

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
            tz="UTC",
        )
        assert criterion.day_workers == 5
        assert criterion.night_workers == 15
        assert criterion.night_start == 20
        assert criterion.night_end == 6
        assert criterion.tz.zone == "UTC"

    @patch('adaptive_executor.criteria.datetime')
    def test_daytime_workers(self, mock_datetime):
        mock_now = MagicMock()
        mock_now.hour = 10
        mock_datetime.now.return_value = mock_now
        
        criterion = TimeCriterion()
        assert criterion.max_workers() == 2

    @patch('adaptive_executor.criteria.datetime')
    def test_nighttime_workers_before_midnight(self, mock_datetime):
        mock_now = MagicMock()
        mock_now.hour = 23
        mock_datetime.now.return_value = mock_now
        
        criterion = TimeCriterion()
        assert criterion.max_workers() == 12

    @patch('adaptive_executor.criteria.datetime')
    def test_nighttime_workers_after_midnight(self, mock_datetime):
        mock_now = MagicMock()
        mock_now.hour = 2
        mock_datetime.now.return_value = mock_now
        
        criterion = TimeCriterion()
        assert criterion.max_workers() == 12

    @patch('adaptive_executor.criteria.datetime')
    def test_edge_case_night_start(self, mock_datetime):
        mock_now = MagicMock()
        mock_now.hour = 22
        mock_datetime.now.return_value = mock_now
        
        criterion = TimeCriterion()
        assert criterion.max_workers() == 12

    @patch('adaptive_executor.criteria.datetime')
    def test_edge_case_night_end(self, mock_datetime):
        mock_now = MagicMock()
        mock_now.hour = 3
        mock_datetime.now.return_value = mock_now
        
        criterion = TimeCriterion()
        assert criterion.max_workers() == 12


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

    @patch('adaptive_executor.criteria.psutil.cpu_percent')
    def test_threshold_exact(self, mock_cpu_percent):
        mock_cpu_percent.return_value = 75
        criterion = CpuCriterion(threshold=75)
        assert criterion.max_workers() == 12


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
