"""Backwards-compatible logger exports.

This module is kept as an import shim. The implementation lives in
``adaptive_executor.utils.logger``.
"""

from .utils.logger import (  # noqa: F401
    DEFAULT_LOG_FORMAT,
    DEFAULT_LOG_LEVEL,
    get_logger,
    logger,
    setup_logger,
)

__all__ = [
    "DEFAULT_LOG_FORMAT",
    "DEFAULT_LOG_LEVEL",
    "setup_logger",
    "get_logger",
    "logger",
]
