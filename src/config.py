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
VECTOR_STORE_NAME = "optibot_vector_store_v1"
TIME_SLEEP_IN_SECONDS = 5

# Set up logging 
def setup_logging():
    # Configure logging for the application
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(message)s'
    )

    # Suppress specific loggers if needed
    logging.getLogger("requests").setLevel(logging.WARNING)
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    logging.getLogger("markdownify").setLevel(logging.WARNING)
    logging.getLogger("openai").setLevel(logging.WARNING)
    logging.getLogger("openai._base_client").setLevel(logging.WARNING)
    logging.getLogger("httpx").setLevel(logging.WARNING)

    
    # Create logger for the application
    logger = logging.getLogger("OptiBot")

    return logger
