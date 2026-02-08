import pytest
from unittest.mock import MagicMock

from adaptive_executor.policies import MultiCriterionPolicy
from adaptive_executor.criteria import ScalingCriterion


class TestMultiCriterionPolicy:
    def test_initialization(self):
        criteria = [MagicMock(spec=ScalingCriterion) for _ in range(3)]
        policy = MultiCriterionPolicy(criteria, hard_cap=10)
        
        assert policy.criteria == criteria
        assert policy.hard_cap == 10

    def test_target_workers_with_single_criterion(self):
        mock_criterion = MagicMock(spec=ScalingCriterion)
        mock_criterion.max_workers.return_value = 5
        
        policy = MultiCriterionPolicy([mock_criterion], hard_cap=10)
        assert policy.target_workers() == 5

    def test_target_workers_with_multiple_criteria(self):
        mock_criterion1 = MagicMock(spec=ScalingCriterion)
        mock_criterion1.max_workers.return_value = 5
        mock_criterion2 = MagicMock(spec=ScalingCriterion)
        mock_criterion2.max_workers.return_value = 8
        mock_criterion3 = MagicMock(spec=ScalingCriterion)
        mock_criterion3.max_workers.return_value = 3
        
        policy = MultiCriterionPolicy([mock_criterion1, mock_criterion2, mock_criterion3], hard_cap=10)
        assert policy.target_workers() == 3

    def test_target_workers_respects_hard_cap(self):
        mock_criterion1 = MagicMock(spec=ScalingCriterion)
        mock_criterion1.max_workers.return_value = 15
        mock_criterion2 = MagicMock(spec=ScalingCriterion)
        mock_criterion2.max_workers.return_value = 20
        
        policy = MultiCriterionPolicy([mock_criterion1, mock_criterion2], hard_cap=10)
        assert policy.target_workers() == 10

    def test_target_workers_minimum_one(self):
        mock_criterion1 = MagicMock(spec=ScalingCriterion)
        mock_criterion1.max_workers.return_value = 0
        mock_criterion2 = MagicMock(spec=ScalingCriterion)
        mock_criterion2.max_workers.return_value = -5
        
        policy = MultiCriterionPolicy([mock_criterion1, mock_criterion2], hard_cap=10)
        assert policy.target_workers() == 1

    def test_target_workers_empty_criteria_list(self):
        policy = MultiCriterionPolicy([], hard_cap=10)
        with pytest.raises(ValueError):
            policy.target_workers()

    def test_target_workers_calls_all_criteria(self):
        mock_criterion1 = MagicMock(spec=ScalingCriterion)
        mock_criterion1.max_workers.return_value = 5
        mock_criterion2 = MagicMock(spec=ScalingCriterion)
        mock_criterion2.max_workers.return_value = 8
        
        policy = MultiCriterionPolicy([mock_criterion1, mock_criterion2], hard_cap=10)
        policy.target_workers()
        
        mock_criterion1.max_workers.assert_called_once()
        mock_criterion2.max_workers.assert_called_once()
