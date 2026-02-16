"""Utility functions and classes for the adaptive-executor package."""

# Import logger functions to make them available at the package level
from .logger import get_logger, setup_logger

# Create a default logger instance
logger = get_logger(__name__)

__all__ = ["get_logger", "setup_logger", "logger"]
