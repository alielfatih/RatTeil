"""
Structured logging for RatTeil application.
"""

import logging
import sys
from typing import Optional, Dict, Any
from pathlib import Path
from datetime import datetime
import json

from ratteil.config.settings import get_settings
from ratteil.config.exceptions import RatTeilError


# Custom log levels
TRACE = 5
VERBOSE = 15

# Add custom levels
logging.addLevelName(TRACE, "TRACE")
logging.addLevelName(VERBOSE, "VERBOSE")


class StructuredFormatter(logging.Formatter):
    """
    Formatter that outputs structured log messages.
    
    Supports both JSON and text formatting.
    """
    
    def __init__(self, fmt: Optional[str] = None, datefmt: Optional[str] = None,
                 json_format: bool = False):
        """
        Initialize formatter.
        
        Args:
            fmt: Format string for text output
            datefmt: Date format string
            json_format: Whether to output JSON
        """
        super().__init__(fmt, datefmt)
        self.json_format = json_format
    
    def format(self, record: logging.LogRecord) -> str:
        """Format the log record."""
        if self.json_format:
            return self._format_json(record)
        return super().format(record)
    
    def _format_json(self, record: logging.LogRecord) -> str:
        """Format record as JSON."""
        log_data = {
            "timestamp": datetime.now().isoformat(),
            "level": record.levelname,
            "levelnum": record.levelno,
            "message": record.getMessage(),
            "logger": record.name,
        }
        
        # Add extra fields
        for key, value in record.__dict__.items():
            if key not in [
                "name", "msg", "args", "created", "filename", "funcName",
                "levelname", "levelno", "lineno", "module", "msecs",
                "pathname", "process", "processName", "relativeCreated",
                "stack_info", "exc_info", "exc_text", "thread", "threadName",
                "message", "asctime"
            ]:
                try:
                    json.dumps(value)  # Check if serializable
                    log_data[key] = value
                except (TypeError, ValueError):
                    log_data[key] = str(value)
        
        # Add exception info
        if record.exc_info:
            log_data["exception"] = {
                "type": record.exc_info[0].__name__ if record.exc_info[0] else None,
                "message": str(record.exc_info[1]) if record.exc_info[1] else None,
                "traceback": self.formatException(record.exc_info)
            }
        
        return json.dumps(log_data, default=str)


class ColorFormatter(logging.Formatter):
    """
    Formatter that adds colors to log output.
    """
    
    # ANSI color codes
    COLORS = {
        "TRACE": "\033[90m",    # Gray
        "DEBUG": "\033[94m",    # Blue
        "INFO": "\033[92m",     # Green
        "WARNING": "\033[93m",  # Yellow
        "ERROR": "\033[91m",    # Red
        "CRITICAL": "\033[95m", # Magenta
    }
    
    RESET = "\033[0m"
    
    def format(self, record: logging.LogRecord) -> str:
        """Format the log record with colors."""
        levelname = record.levelname
        color = self.COLORS.get(levelname, "")
        
        # Format the message
        message = super().format(record)
        
        # Add color to level name
        if color:
            message = message.replace(
                f"{levelname}:",
                f"{color}{levelname}:{self.RESET}"
            )
        
        return message


