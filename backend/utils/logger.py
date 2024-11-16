import os
import logging
from logging.handlers import RotatingFileHandler

# Create a directory for logs if it doesn't exist
LOG_DIR = "logs"
if not os.path.exists(LOG_DIR):
    os.makedirs(LOG_DIR)

def get_logger(name: str = "[NLQ]"):
    """Sets up the logger with rotating file and console handlers."""
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)  # Capture everything, including DEBUG

    # Avoid duplicate handlers when importing the logger multiple times
    if logger.hasHandlers():
        return logger

    # Formatter for logs
    formatter = logging.Formatter(
        "[%(asctime)s] [%(levelname)s] %(name)s - %(message)s",
        datefmt="%d-%m-%Y %H:%M:%S",
    )

    # Console Handler (Logs everything to the console)
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.DEBUG)
    console_handler.setFormatter(formatter)

    # Rotating File Handler (Logs everything to files, with rotation)
    file_handler = RotatingFileHandler(
        os.path.join(LOG_DIR, "server.log"), maxBytes=5 * 1024 * 1024, backupCount=3
    )
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)

    # Add handlers to the logger
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)

    return logger
