"""Scaling criteria for adaptive executor."""
from typing import Any, Dict

from .base import ScalingCriterion
from .time import TimeCriterion
from .datetime import DateTimeCriterion
from .cpu import CpuCriterion
from .memory import MemoryCriterion
from .multi import MultiCriterion, ConditionalCriterion

# Also expose the modules for patching
from . import time
from . import datetime
from . import cpu
from . import memory
from . import multi


def from_dict(data: Dict[str, Any]) -> ScalingCriterion:
    """Create a criterion from a dictionary.
    
    Args:
        data: Dictionary containing serialized criterion data
        
    Returns:
        ScalingCriterion: An instance of the appropriate criterion class
        
    Raises:
        ValueError: If the criterion type is unknown
    """
    criterion_type = data.get("type")
    
    if criterion_type == "TimeCriterion":
        return TimeCriterion.from_dict(data)
    elif criterion_type == "DateTimeCriterion":
        return DateTimeCriterion.from_dict(data)
    elif criterion_type == "CpuCriterion":
        return CpuCriterion.from_dict(data)
    elif criterion_type == "MemoryCriterion":
        return MemoryCriterion.from_dict(data)
    elif criterion_type == "MultiCriterion":
        return MultiCriterion.from_dict(data)
    elif criterion_type == "ConditionalCriterion":
        return ConditionalCriterion.from_dict(data)
    else:
        raise ValueError(f"Unknown criterion type: {criterion_type}")


__all__ = [
    'ScalingCriterion',
    'TimeCriterion',
    'DateTimeCriterion',
    'CpuCriterion',
    'MemoryCriterion',
    'MultiCriterion',
    'ConditionalCriterion',
    'from_dict',
    'time',
    'datetime',
    'cpu',
    'memory',
    'multi'
]