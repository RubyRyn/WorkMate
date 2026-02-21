import os
from dotenv import load_dotenv

# Load .env once when this module is imported
load_dotenv()

DEFAULT_GEMINI_MODEL_ID = os.getenv("GEMINI_MODEL_ID", "gemini-3-flash-preview")


def get_required_env(key: str) -> str:
    """Fetch an env var or raise a clear error."""
    value = os.getenv(key)
    if not value:
        raise ValueError(f"{key} not found in environment (.env)")
    return value
