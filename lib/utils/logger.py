import logging
import os
from datetime import datetime
from lib import config

# Setup logging to a file in the root directory
LOG_FILE = os.path.join(config.BASE_DIR, "app_logs.txt")

# Configure the logger
logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

def log_info(message):
    """Log informational messages."""
    logging.info(message)

def log_warning(message):
    """Log warning messages."""
    logging.warning(message)

def log_error(message, exc_info=False):
    """Log error messages. If exc_info is True, it will log the stack trace."""
    if exc_info:
        logging.error(message, exc_info=True)
    else:
        logging.error(message)

def clear_logs():
    """Clear the log file."""
    with open(LOG_FILE, 'w') as f:
        f.write(f"--- Log cleared at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} ---\n")
