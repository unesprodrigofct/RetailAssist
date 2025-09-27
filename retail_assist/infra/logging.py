"""Centralized logging configuration using loguru."""

import sys
from pathlib import Path
from typing import Optional

from loguru import logger

from .settings import settings


def setup_logging(
    log_level: Optional[str] = None,
    log_file: Optional[Path] = None,
    rotation: str = "10 MB",
    retention: str = "7 days",
) -> None:
    """
    Configure logging with loguru.
    
    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: Path to log file. If None, uses default from settings
        rotation: Log rotation policy
        retention: Log retention policy
    """
    # Remove default handler
    logger.remove()
    
    # Set log level
    level = log_level or settings.LOG_LEVEL
    
    # Add console handler
    logger.add(
        sys.stderr,
        format=settings.LOG_FORMAT,
        level=level,
        colorize=True,
        backtrace=True,
        diagnose=True,
    )
    
    # Add file handler if log file is specified or can be determined
    if log_file is None:
        log_file = settings.LOGS_DIR / "retail_assist.log"
    
    logger.add(
        log_file,
        format=settings.LOG_FORMAT,
        level=level,
        rotation=rotation,
        retention=retention,
        backtrace=True,
        diagnose=True,
        enqueue=True,  # Thread-safe logging
    )
    
    logger.info(f"Logging configured with level: {level}")
    logger.info(f"Log file: {log_file}")


def get_logger(name: str):
    """
    Get a logger instance with the specified name.
    
    Args:
        name: Logger name (usually __name__)
        
    Returns:
        Logger instance
    """
    return logger.bind(name=name)


# Initialize logging on module import
setup_logging()

# Export the main logger
__all__ = ["logger", "get_logger", "setup_logging"]
