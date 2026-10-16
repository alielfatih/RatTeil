"""Logging configuration for RatTeil application."""

import logging
import sys
from pathlib import Path
from typing import Optional

from ratteil.config import get_settings


# Create custom formatter
class CustomFormatter(logging.Formatter):
    """Custom log formatter with colors."""
    
    GRAY = '\033[90m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BLUE = '\033[94m'
    MAGENTA = '\033[95m'
    CYAN = '\033[96m'
    WHITE = '\033[97m'
    RESET = '\033[0m'
    
    FORMATS = {
        logging.DEBUG: f'{GRAY}%(asctime)s{GRAY} | {BLUE}%(name)s{RESET} | {CYAN}%(levelname)s{RESET} | %(message)s',
        logging.INFO: f'{GREEN}%(asctime)s{GREEN} | {BLUE}%(name)s{RESET} | {GREEN}%(levelname)s{RESET} | %(message)s',
        logging.WARNING: f'{YELLOW}%(asctime)s{YELLOW} | {BLUE}%(name)s{RESET} | {YELLOW}%(levelname)s{RESET} | %(message)s',
        logging.ERROR: f'{RED}%(asctime)s{RED} | {BLUE}%(name)s{RESET} | {RED}%(levelname)s{RESET} | %(message)s',
        logging.CRITICAL: f'{RED}%(asctime)s{RED} | {BLUE}%(name)s{RESET} | {RED}%(levelname)s{RESET} | %(message)s',
    }
    
    def format(self, record):
        log_fmt = self.FORMATS.get(record.levelno, self.FORMATS[logging.INFO])
        formatter = logging.Formatter(log_fmt, datefmt='%Y-%m-%d %H:%M:%S')
        return formatter.format(record)


def setup_logging(
    log_level: Optional[str] = None,
    log_file: Optional[str] = None,
) -> logging.Logger:
    """Set up logging configuration.
    
    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: Optional path to log file
        
    Returns:
        Configured logger
    """
    settings = get_settings()
    
    # Determine log level
    if log_level is None:
        log_level = 'DEBUG' if settings.DEBUG else 'INFO'
    
    numeric_level = getattr(logging, log_level.upper(), logging.INFO)
    
    # Create logger
    logger = logging.getLogger('ratteil')
    logger.setLevel(numeric_level)
    
    # Prevent duplicate handlers
    if logger.handlers:
        return logger
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(numeric_level)
    
    if sys.stdout.isatty():
        # Use colored formatter for terminal
        console_handler.setFormatter(CustomFormatter())
    else:
        # Use simple formatter for non-terminal
        console_handler.setFormatter(
            logging.Formatter(
                '%(asctime)s | %(name)s | %(levelname)s | %(message)s',
                datefmt='%Y-%m-%d %H:%M:%S',
            )
        )
    
    logger.addHandler(console_handler)
    
    # File handler
    if log_file or settings.DEBUG:
        log_dir = settings.LOG_DIR
        log_dir.mkdir(parents=True, exist_ok=True)
        
        log_file_path = log_file or (log_dir / 'ratteil.log')
        file_handler = logging.FileHandler(log_file_path, encoding='utf-8')
        file_handler.setLevel(logging.DEBUG)  # Always log debug to file
        file_handler.setFormatter(
            logging.Formatter(
                '%(asctime)s | %(name)s | %(levelname)s | %(message)s',
                datefmt='%Y-%m-%d %H:%M:%S',
            )
        )
        logger.addHandler(file_handler)
    
    return logger


def get_logger(name: Optional[str] = None) -> logging.Logger:
    """Get a logger with the RatTeil configuration.
    
    Args:
        name: Optional logger name (defaults to 'ratteil')
        
    Returns:
        Configured logger
    """
    if name is None:
        return logging.getLogger('ratteil')
    return logging.getLogger(f'ratteil.{name}')


# Initialize logging on import
logger = setup_logging()
