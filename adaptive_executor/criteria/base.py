"""Base class for all scaling criteria."""
import datetime
import json
from typing import Any, Dict, Type, TypeVar

from ..utils import get_logger

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
    def _parse_datetime(dt_val:str) -> datetime.datetime:
        """Parse a datetime from string or timestamp."""
        return datetime.datetime.fromisoformat(dt_val)
    @staticmethod    
    def _format_with_tz(dt: datetime.datetime) -> str:
        """Format a datetime with timezone if available."""
        return dt.isoformat()
