"""Scaling criteria for adaptive executor.

This module provides various criteria that determine how the executor should scale
its worker pool based on different conditions like time, CPU usage, etc.
"""
import datetime
import importlib.util
import json
from typing import Any, Dict, List, Tuple, Type, TypeVar

import pytz

from .utils import get_logger

logger = get_logger(__name__)

# Type variable for criterion classes
C = TypeVar('C', bound='ScalingCriterion')


class ScalingCriterion:
    """Base class for all scaling criteria.
    
    Subclasses must implement the max_workers() method to define their scaling logic.
    """
    
    def max_workers(self) -> int:
        """Calculate the maximum number of workers based on this criterion.
        
        Returns:
            int: The maximum number of workers (must be at least 1)
            
        Raises:
            NotImplementedError: If the subclass doesn't implement this method
        """
        raise NotImplementedError("Subclasses must implement max_workers()")
    
    def to_dict(self) -> Dict[str, Any]:
        """Serialize criterion to a dictionary.
        
        Returns:
            Dict[str, Any]: A dictionary representation of the criterion
            
        Raises:
            NotImplementedError: If the subclass doesn't implement this method
        """
        raise NotImplementedError("Subclasses must implement to_dict()")
    
    @classmethod
    def from_dict(cls: Type[C], data: Dict[str, Any]) -> C:
        """Deserialize criterion from a dictionary.
        
        Args:
            data: Dictionary containing serialized criterion data
                
        Returns:
            An instance of the criterion
            
        Raises:
            NotImplementedError: If the subclass doesn't implement this method
            ValueError: If the data is invalid
        """
        raise NotImplementedError("Subclasses must implement from_dict()")
    
    def to_json(self) -> str:
        """Serialize criterion to a JSON string.
        
        Returns:
            str: JSON string representation of the criterion
            
        Raises:
            json.JSONEncodeError: If the criterion cannot be serialized to JSON
        """
        try:
            return json.dumps(self.to_dict())
        except Exception as e:
            logger.error("Failed to serialize criterion to JSON: %s", str(e), exc_info=True)
            raise
    
    @classmethod
    def from_json(cls: Type[C], json_str: str) -> C:
        """Deserialize criterion from a JSON string.
        
        Args:
            json_str: JSON string containing serialized criterion data
                
        Returns:
            An instance of the criterion
            
        Raises:
            json.JSONDecodeError: If the JSON string is invalid
            ValueError: If the data is invalid
            NotImplementedError: If the criterion type is not supported
        """
        try:
            data = json.loads(json_str)
            return cls.from_dict(data)
        except json.JSONDecodeError as e:
            logger.error("Invalid JSON string: %s", str(e))
            raise
        except Exception as e:
            logger.error("Failed to deserialize criterion from JSON: %s", str(e), exc_info=True)
            raise
    @staticmethod    
    def _parse_datetime(dt_val):
        return datetime.datetime.fromisoformat(dt_val)
        
    def _format_with_tz(self, dt: datetime.datetime) -> str:
        return dt.astimezone(self.tz).isoformat()
        
        
class TimeCriterion(ScalingCriterion):
    """A criterion that scales workers based on timestamp.
    
    This criterion returns the configured worker count if the current timestamp falls
    within the specified time range (inclusive start, exclusive end), otherwise
    returns 1 (minimum workers).
    
    """
    
    def __init__(
        self,
        worker_count: int,
        active_start: datetime.datetime,
        active_end: datetime.datetime,
        timezone: str = "UTC",
    ):
        """Initialize the time-based criterion.
        
        Args:
            worker_count: Number of workers to use during active hours
            active_start: Start timestamp of the active period
            active_end: End timestamp of the active period
            timezone: Timezone for the active period (default: "UTC")
                
        Raises:
            ImportError: If pytz is not installed
            ValueError: If worker_count is less than 1 or time values are invalid
            TypeError: If active_start or active_end are not datetime objects
        """
        if not importlib.util.find_spec("pytz"):
            error_msg = "TimeCriterion requires 'pytz' package. Install with: pip install adaptive-executor[time]"
            logger.error(error_msg)
            raise ImportError(error_msg)
         
            
        # Store the time objects and other attributes
        self.active_start = active_start
        self.active_end = active_end
        self.worker_count = worker_count
        
        # Set up timezone
        try:
            self.tz = pytz.timezone(timezone)
        except pytz.exceptions.UnknownTimeZoneError as e:
            error_msg = f"Invalid timezone: {timezone}"
            logger.error(error_msg)
            raise ValueError(error_msg) from e
            
        # Log the configured time window
        logger.debug(
            "Initialized TimeCriterion: worker_count=%d, active_window=%s-%s %s",
            worker_count, 
            active_start.strftime('%H:%M'), 
            active_end.strftime('%H:%M'),
            timezone
        )
       
    def max_workers(self) -> int:
        """Get the maximum number of workers based on the current time.
        
        Returns:
            int: self.worker_count if current time is within active hours, else 1
        """
        try:
            now = datetime.datetime.now(self.tz)
           
            is_active = self.active_start <= now <= self.active_end
            
            if is_active:
                logger.debug(
                    "TimeCriterion: Active time %s-%s, current time %s -> %d workers",
                    self.active_start.strftime('%H:%M'), self.active_end.strftime('%H:%M'), now.strftime('%H:%M'), self.worker_count
                )
                return self.worker_count
            else:
                logger.debug(
                    "TimeCriterion: Outside active time %s-%s, current time %s -> 1 worker",
                    self.active_start.strftime('%H:%M'), self.active_end.strftime('%H:%M'), now.strftime('%H:%M')
                )
                return 1  # Minimum workers outside time range
                
        except Exception as e:
            logger.error(
                "Error in TimeCriterion.max_workers: %s",
                str(e), exc_info=True
            )
            return 1  # Fallback to minimum workers on error
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "type": "TimeCriterion",
            "worker_count": self.worker_count,
            "active_start": self._format_with_tz(self.active_start),
            "active_end": self._format_with_tz(self.active_end),
            "timezone": self.tz.zone
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "TimeCriterion":
        # Parse timestamps using the base class method
        active_start = cls._parse_datetime(data["active_start"])
        active_end = cls._parse_datetime(data["active_end"])
        
        return cls(
            worker_count=data["worker_count"],
            active_start=active_start,
            active_end=active_end,
            timezone=data["timezone"]
        )


