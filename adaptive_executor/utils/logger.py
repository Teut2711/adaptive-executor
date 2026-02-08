"""Logging configuration for the adaptive-executor package."""
import logging
import logging.handlers
import os
import sys
from typing import Optional

# Default log format
DEFAULT_LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
DEFAULT_LOG_LEVEL = logging.INFO


def setup_logger(
    name: str = "adaptive_executor",
    level: int = None,
    log_file: Optional[str] = None,
    max_bytes: int = 10 * 1024 * 1024,  # 10MB
    backup_count: int = 5,
) -> logging.Logger:
    """
    Configure and return a logger with both console and optional file handlers.
    
    Args:
        name: Logger name (usually __name__)
        level: Logging level (e.g., logging.INFO, logging.DEBUG)
        log_file: Path to log file (if file logging is desired)
        max_bytes: Maximum log file size before rotation
        backup_count: Number of backup log files to keep
        
    Returns:
        Configured logger instance
    """
    logger = logging.getLogger(name)
    
    # Don't add handlers if they're already configured
    if logger.handlers:
        return logger
    
    # Set log level
    logger.setLevel(level or DEFAULT_LOG_LEVEL)
    
    # Create formatter
    formatter = logging.Formatter(DEFAULT_LOG_FORMAT)
    
    # Add console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # Add file handler if log_file is provided
    if log_file:
        # Create directory if it doesn't exist
        log_dir = os.path.dirname(log_file)
        if log_dir:
            os.makedirs(log_dir, exist_ok=True)
            
        file_handler = logging.handlers.RotatingFileHandler(
            log_file, maxBytes=max_bytes, backupCount=backup_count
        )
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    
    return logger


def get_logger(name: str = None) -> logging.Logger:
    """Get a logger instance with the given name."""
    return logging.getLogger(name or __name__)


# Create a default logger instance
logger = get_logger("adaptive_executor")

# Set default logging level for the package
logger.setLevel(DEFAULT_LOG_LEVEL)
