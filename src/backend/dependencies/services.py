import logging

from fastapi import HTTPException

from src.backend.load.chroma_manager import ChromaManager
from src.backend.llm.gemini_client import GeminiClient

logger = logging.getLogger(__name__)

_chroma_manager = None
_gemini_client = None


def get_chroma_manager() -> ChromaManager:
    global _chroma_manager
    if _chroma_manager is None:
        try:
            _chroma_manager = ChromaManager()
        except Exception as e:
            logger.error(f"Failed to initialize ChromaManager: {e}")
            raise HTTPException(
                status_code=500, detail="Vector database connection failed."
            )
    return _chroma_manager


def get_gemini_client() -> GeminiClient:
    global _gemini_client
    if _gemini_client is None:
        try:
            _gemini_client = GeminiClient()
        except Exception as e:
            logger.error(f"Failed to initialize GeminiClient: {e}")
            raise HTTPException(status_code=500, detail="LLM configuration missing.")
    return _gemini_client
