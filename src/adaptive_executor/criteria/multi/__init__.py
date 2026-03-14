"""Multi-criteria scaling implementations."""

from .conditional import ConditionalCriterion
from .multi import MultiCriterion

__all__ = ["MultiCriterion", "ConditionalCriterion"]


def from_dict(data):
    """Create a criterion from dictionary data."""
    criterion_type = data.get("type")

    if criterion_type == "MultiCriterion":
        return MultiCriterion.from_dict(data)
    elif criterion_type == "ConditionalCriterion":
        return ConditionalCriterion.from_dict(data)
    else:
        raise ValueError(f"Unknown criterion type: {criterion_type}")
