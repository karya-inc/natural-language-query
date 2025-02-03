import logging
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Access environment variables
LOGS_FOLDER_PATH = os.getenv("LOGS_FOLDER_PATH")


def disable_logging(logger_name: str) -> None:
    """
    Disable logging for a specific logger by setting its level above CRITICAL.

    Args:
        logger_name (str): Name of the logger to disable.
    """
    logger_name = f"{LOGS_FOLDER_PATH}/{logger_name}"

    logger = logging.getLogger(logger_name)
    logger.setLevel(logging.CRITICAL)

    # Remove all handlers for this logger
    while logger.handlers:
        handler = logger.handlers[0]
        logger.removeHandler(handler)
        handler.close()

    
def setup_logging(logger_name: str, success_file: str, error_file: str) -> logging.Logger:
    """
    Set up logging configuration with separate handlers for success and error logs.

    Args:
        logger_name (str): Name of the logger.
        success_file (str): Path to the file for success logs.
        error_file (str): Path to the file for error logs.

    Returns:
        logging.Logger: Configured logger instance.
    """
    # Create the folder if it doesn't exist
    if not os.path.exists(LOGS_FOLDER_PATH):
        print(f"Folder {LOGS_FOLDER_PATH} does not exist. Creating it...")
        os.makedirs(LOGS_FOLDER_PATH)


    log_format = '%(asctime)s - %(levelname)s - %(name)s - %(message)s'
    logger = logging.getLogger(f"{LOGS_FOLDER_PATH}/{logger_name}")
    
    # Clear any existing handlers to avoid duplicate logs
    if logger.hasHandlers():
        logger.handlers.clear()

    logger.setLevel(logging.DEBUG)
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(logging.Formatter(log_format))
    console_handler.setLevel(logging.INFO)
    
    # Success file handler
    success_handler = logging.FileHandler(f"{LOGS_FOLDER_PATH}/{success_file}")
    success_handler.setFormatter(logging.Formatter(log_format))
    success_handler.setLevel(logging.INFO)
    
    # Error file handler
    error_handler = logging.FileHandler(f"{LOGS_FOLDER_PATH}/{error_file}")
    error_handler.setFormatter(logging.Formatter(log_format))
    error_handler.setLevel(logging.ERROR)
    
    # Add handlers to logger
    logger.addHandler(console_handler)
    logger.addHandler(success_handler)
    logger.addHandler(error_handler)
    
    return logger