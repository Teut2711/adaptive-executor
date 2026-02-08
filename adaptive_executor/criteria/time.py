"""Time-based scaling criterion."""
import datetime
import importlib.util
from typing import Any, Dict

import pytz

from .base import ScalingCriterion
from ..utils import get_logger

logger = get_logger(__name__)


class TimeCriterion(ScalingCriterion):
    """A criterion that scales workers based on time of day.
    
    This criterion returns the configured worker count if the current time of day
    falls within the specified time range (inclusive start, exclusive end), otherwise
    returns 1 (minimum workers).
    """
    
    def __init__(
        self,
        worker_count: int,
        active_start: datetime.time,
        active_end: datetime.time,
        timezone: str = "UTC",
    ):
        """Initialize the time-based criterion.
        
        Args:
            worker_count: Number of workers to use during active hours
            active_start: Start time of the active period (time of day)
            active_end: End time of the active period (time of day)
            timezone: Timezone for the active period (default: "UTC")
                
        Raises:
            ImportError: If pytz is not installed
            ValueError: If worker_count is less than 1 or time values are invalid
            TypeError: If active_start or active_end are not time objects
        """
        
        if not importlib.util.find_spec("pytz"):
            error_msg = "TimeCriterion requires 'pytz' package. Install with: pip install adaptive-executor[time]"
            logger.error(error_msg)
            raise ImportError(error_msg)
        
        # Validate types
        if not isinstance(active_start, datetime.time):
            raise TypeError("active_start must be a datetime.time instance")
        if not isinstance(active_end, datetime.time):
            raise TypeError("active_end must be a datetime.time instance")
        
        # Validate worker count
        if worker_count < 1:
            raise ValueError("worker_count must be at least 1")
        
        # Set up timezone
        try:
            self.tz = pytz.timezone(timezone)
        except pytz.exceptions.UnknownTimeZoneError as e:
            error_msg = f"Invalid timezone: {timezone}"
            logger.error(error_msg)
            raise ValueError(error_msg) from e
            
        # Store the time objects and other attributes
        self.active_start = active_start
        self.active_end = active_end
        self.worker_count = worker_count
            
        # Log the configured time window
        logger.debug(
            "Initialized TimeCriterion: worker_count=%d, active_window=%s to %s %s",
            worker_count, 
            active_start.strftime('%H:%M:%S'), 
            active_end.strftime('%H:%M:%S'),
            timezone
        )
       
    def max_workers(self) -> int:
        """Get the maximum number of workers based on the current time.
        
        Returns:
            int: self.worker_count if current time is within active hours, else 1
        """
        try:
            now = datetime.datetime.now(self.tz)
            current_time = now.time()
           
            # Handle time ranges that cross midnight
            if self.active_start <= self.active_end:
                # Normal range: start <= end (e.g., 9:00 to 17:00)
                is_active = self.active_start <= current_time <= self.active_end
            else:
                # Cross-midnight range: start > end (e.g., 22:00 to 06:00)
                is_active = current_time >= self.active_start or current_time < self.active_end
            
            if is_active:
                logger.debug(
                    "TimeCriterion: Active time %s-%s, current time %s -> %d workers",
                    self.active_start.strftime('%H:%M'), 
                    self.active_end.strftime('%H:%M'), 
                    current_time.strftime('%H:%M'), 
                    self.worker_count
                )
                return self.worker_count
            else:
                logger.debug(
                    "TimeCriterion: Outside active time %s-%s, current time %s -> 1 worker",
                    self.active_start.strftime('%H:%M'), 
                    self.active_end.strftime('%H:%M'), 
                    current_time.strftime('%H:%M')
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
            "active_start": self.active_start.isoformat(),
            "active_end": self.active_end.isoformat(),
            "timezone": self.tz.zone
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "TimeCriterion":
        # Parse time objects from ISO format
        active_start = datetime.time.fromisoformat(data["active_start"])
        active_end = datetime.time.fromisoformat(data["active_end"])
        
        return cls(
            worker_count=data["worker_count"],
            active_start=active_start,
            active_end=active_end,
            timezone=data["timezone"]
        )
