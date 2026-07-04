"""
logger_config.py
----------------
Centralized logging configuration for Smart File Organizer & Cleaner.
Sets up both file-based and console-based logging handlers.

Author: Smart File Organizer Project
"""

import logging
import os
from datetime import datetime


def setup_logger(log_dir: str = "logs") -> logging.Logger:
    """
    Configure and return a logger with both file and console handlers.

    Args:
        log_dir (str): Directory where the log file will be stored.

    Returns:
        logging.Logger: Configured logger instance.
    """
    os.makedirs(log_dir, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_filename = os.path.join(log_dir, f"operations_{timestamp}.log")

    latest_log = os.path.join(log_dir, "operations.log")

    logger = logging.getLogger("SmartFileOrganizer")
    logger.setLevel(logging.DEBUG)

    if logger.handlers:
        logger.handlers.clear()

    file_formatter = logging.Formatter(
        fmt="%(asctime)s | %(levelname)-8s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )

    file_handler = logging.FileHandler(log_filename, encoding="utf-8")
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(file_formatter)

    latest_handler = logging.FileHandler(latest_log, mode="w", encoding="utf-8")
    latest_handler.setLevel(logging.DEBUG)
    latest_handler.setFormatter(file_formatter)

    console_formatter = logging.Formatter(
        fmt="  %(levelname)-8s %(message)s"
    )
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(console_formatter)

    logger.addHandler(file_handler)
    logger.addHandler(latest_handler)
    logger.addHandler(console_handler)

    logger.info(f"Logger initialized. Log file: {log_filename}")
    return logger