import logging
import os
from collections import deque
from config import SETTINGS

# Log directory from settings
LOGS_DIR = SETTINGS.get("logs_dir", "/tmp")
os.makedirs(LOGS_DIR, exist_ok=True)  # Ensure the directory exists

# Set up the log file path
LOG_FILE_PATH = os.path.join(LOGS_DIR, "PHOMODLogger.log")

# Log buffer (for capturing recent logs)
LOG_BUFFER = deque(maxlen=100)


class BufferedHandler(logging.Handler):
    """Temporary handler to store logs before UI is ready."""

    def emit(self, record):
        log_entry = self.format(record)
        LOG_BUFFER.append(log_entry)


def configure_logger(name="PHOMODLogger", log_to_console=True, log_to_file=True):
    """Configures a logger with console, file, and buffered logging."""
    logger = logging.getLogger(name)

    if len(logger.handlers) > 0:  # Return existing logger if configured
        return logger

    log_level_str = SETTINGS.get("log_level", "INFO").upper()
    log_level = getattr(logging, log_level_str, logging.INFO)

    logger.setLevel(log_level)
    logger.propagate = False

    formatter = logging.Formatter('%(asctime)s - %(levelname)-8s | %(module)s - %(message)s', datefmt='%H:%M:%S')

    # Console logging setup
    if log_to_console:
        try:
            console_handler = logging.StreamHandler()
            console_handler.setFormatter(formatter)
            logger.addHandler(console_handler)
        except Exception as e:
            print(f"⚠️ Failed to add console handler: {e}")

    # File logging setup
    if log_to_file:
        try:
            log_file = os.path.join(LOGS_DIR, f"{name}.log")
            file_handler = logging.FileHandler(log_file, mode='a', encoding='utf-8')
            file_handler.setFormatter(formatter)
            file_handler.setLevel(logging.DEBUG)
            logger.addHandler(file_handler)
        except Exception as e:
            print(f"⚠️ Failed to add file handler: {e}")

    # Add a buffer handler to capture logs before UI starts
    try:
        buffered_handler = BufferedHandler()
        buffered_handler.setFormatter(formatter)
        logger.addHandler(buffered_handler)
    except Exception as e:
        print(f"⚠️ Failed to add buffered handler: {e}")

    # Ensure logs are written immediately
    try:
        logger.debug(f"✅ Logging initialized. Logs saved to {LOG_FILE_PATH}")
    except Exception as e:
        print(f"⚠️ Logging initialization message failed: {e}")

    return logger


# Create the application logger
app_logger = configure_logger()
