"""Time-based scaling criterion."""
import datetime
import importlib.util
from typing import Any, Dict

import pytz

from .base import ScalingCriterion
from ..utils import get_logger

logger = get_logger(__name__)


class DateTimeCriterion(ScalingCriterion):
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
        """Initialize the datetime-based criterion.
        
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
            error_msg = "DateTimeCriterion requires 'pytz' package. Install with: pip install adaptive-executor[time]"
            logger.error(error_msg)
            raise ImportError(error_msg)
        
        # Validate types
        if not isinstance(active_start, datetime.datetime):
            raise TypeError("active_start must be a datetime.datetime instance")
        if not isinstance(active_end, datetime.datetime):
            raise TypeError("active_end must be a datetime.datetime instance")
        
        # Validate worker count
        if worker_count < 1:
            raise ValueError("worker_count must be at least 1")
        
        # Set up timezone first
        try:
            self.tz = pytz.timezone(timezone)
        except pytz.exceptions.UnknownTimeZoneError as e:
            error_msg = f"Invalid timezone: {timezone}"
            logger.error(error_msg)
            raise ValueError(error_msg) from e
            
        # Store the time objects and other attributes
        # Ensure the datetime objects are timezone-aware
        if active_start.tzinfo is None:
            active_start = self.tz.localize(active_start)
        else:
            active_start = active_start.astimezone(self.tz)
            
        if active_end.tzinfo is None:
            active_end = self.tz.localize(active_end)
        else:
            active_end = active_end.astimezone(self.tz)
            
        self.active_start = active_start
        self.active_end = active_end
        self.worker_count = worker_count
            
        # Log the configured time window
        logger.debug(
            "Initialized TimeCriterion: worker_count=%d, active_window=%s to %s %s",
            worker_count, 
            self._format_with_tz(self.active_start), 
            self._format_with_tz(self.active_end),
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
                    ScalingCriterion._format_with_tz(self.active_start), ScalingCriterion._format_with_tz(self.active_end), ScalingCriterion._format_with_tz(now), self.worker_count
                )
                return self.worker_count
            else:
                logger.debug(
                    "TimeCriterion: Outside active time %s-%s, current time %s -> 1 worker",
                    ScalingCriterion._format_with_tz(self.active_start), ScalingCriterion._format_with_tz(self.active_end), ScalingCriterion._format_with_tz(now)
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
            "type": "DateTimeCriterion",
            "worker_count": self.worker_count,
            "active_start": ScalingCriterion._format_with_tz(self.active_start),
            "active_end": ScalingCriterion._format_with_tz(self.active_end),
            "timezone": self.tz.zone
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "DateTimeCriterion":
        # Parse timestamps using the base class static method
        active_start = ScalingCriterion._parse_datetime(data["active_start"])
        active_end = ScalingCriterion._parse_datetime(data["active_end"])
        
        return cls(
            worker_count=data["worker_count"],
            active_start=active_start,
            active_end=active_end,
            timezone=data["timezone"]
        )