class CpuCriterion(ScalingCriterion):
    """A criterion that scales workers based on CPU usage.
    
    This criterion returns the configured worker count if the current CPU usage
    is above the threshold, otherwise returns 1 (minimum workers).
    """
    
    def __init__(self, threshold: float, workers: int):
        """Initialize the CPU-based criterion.
        
        Args:
            threshold: CPU usage threshold (0-100) above which to scale up
            workers: Number of workers to use when CPU usage is above threshold
            
        Raises:
            ImportError: If psutil is not installed
            ValueError: If threshold is not between 0 and 100 or workers < 1
        """
        if not importlib.util.find_spec("psutil"):
            error_msg = "CpuCriterion requires 'psutil' package. Install with: pip install adaptive-executor[cpu]"
            logger.error(error_msg)
            raise ImportError(error_msg)
        
        if not (0 <= threshold <= 100):
            error_msg = f"threshold must be between 0 and 100, got {threshold}"
            logger.error(error_msg)
            raise ValueError(error_msg)
            
        if workers < 1:
            error_msg = f"workers must be at least 1, got {workers}"
            logger.error(error_msg)
            raise ValueError(error_msg)
        
        self.threshold = threshold
        self.workers = workers
        
        logger.debug(
            "Initialized CpuCriterion: threshold=%.1f%%, workers=%d",
            threshold, workers
        )

    def max_workers(self) -> int:
        """Get the maximum number of workers based on current CPU usage.
        
        Returns:
            int: self.workers if CPU usage >= threshold, else 1
        """
        try:
            import psutil
            
            # Get CPU usage with a short interval for more accurate reading
            cpu_percent = psutil.cpu_percent(interval=0.1)
            is_above_threshold = cpu_percent >= self.threshold
            
            if is_above_threshold:
                logger.debug(
                    "CpuCriterion: CPU usage %.1f%% >= %.1f%% -> %d workers",
                    cpu_percent, self.threshold, self.workers
                )
                return self.workers
            else:
                logger.debug(
                    "CpuCriterion: CPU usage %.1f%% < %.1f%% -> 1 worker",
                    cpu_percent, self.threshold
                )
                return 1
                
        except Exception as e:
            logger.error(
                "Error in CpuCriterion.max_workers: %s",
                str(e), exc_info=True
            )
            return 1  # Fallback to minimum workers on error
    
    def to_dict(self) -> Dict[str, Any]:
        """Serialize the criterion to a dictionary.
        
        Returns:
            Dict[str, Any]: Dictionary containing the criterion's state
        """
        try:
            return {
                "type": "CpuCriterion",
                "threshold": self.threshold,
                "workers": self.workers
            }
        except Exception as e:
            logger.error(
                "Error serializing CpuCriterion to dict: %s",
                str(e), exc_info=True
            )
            raise
    
    @classmethod
    def from_dict(cls: Type['CpuCriterion'], data: Dict[str, Any]) -> 'CpuCriterion':
        """Create a CpuCriterion from a dictionary.
        
        Args:
            data: Dictionary containing 'threshold' and 'workers' keys
                
        Returns:
            CpuCriterion: A new instance of CpuCriterion
                
        Raises:
            KeyError: If required keys are missing
            ValueError: If values are invalid
        """
        try:
            return cls(threshold=data["threshold"], workers=data["workers"])
        except KeyError as e:
            logger.error("Missing required key in CpuCriterion data: %s", str(e))
            raise
        except Exception as e:
            logger.error(
                "Error deserializing CpuCriterion from dict: %s",
                str(e), exc_info=True
            )
            raise


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