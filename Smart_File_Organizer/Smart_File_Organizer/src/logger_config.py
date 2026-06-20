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
    # Ensure log directory exists
    os.makedirs(log_dir, exist_ok=True)

    # Create a timestamped log filename
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_filename = os.path.join(log_dir, f"operations_{timestamp}.log")

    # Also maintain a persistent 'latest' log for easy access
    latest_log = os.path.join(log_dir, "operations.log")

    # Create logger
    logger = logging.getLogger("SmartFileOrganizer")
    logger.setLevel(logging.DEBUG)

    # Avoid duplicate handlers if logger is re-initialized
    if logger.handlers:
        logger.handlers.clear()

    # ── File Handler ──────────────────────────────────────────────────────────
    file_formatter = logging.Formatter(
        fmt="%(asctime)s | %(levelname)-8s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )

    # Timestamped file
    file_handler = logging.FileHandler(log_filename, encoding="utf-8")
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(file_formatter)

    # Latest/persistent log
    latest_handler = logging.FileHandler(latest_log, mode="w", encoding="utf-8")
    latest_handler.setLevel(logging.DEBUG)
    latest_handler.setFormatter(file_formatter)

    # ── Console Handler ───────────────────────────────────────────────────────
    console_formatter = logging.Formatter(
        fmt="  %(levelname)-8s %(message)s"
    )
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(console_formatter)

    # Attach handlers
    logger.addHandler(file_handler)
    logger.addHandler(latest_handler)
    logger.addHandler(console_handler)

    logger.info(f"Logger initialized. Log file: {log_filename}")
    return logger