class RatTeilLogger:
    """
    Logger class for RatTeil application.
    
    Provides structured logging with support for:
    - Multiple handlers (console, file)
    - JSON and text formatting
    - Color output
    - Custom log levels
    """
    
    def __init__(self, name: str = "ratteil"):
        """
        Initialize the logger.
        
        Args:
            name: Logger name
        """
        self.logger = logging.getLogger(name)
        self._configure()
    
    def _configure(self) -> None:
        """Configure the logger from settings."""
        settings = get_settings()
        
        # Prevent duplicate handlers
        if self.logger.handlers:
            return
        
        # Set log level
        level = getattr(logging, settings.log_level.upper(), logging.INFO)
        self.logger.setLevel(level)
        
        # Create formatter
        if settings.debug:
            fmt = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        else:
            fmt = "%(levelname)s: %(message)s"
        
        # Create handlers
        handlers = []
        
        # Console handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(level)
        
        # Use color formatter for console
        if sys.stdout.isatty():
            console_handler.setFormatter(ColorFormatter(fmt))
        else:
            console_handler.setFormatter(logging.Formatter(fmt))
        
        handlers.append(console_handler)
        
        # File handler (if configured)
        if settings.log_file:
            try:
                log_file = Path(settings.log_file)
                log_file.parent.mkdir(parents=True, exist_ok=True)
                
                file_handler = logging.FileHandler(log_file)
                file_handler.setLevel(level)
                
                # Use JSON formatter for file
                file_handler.setFormatter(StructuredFormatter(json_format=True))
                handlers.append(file_handler)
            except Exception as e:
                self.logger.warning(f"Failed to create file handler: {e}")
        
        # Add handlers
        for handler in handlers:
            self.logger.addHandler(handler)
    
    def get_logger(self) -> logging.Logger:
        """Get the underlying logger."""
        return self.logger
    
    def trace(self, msg: str, *args, **kwargs) -> None:
        """Log a TRACE message."""
        self.logger.log(TRACE, msg, *args, **kwargs)
    
    def verbose(self, msg: str, *args, **kwargs) -> None:
        """Log a VERBOSE message."""
        self.logger.log(VERBOSE, msg, *args, **kwargs)
    
    def debug(self, msg: str, *args, **kwargs) -> None:
        """Log a DEBUG message."""
        self.logger.debug(msg, *args, **kwargs)
    
    def info(self, msg: str, *args, **kwargs) -> None:
        """Log an INFO message."""
        self.logger.info(msg, *args, **kwargs)
    
    def warning(self, msg: str, *args, **kwargs) -> None:
        """Log a WARNING message."""
        self.logger.warning(msg, *args, **kwargs)
    
    def error(self, msg: str, *args, **kwargs) -> None:
        """Log an ERROR message."""
        self.logger.error(msg, *args, **kwargs)
    
    def critical(self, msg: str, *args, **kwargs) -> None:
        """Log a CRITICAL message."""
        self.logger.critical(msg, *args, **kwargs)
    
    def exception(self, msg: str, *args, **kwargs) -> None:
        """Log an exception with ERROR level."""
        self.logger.exception(msg, *args, **kwargs)


# Module-level logger instance
_logger: Optional[RatTeilLogger] = None


def get_logger(name: Optional[str] = None) -> RatTeilLogger:
    """
    Get a logger instance.
    
    Args:
        name: Logger name (defaults to module name)
        
    Returns:
        RatTeilLogger instance
    """
    global _logger
    if _logger is None:
        _logger = RatTeilLogger(name or "ratteil")
    return _logger


def reset_logger() -> None:
    """Reset the logger instance."""
    global _logger
    _logger = None


# Convenience functions
def trace(msg: str, *args, **kwargs) -> None:
    """Log a TRACE message."""
    get_logger().trace(msg, *args, **kwargs)


def verbose(msg: str, *args, **kwargs) -> None:
    """Log a VERBOSE message."""
    get_logger().verbose(msg, *args, **kwargs)


def debug(msg: str, *args, **kwargs) -> None:
    """Log a DEBUG message."""
    get_logger().debug(msg, *args, **kwargs)


def info(msg: str, *args, **kwargs) -> None:
    """Log an INFO message."""
    get_logger().info(msg, *args, **kwargs)


def warning(msg: str, *args, **kwargs) -> None:
    """Log a WARNING message."""
    get_logger().warning(msg, *args, **kwargs)


def error(msg: str, *args, **kwargs) -> None:
    """Log an ERROR message."""
    get_logger().error(msg, *args, **kwargs)


def critical(msg: str, *args, **kwargs) -> None:
    """Log a CRITICAL message."""
    get_logger().critical(msg, *args, **kwargs)


def exception(msg: str, *args, **kwargs) -> None:
    """Log an exception."""
    get_logger().exception(msg, *args, **kwargs)
