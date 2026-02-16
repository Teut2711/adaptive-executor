"""Policies for determining the target number of workers."""

from typing import List

from .utils import get_logger

logger = get_logger(__name__)


class MultiCriterionPolicy:
    """A policy that combines multiple scaling criteria.

    This policy takes the minimum worker count from all criteria and ensures
    it doesn't exceed the hard cap.
    """

    def __init__(self, criteria: List[object], hard_cap: int):
        """Initialize the policy with scaling criteria and a hard cap.

        Args:
            criteria: List of scaling criteria objects that implement max_workers()
            hard_cap: Maximum number of workers allowed
        """
        if not criteria:
            raise ValueError("At least one criterion is required")
        if hard_cap < 1:
            raise ValueError("Hard cap must be at least 1")

        self.criteria = criteria
        self.hard_cap = hard_cap
        logger.debug(
            "Initialized MultiCriterionPolicy with %d criteria and hard cap of %d",
            len(criteria),
            hard_cap,
        )

    def target_workers(self) -> int:
        """Calculate the target number of workers based on all criteria.

        Returns:
            int: The target number of workers, between 1 and hard_cap (inclusive)
        """
        try:
            limits = []
            for criterion in self.criteria:
                try:
                    limit = criterion.max_workers()
                    limits.append(limit)
                    logger.debug(
                        "Criterion %s suggested %d workers",
                        criterion.__class__.__name__,
                        limit,
                    )
                except Exception as e:
                    logger.error(
                        "Error getting worker limit from %s: %s",
                        criterion.__class__.__name__,
                        str(e),
                        exc_info=True,
                    )
                    # Use a safe default if a criterion fails
                    limits.append(1)

            if not limits:
                logger.warning("No valid criteria results, using 1 worker")
                return 1

            min_limit = min(limits)
            result = max(1, min(min_limit, self.hard_cap))

            logger.debug(
                "Calculated target workers: min_limit=%d, hard_cap=%d, result=%d",
                min_limit,
                self.hard_cap,
                result,
            )

            return result

        except Exception as e:
            logger.error("Error calculating target workers: %s", str(e), exc_info=True)
            return 1  # Fallback to minimum workers on error
