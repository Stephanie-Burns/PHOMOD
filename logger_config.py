
import logging
import os
from collections import deque

LOGS_DIR = "logs"
os.makedirs(LOGS_DIR, exist_ok=True)
LOG_BUFFER = deque(maxlen=100)


class BufferedHandler(logging.Handler):
    """Temporary handler to store logs before UI is ready."""

    def emit(self, record):
        log_entry = self.format(record)
        LOG_BUFFER.append(log_entry)


def configure_logger(name, log_to_console=True, log_to_file=True, level=logging.INFO):
    logger = logging.getLogger(name)
    logger.setLevel(level)
    logger.propagate = False

    if logger.hasHandlers():
        logger.handlers.clear()

    formatter = logging.Formatter('%(asctime)s - %(levelname)-8s | %(module)s - %(message)s', datefmt='%H:%M:%S')

    # Console logging setup
    if log_to_console:
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

    # File logging setup
    if log_to_file:
        log_file = os.path.join(LOGS_DIR, f"{name}.log")
        file_handler = logging.FileHandler(log_file, mode='a', encoding='utf-8')
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    # Add a buffer handler to capture logs before UI starts
    buffered_handler = BufferedHandler()
    buffered_handler.setFormatter(formatter)
    logger.addHandler(buffered_handler)

    return logger


app_logger = configure_logger('FOMODLogger')
