import logging

# Set up logging configuration
def setup_logging(success_file, error_file):
    # Set up logging configuration
    log_format = '%(asctime)s - %(levelname)s - %(message)s'

    # Create two handlers: one for console output and one for file output
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(logging.Formatter(log_format))
    console_handler.setLevel(logging.INFO)

    # Create file handlers for success and error logs
    success_handler = logging.FileHandler(success_file) # "success_test.log"
    success_handler.setFormatter(logging.Formatter(log_format))
    success_handler.setLevel(logging.INFO)

    error_handler = logging.FileHandler(error_file) # "error_test.log"
    error_handler.setFormatter(logging.Formatter(log_format))
    error_handler.setLevel(logging.ERROR)

    # Create a logger and add the handlers
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)
    logger.addHandler(console_handler)
    logger.addHandler(success_handler)
    logger.addHandler(error_handler)

    return logger

# Function to disable logging
def disable_logging():
    logging.disable(logging.CRITICAL)