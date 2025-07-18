from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
BASE_URL = "https://support.optisigns.com/api/v2/help_center/en-us/articles.json"
BATCH_SIZE = 10
MAX_CHUNK_SIZE_TOKENS = 600
CHUNK_OVERLAP_TOKENS = 200