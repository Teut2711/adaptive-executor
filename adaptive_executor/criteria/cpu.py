"""CPU-based scaling criterion."""
import importlib.util
from typing import Any, Dict, Type

from .base import ScalingCriterion
from ..utils import get_logger

logger = get_logger(__name__)


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
            logger.error("Error creating CpuCriterion from dict: %s", str(e), exc_info=True)
            raise