import logging
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
BASE_URL = "https://support.optisigns.com/api/v2/help_center/en-us/articles.json"
BATCH_SIZE = 10
MAX_CHUNK_SIZE_TOKENS = 600
CHUNK_OVERLAP_TOKENS = 200
VECTOR_STORE_NAME = "optibot_vector_store_v2"
TIME_SLEEP_IN_SECONDS = 5

# Module-level variable to store the logger instance
_logger = None

def setup_logging():
    global _logger
    if _logger is None:
        # Create logger for the application
        _logger = logging.getLogger("OptiBot")
        _logger.setLevel(logging.DEBUG)

        # Create a handler
        handler = logging.StreamHandler()
        handler.setLevel(logging.DEBUG)

        # Create a formatter
        formatter = logging.Formatter('%(message)s')
        handler.setFormatter(formatter)

        # Add the handler to the logger
        _logger.addHandler(handler)
        _logger.propagate = False  # Prevent propagation to root logger

    return _logger
