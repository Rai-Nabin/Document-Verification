"""
File Path: app/utils/logging.py

Centralized Application Logging for Document Verification System.

This module provides a configurable logging utility with file rotation and console output.
It uses a TimedRotatingFileHandler for daily log rotation and a StreamHandler for console logs,
integrating with the application's settings for consistent log management.

Usage:
- Instantiate: `logger = AppLogger(logger_name=__name__).get_logger()`
- Log messages: `logger.info("Operation completed")`
"""

import logging
import os
import sys
from logging.handlers import TimedRotatingFileHandler

from app.core import settings


class AppLogger:
    """
    Configures and manages logging for the application with file and console handlers.

    Attributes:
        log_dir (str): Directory for log files.
        log_level (str): Overall logger level (e.g., "INFO", "DEBUG").
        file_level (str): Log level for file output (e.g., "DEBUG").
        console_level (str): Log level for console output (e.g., "INFO").
        log_filename (str): Name of the log file (e.g., "app.log").
        backup_count (int): Number of backup log files to retain.
        logger_name (str): Name of the logger instance.
        logger (logging.Logger): The configured logger.
    """

    def __init__(
        self,
        log_dir: str = settings.LOG_DIR,
        log_level: str = settings.LOG_LEVEL,
        file_level: str = "DEBUG",
        console_level: str = "INFO",
        log_filename: str = "app.log",
        backup_count: int = 7,
        logger_name: str = "app",
    ) -> None:
        """
        Initialize the logger with specified settings.

        Args:
            log_dir (str): Directory for log files (default: settings.LOG_DIR).
            log_level (str): Overall logger level (default: settings.LOG_LEVEL).
            file_level (str): File handler log level (default: "DEBUG").
            console_level (str): Console handler log level (default: "INFO").
            log_filename (str): Name of log file (default: "app.log").
            backup_count (int): Number of backup log files to keep (default: 7).
            logger_name (str): Name of the logger (default: "app").
        """
        self.log_dir = log_dir
        self.log_level = log_level
        self.file_level = file_level
        self.console_level = console_level
        self.log_filename = log_filename
        self.backup_count = backup_count
        self.logger_name = logger_name
        self.logger = self._setup_logging()

    def _setup_logging(self) -> logging.Logger:
        """
        Configure logging with file rotation and console output.

        Returns:
            logging.Logger: The configured logger instance.

        Raises:
            OSError: Handled internally if log directory creation fails.
        """
        # Get or create a logger with the specified name
        logger = logging.getLogger(self.logger_name)
        logger.setLevel(getattr(logging, self.log_level.upper(), logging.INFO))

        # Prevent duplicate handlers
        if logger.handlers:
            return logger

        # Ensure log directory exists
        try:
            os.makedirs(self.log_dir, exist_ok=True)
        except OSError as e:
            print(
                f"Warning: Could not create log directory '{self.log_dir}': {str(e)}",
                file=sys.stderr,
            )

        # Set up file handler with rotation
        log_file = os.path.join(self.log_dir, self.log_filename)
        file_handler = TimedRotatingFileHandler(
            log_file, when="midnight", interval=1, backupCount=self.backup_count
        )
        file_handler.setLevel(getattr(logging, self.file_level.upper(), logging.DEBUG))

        # Set up console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(
            getattr(logging, self.console_level.upper(), logging.INFO)
        )

        # Define log format
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)

        # Add handlers to logger
        logger.addHandler(file_handler)
        logger.addHandler(console_handler)

        logger.info(
            f"Logging configured with file '{self.log_filename}' and console output"
        )
        return logger

    def get_logger(self) -> logging.Logger:
        """
        Retrieve the configured logger instance.

        Returns:
            logging.Logger: The logger instance for logging messages.
        """
        return self.logger


# Example usage:
# from app.utils.logging import AppLogger
# logger = AppLogger(logger_name=__name__).get_logger()
# logger.debug("Debug message")  # File only
# logger.info("Info message")    # File and console
# logger.error("Error message")  # File and console
