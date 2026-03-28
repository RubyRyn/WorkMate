import logging
import os

from fastapi import HTTPException

from src.backend.load.bm25_manager import BM25Manager, BM25_INDEX_PATH
from src.backend.load.chroma_manager import ChromaManager
from src.backend.load.hybrid_retriever import HybridRetriever
from src.backend.llm.gemini_client import GeminiClient
from src.backend.llm.voyage_reranker import VoyageReranker

logger = logging.getLogger(__name__)

_chroma_manager = None
_gemini_client = None
_voyage_reranker = None
_bm25_manager = None
_hybrid_retriever = None


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


def get_voyage_reranker() -> VoyageReranker:
    global _voyage_reranker
    if _voyage_reranker is None:
        try:
            _voyage_reranker = VoyageReranker()
        except Exception as e:
            logger.error(f"Failed to initialize VoyageReranker: {e}")
            raise HTTPException(status_code=500, detail="Reranker configuration missing.")
    return _voyage_reranker


def get_bm25_manager() -> BM25Manager:
    global _bm25_manager
    if _bm25_manager is None:
        _bm25_manager = BM25Manager()
        if os.path.exists(BM25_INDEX_PATH):
            _bm25_manager.load(BM25_INDEX_PATH)
        else:
            logger.warning(f"BM25 index not found at {BM25_INDEX_PATH}. Run NotionIngestor to build it.")
    return _bm25_manager


def get_hybrid_retriever() -> HybridRetriever:
    global _hybrid_retriever
    if _hybrid_retriever is None:
        _hybrid_retriever = HybridRetriever(get_chroma_manager(), get_bm25_manager())
    return _hybrid_retriever
