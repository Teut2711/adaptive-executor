import pytest
from unittest.mock import MagicMock

from adaptive_executor.policies import MultiCriterionPolicy
from adaptive_executor.criteria import ScalingCriterion


def test_initialization(mocker):
    criteria = [mocker.MagicMock(spec=ScalingCriterion) for _ in range(3)]
    policy = MultiCriterionPolicy(criteria, hard_cap=10)

    assert policy.criteria == criteria
    assert policy.hard_cap == 10


def test_target_workers_with_single_criterion(mocker):
    criterion = mocker.MagicMock(spec=ScalingCriterion)
    criterion.max_workers.return_value = 5

    policy = MultiCriterionPolicy([criterion], hard_cap=10)

    assert policy.target_workers() == 5


def test_target_workers_with_multiple_criteria_uses_minimum(mocker):
    c1 = mocker.MagicMock(spec=ScalingCriterion)
    c1.max_workers.return_value = 5

    c2 = mocker.MagicMock(spec=ScalingCriterion)
    c2.max_workers.return_value = 8

    c3 = mocker.MagicMock(spec=ScalingCriterion)
    c3.max_workers.return_value = 3

    policy = MultiCriterionPolicy([c1, c2, c3], hard_cap=10)

    assert policy.target_workers() == 3


def test_target_workers_respects_hard_cap(mocker):
    c1 = mocker.MagicMock(spec=ScalingCriterion)
    c1.max_workers.return_value = 15

    c2 = mocker.MagicMock(spec=ScalingCriterion)
    c2.max_workers.return_value = 20

    policy = MultiCriterionPolicy([c1, c2], hard_cap=10)

    assert policy.target_workers() == 10


def test_target_workers_is_at_least_one(mocker):
    c1 = mocker.MagicMock(spec=ScalingCriterion)
    c1.max_workers.return_value = 0

    c2 = mocker.MagicMock(spec=ScalingCriterion)
    c2.max_workers.return_value = -5

    policy = MultiCriterionPolicy([c1, c2], hard_cap=10)

    assert policy.target_workers() == 1


def test_initialization_with_empty_criteria_raises(mocker):
    with pytest.raises(ValueError, match="At least one criterion is required"):
        MultiCriterionPolicy([], hard_cap=10)


def test_target_workers_calls_all_criteria(mocker):
    c1 = mocker.MagicMock(spec=ScalingCriterion)
    c1.max_workers.return_value = 5

    c2 = mocker.MagicMock(spec=ScalingCriterion)
    c2.max_workers.return_value = 8

    policy = MultiCriterionPolicy([c1, c2], hard_cap=10)
    policy.target_workers()

    c1.max_workers.assert_called_once()
    c2.max_workers.assert_called_once()
