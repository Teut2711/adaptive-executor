import pytest

from adaptive_executor.criteria import (
    ConditionalCriterion,
    MultiCriterion,
    ScalingCriterion,
)


class StaticCriterion(ScalingCriterion):
    def __init__(self, value):
        self.value = value

    def max_workers(self):
        return self.value

    def to_dict(self):
        return {"type": "StaticCriterion", "value": self.value}

    @classmethod
    def from_dict(cls, data):
        return cls(data["value"])


class ExplodingMaxCriterion(ScalingCriterion):
    def max_workers(self):
        raise RuntimeError("boom")

    def to_dict(self):
        return {"type": "ExplodingMaxCriterion"}

    @classmethod
    def from_dict(cls, data):
        return cls()


class ExplodingToDictCriterion(ScalingCriterion):
    def max_workers(self):
        return 2

    def to_dict(self):
        raise ValueError("cannot serialize")

    @classmethod
    def from_dict(cls, data):
        return cls()


def test_multi_criterion_runtime_invalid_logic_returns_one():
    multi = MultiCriterion(criteria=[(StaticCriterion(2), 4)], logic="and")
    multi.logic = "invalid"
    assert multi.max_workers() == 1


def test_multi_criterion_exception_in_max_workers_returns_one():
    multi = MultiCriterion(criteria=[(ExplodingMaxCriterion(), 4)], logic="and")
    assert multi.max_workers() == 1


def test_multi_criterion_to_dict_propagates_serialization_error():
    multi = MultiCriterion(criteria=[(ExplodingToDictCriterion(), 3)], logic="and")
    with pytest.raises(ValueError, match="cannot serialize"):
        multi.to_dict()


def test_multi_criterion_from_dict_unknown_type_raises():
    with pytest.raises(ValueError, match="Unknown criterion type"):
        MultiCriterion.from_dict(
            {
                "criteria": [
                    {
                        "criterion": {"type": "UnknownCriterion"},
                        "workers": 3,
                    }
                ],
                "logic": "and",
            }
        )


def test_multi_criterion_from_dict_missing_key_raises():
    with pytest.raises(KeyError):
        MultiCriterion.from_dict({"logic": "and"})


def test_multi_criterion_from_dict_supports_nested_multi():
    data = {
        "type": "MultiCriterion",
        "criteria": [
            {
                "criterion": {
                    "type": "MultiCriterion",
                    "criteria": [
                        {
                            "criterion": {
                                "type": "TimeCriterion",
                                "worker_count": 5,
                                "active_start": "09:00:00",
                                "active_end": "17:00:00",
                                "timezone": "UTC",
                            },
                            "workers": 5,
                        }
                    ],
                    "logic": "and",
                },
                "workers": 5,
            }
        ],
        "logic": "and",
    }

    restored = MultiCriterion.from_dict(data)
    assert isinstance(restored, MultiCriterion)
    assert isinstance(restored.criteria[0][0], MultiCriterion)


def test_conditional_criterion_validation_errors():
    valid = StaticCriterion(2)

    with pytest.raises(
        TypeError, match="condition_criterion must be a ScalingCriterion"
    ):
        ConditionalCriterion("bad", valid, 2)

    with pytest.raises(TypeError, match="action_criterion must be a ScalingCriterion"):
        ConditionalCriterion(valid, "bad", 2)

    with pytest.raises(ValueError, match="workers must be a positive integer"):
        ConditionalCriterion(valid, valid, 0)


def test_conditional_criterion_max_workers_condition_met():
    conditional = ConditionalCriterion(
        condition_criterion=StaticCriterion(2),
        action_criterion=StaticCriterion(9),
        workers=6,
    )
    assert conditional.max_workers() == 6


def test_conditional_criterion_max_workers_condition_not_met_uses_action():
    conditional = ConditionalCriterion(
        condition_criterion=StaticCriterion(1),
        action_criterion=StaticCriterion(4),
        workers=6,
    )
    assert conditional.max_workers() == 4


def test_conditional_criterion_max_workers_exception_returns_one():
    conditional = ConditionalCriterion(
        condition_criterion=ExplodingMaxCriterion(),
        action_criterion=StaticCriterion(4),
        workers=6,
    )
    assert conditional.max_workers() == 1


def test_conditional_criterion_to_dict_propagates_error():
    conditional = ConditionalCriterion(
        condition_criterion=ExplodingToDictCriterion(),
        action_criterion=StaticCriterion(3),
        workers=6,
    )
    with pytest.raises(ValueError, match="cannot serialize"):
        conditional.to_dict()


def test_conditional_criterion_from_dict_missing_key_raises():
    with pytest.raises(KeyError):
        ConditionalCriterion.from_dict({"workers": 3})
