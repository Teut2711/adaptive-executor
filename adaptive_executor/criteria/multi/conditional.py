"""Conditional criterion scaling implementation."""
from typing import Any, Dict

from ..base import ScalingCriterion
from ...utils import get_logger

logger = get_logger(__name__)


class ConditionalCriterion(ScalingCriterion):
    """A criterion that applies a condition to another criterion."""
    
    def __init__(self, condition_criterion: ScalingCriterion, action_criterion: ScalingCriterion, workers: int):
        """Initialize ConditionalCriterion.
        
        Args:
            condition_criterion: Criterion that determines when to apply
            action_criterion: Criterion that provides the action
            workers: Number of workers when condition is met
            
        Raises:
            TypeError: If criteria are not ScalingCriterion instances
            ValueError: If workers is not a positive integer
        """
        if not isinstance(condition_criterion, ScalingCriterion):
            error_msg = "condition_criterion must be a ScalingCriterion instance"
            logger.error(error_msg)
            raise TypeError(error_msg)
            
        if not isinstance(action_criterion, ScalingCriterion):
            error_msg = "action_criterion must be a ScalingCriterion instance"
            logger.error(error_msg)
            raise TypeError(error_msg)
            
        if not isinstance(workers, int) or workers < 1:
            error_msg = f"workers must be a positive integer, got {workers}"
            logger.error(error_msg)
            raise ValueError(error_msg)
        
        self.condition_criterion = condition_criterion
        self.action_criterion = action_criterion
        self.workers = workers
        
        logger.debug(
            "Initialized ConditionalCriterion: condition_type=%s, action_type=%s, workers=%d",
            type(condition_criterion).__name__,
            type(action_criterion).__name__,
            workers
        )

    def max_workers(self) -> int:
        """Get the maximum number of workers based on condition.
        
        Returns:
            int: self.workers if condition is met, else action_criterion.max_workers()
        """
        try:
            if self.condition_criterion.max_workers() > 1:
                logger.debug(
                    "ConditionalCriterion: Condition met, returning %d workers",
                    self.workers
                )
                return self.workers
            else:
                action_workers = self.action_criterion.max_workers()
                logger.debug(
                    "ConditionalCriterion: Condition not met, using action criterion with %d workers",
                    action_workers
                )
                return action_workers
                
        except Exception as e:
            logger.error(
                "Error in ConditionalCriterion.max_workers: %s",
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
                "type": "ConditionalCriterion",
                "condition_criterion": self.condition_criterion.to_dict(),
                "action_criterion": self.action_criterion.to_dict(),
                "workers": self.workers
            }
        except Exception as e:
            logger.error(
                "Error serializing ConditionalCriterion to dict: %s",
                str(e), exc_info=True
            )
            raise
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ConditionalCriterion':
        """Create a ConditionalCriterion from a dictionary.
        
        Args:
            data: Dictionary containing 'condition_criterion', 'action_criterion', and 'workers' keys
                
        Returns:
            ConditionalCriterion: A new instance of ConditionalCriterion
            
        Raises:
            KeyError: If required keys are missing
            ValueError: If values are invalid
        """
        try:
            # Import the main from_dict function to handle all criterion types
            from .. import from_dict
            
            condition_data = data["condition_criterion"]
            action_data = data["action_criterion"]
            
            condition_criterion = from_dict(condition_data)
            action_criterion = from_dict(action_data)
            
            return cls(
                condition_criterion=condition_criterion,
                action_criterion=action_criterion,
                workers=data["workers"]
            )
        except KeyError as e:
            logger.error("Missing required key in ConditionalCriterion data: %s", str(e))
            raise
        except Exception as e:
            logger.error("Error creating ConditionalCriterion from dict: %s", str(e), exc_info=True)
            raise
