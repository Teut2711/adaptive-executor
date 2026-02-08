"""Multi-criterion scaling implementation."""
from typing import Any, Dict, List, Tuple

from ..base import ScalingCriterion
from ..time import TimeCriterion
from ..cpu import CpuCriterion
from ..memory import MemoryCriterion
from ...utils import get_logger

logger = get_logger(__name__)


class MultiCriterion(ScalingCriterion):
    """A criterion that combines multiple criteria with custom logic."""
    
    def __init__(self, criteria: List[Tuple[ScalingCriterion, int]], logic: str = "and"):
        """Initialize MultiCriterion.
        
        Args:
            criteria: List of criteria tuples (criterion, workers)
            logic: "and" or "or" for combining conditions
            
        Raises:
            ValueError: If logic is not 'and' or 'or', or if criteria is empty
            TypeError: If any criterion is not a ScalingCriterion instance
        """
        if logic not in ["and", "or"]:
            error_msg = f"logic must be 'and' or 'or', got {logic}"
            logger.error(error_msg)
            raise ValueError(error_msg)
        
        if not criteria:
            error_msg = "criteria cannot be empty"
            logger.error(error_msg)
            raise ValueError(error_msg)
        
        for criterion, workers in criteria:
            if not isinstance(criterion, ScalingCriterion):
                error_msg = "All criteria must be ScalingCriterion instances"
                logger.error(error_msg)
                raise TypeError(error_msg)
            if not isinstance(workers, int) or workers < 1:
                error_msg = f"workers must be a positive integer, got {workers}"
                logger.error(error_msg)
                raise ValueError(error_msg)
        
        self.criteria = criteria
        self.logic = logic
        
        logger.debug(
            "Initialized MultiCriterion: logic=%s, criteria_count=%d",
            logic, len(criteria)
        )

    def max_workers(self) -> int:
        """Get the maximum number of workers based on combined criteria.
        
        Returns:
            int: Number of workers based on the logic and criteria states
        """
        try:
            if self.logic == "and":
                # All conditions must be met
                for criterion, workers in self.criteria:
                    if criterion.max_workers() == 1:
                        logger.debug(
                            "MultiCriterion (AND): Criterion returned 1 worker, returning 1"
                        )
                        return 1
                # All conditions met, return maximum workers from all criteria
                max_workers = max(workers for criterion, workers in self.criteria)
                logger.debug(
                    "MultiCriterion (AND): All criteria met, returning %d workers",
                    max_workers
                )
                return max_workers
            elif self.logic == "or":
                # Any condition met
                for criterion, workers in self.criteria:
                    if criterion.max_workers() > 1:
                        logger.debug(
                            "MultiCriterion (OR): Criterion met, returning %d workers",
                            workers
                        )
                        return workers
                logger.debug("MultiCriterion (OR): No criteria met, returning 1 worker")
                return 1
            else:
                logger.error("MultiCriterion: Invalid logic '%s'", self.logic)
                return 1
                
        except Exception as e:
            logger.error(
                "Error in MultiCriterion.max_workers: %s",
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
                "type": "MultiCriterion",
                "criteria": [
                    {
                        "criterion": criterion.to_dict(),
                        "workers": workers
                    }
                    for criterion, workers in self.criteria
                ],
                "logic": self.logic
            }
        except Exception as e:
            logger.error(
                "Error serializing MultiCriterion to dict: %s",
                str(e), exc_info=True
            )
            raise
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'MultiCriterion':
        """Create a MultiCriterion from a dictionary.
        
        Args:
            data: Dictionary containing 'criteria' and 'logic' keys
                
        Returns:
            MultiCriterion: A new instance of MultiCriterion
            
        Raises:
            KeyError: If required keys are missing
            ValueError: If values are invalid
        """
        try:
            criteria = []
            for item in data["criteria"]:
                criterion_data = item["criterion"]
                workers = item["workers"]
                criterion_type = criterion_data["type"]
                
                if criterion_type == "TimeCriterion":
                    criterion = TimeCriterion.from_dict(criterion_data)
                elif criterion_type == "CpuCriterion":
                    criterion = CpuCriterion.from_dict(criterion_data)
                elif criterion_type == "MemoryCriterion":
                    criterion = MemoryCriterion.from_dict(criterion_data)
                elif criterion_type == "MultiCriterion":
                    criterion = cls.from_dict(criterion_data)  # Handle nested MultiCriterion
                else:
                    error_msg = f"Unknown criterion type: {criterion_type}"
                    logger.error(error_msg)
                    raise ValueError(error_msg)
                    
                criteria.append((criterion, workers))
            
            return cls(criteria=criteria, logic=data["logic"])
        except KeyError as e:
            logger.error("Missing required key in MultiCriterion data: %s", str(e))
            raise
        except Exception as e:
            logger.error("Error creating MultiCriterion from dict: %s", str(e), exc_info=True)
            raise
