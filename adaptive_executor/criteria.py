
import importlib.util
import json
from typing import List, Tuple, Dict, Any


class ScalingCriterion:
    def max_workers(self) -> int:
        raise NotImplementedError
    
    def to_dict(self) -> Dict[str, Any]:
        """Serialize criterion to dictionary"""
        raise NotImplementedError
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ScalingCriterion":
        """Deserialize criterion from dictionary"""
        raise NotImplementedError
    
    def to_json(self) -> str:
        """Serialize criterion to JSON string"""
        return json.dumps(self.to_dict())
    
    @classmethod
    def from_json(cls, json_str: str) -> "ScalingCriterion":
        """Deserialize criterion from JSON string"""
        data = json.loads(json_str)
        return cls.from_dict(data)


class TimeCriterion(ScalingCriterion):
    def __init__(
        self,
        workers: int,
        time_start: int,
        time_end: int,
        tz: str = "UTC",
    ):
        if not importlib.util.find_spec("pytz"):
            raise ImportError("TimeCriterion requires 'pytz' package. Install with: pip install adaptive-executor[time]")
        
        if not (0 <= time_start <= 23) or not (0 <= time_end <= 23):
            raise ValueError("time_start and time_end must be between 0 and 23")
        
        if workers < 1:
            raise ValueError("workers must be at least 1")
        
        import pytz
        self.workers = workers
        self.time_start = time_start
        self.time_end = time_end
        self.tz = pytz.timezone(tz)

    def max_workers(self) -> int:
        from datetime import datetime
        h = datetime.now(self.tz).hour
        if h >= self.time_start or h < self.time_end:
            return self.workers
        return 1  # Minimum workers outside time range
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "type": "TimeCriterion",
            "workers": self.workers,
            "time_start": self.time_start,
            "time_end": self.time_end,
            "tz": self.tz.zone
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "TimeCriterion":
        return cls(
            workers=data["workers"],
            time_start=data["time_start"],
            time_end=data["time_end"],
            tz=data["tz"]
        )


class CpuCriterion(ScalingCriterion):
    def __init__(self, threshold: float, workers: int):
        if not importlib.util.find_spec("psutil"):
            raise ImportError("CpuCriterion requires 'psutil' package. Install with: pip install adaptive-executor[cpu]")
        
        self.threshold = threshold
        self.workers = workers

    def max_workers(self) -> int:
        import psutil
        return self.workers if psutil.cpu_percent() >= self.threshold else 1
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "type": "CpuCriterion",
            "threshold": self.threshold,
            "workers": self.workers
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "CpuCriterion":
        return cls(threshold=data["threshold"], workers=data["workers"])


class MemoryCriterion(ScalingCriterion):
    def __init__(self, threshold: float, workers: int):
        if not importlib.util.find_spec("psutil"):
            raise ImportError("MemoryCriterion requires 'psutil' package. Install with: pip install adaptive-executor[cpu]")
        
        self.threshold = threshold
        self.workers = workers

    def max_workers(self) -> int:
        import psutil
        return self.workers if psutil.virtual_memory().percent >= self.threshold else 1
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "type": "MemoryCriterion",
            "threshold": self.threshold,
            "workers": self.workers
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "MemoryCriterion":
        return cls(threshold=data["threshold"], workers=data["workers"])


class MultiCriterion(ScalingCriterion):
    def __init__(self, criteria: List[Tuple[ScalingCriterion, int]], logic: str = "and"):
        """
        MultiCriterion allows combining multiple criteria with custom logic.
        
        Args:
            criteria: List of criteria tuples (criterion, workers)
            logic: "and" or "or" for combining conditions
        """
        if logic not in ["and", "or"]:
            raise ValueError("logic must be 'and' or 'or'")
        
        if not criteria:
            raise ValueError("criteria cannot be empty")
        
        for criterion, workers in criteria:
            if not isinstance(criterion, ScalingCriterion):
                raise TypeError("All criteria must be ScalingCriterion instances")
            if not isinstance(workers, int) or workers < 1:
                raise ValueError("workers must be a positive integer")
        
        self.criteria = criteria
        self.logic = logic

    def max_workers(self) -> int:
        if self.logic == "and":
            # All conditions must be met
            for criterion, workers in self.criteria:
                if criterion.max_workers() == 1:
                    return 1
            # All conditions met, return maximum workers from all criteria
            return max(workers for criterion, workers in self.criteria) if self.criteria else 1
        elif self.logic == "or":
            # Any condition met
            for criterion, workers in self.criteria:
                if criterion.max_workers() > 1:
                    return workers
            return 1
        return 1
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "type": "MultiCriterion",
            "criteria": [(criterion.to_dict(), workers) for criterion, workers in self.criteria],
            "logic": self.logic
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "MultiCriterion":
        criteria = []
        for criterion_data, workers in data["criteria"]:
            criterion_type = criterion_data["type"]
            if criterion_type == "TimeCriterion":
                criterion = TimeCriterion.from_dict(criterion_data)
            elif criterion_type == "CpuCriterion":
                criterion = CpuCriterion.from_dict(criterion_data)
            elif criterion_type == "MemoryCriterion":
                criterion = MemoryCriterion.from_dict(criterion_data)
            else:
                raise ValueError(f"Unknown criterion type: {criterion_type}")
            criteria.append((criterion, workers))
        
        return cls(criteria=criteria, logic=data["logic"])


class ConditionalCriterion(ScalingCriterion):
    def __init__(self, condition_criterion: ScalingCriterion, action_criterion: ScalingCriterion, workers: int):
        """
        ConditionalCriterion applies action only when condition is met.
        
        Args:
            condition_criterion: Criterion that determines when to apply
            action_criterion: Criterion that provides the action
            workers: Number of workers when condition is met
        """
        self.condition_criterion = condition_criterion
        self.action_criterion = action_criterion
        self.workers = workers

    def max_workers(self) -> int:
        if self.condition_criterion.max_workers() > 1:
            return self.workers
        return self.action_criterion.max_workers()
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "type": "ConditionalCriterion",
            "condition_criterion": self.condition_criterion.to_dict(),
            "action_criterion": self.action_criterion.to_dict(),
            "workers": self.workers
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ConditionalCriterion":
        condition_data = data["condition_criterion"]
        action_data = data["action_criterion"]
        
        condition_type = condition_data["type"]
        if condition_type == "TimeCriterion":
            condition_criterion = TimeCriterion.from_dict(condition_data)
        elif condition_type == "CpuCriterion":
            condition_criterion = CpuCriterion.from_dict(condition_data)
        elif condition_type == "MemoryCriterion":
            condition_criterion = MemoryCriterion.from_dict(condition_data)
        else:
            raise ValueError(f"Unknown criterion type: {condition_type}")
        
        action_type = action_data["type"]
        if action_type == "TimeCriterion":
            action_criterion = TimeCriterion.from_dict(action_data)
        elif action_type == "CpuCriterion":
            action_criterion = CpuCriterion.from_dict(action_data)
        elif action_type == "MemoryCriterion":
            action_criterion = MemoryCriterion.from_dict(action_data)
        else:
            raise ValueError(f"Unknown criterion type: {action_type}")
        
        return cls(
            condition_criterion=condition_criterion,
            action_criterion=action_criterion,
            workers=data["workers"]
        )
