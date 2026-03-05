import logging

from fastapi import APIRouter, Depends, HTTPException

from src.backend.load.chroma_manager import ChromaManager
from src.backend.llm.gemini_client import GeminiClient
from src.backend.schemas.chat import ChatRequest, ChatResponse

router = APIRouter(prefix="/chat", tags=["Chat"])
logger = logging.getLogger(__name__)

# Lazily instantiated singletons
_chroma_manager = None
_gemini_client = None


def get_chroma_manager() -> ChromaManager:
    global _chroma_manager
    if _chroma_manager is None:
        try:
            _chroma_manager = ChromaManager(
                db_path="chroma_db", collection_name="notion_docs"
            )
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


@router.post("/ask", response_model=ChatResponse)
async def ask_question(
    request: ChatRequest,
    chroma: ChromaManager = Depends(get_chroma_manager),
    gemini: GeminiClient = Depends(get_gemini_client),
):
    """
    RAG Pipeline Endpoint:
    1. Retrieves relevant documents from the ChromaDB vector store.
    2. Combines them into a single context string.
    3. Calls Gemini LLM using the WorkMate prompt.
    """
    try:
        # Step 1: Retrieval
        results = chroma.query(request.question, n_results=3)

        # Step 2: Augmentation – build the context string
        context_parts = []
        if results and results.get("documents") and results["documents"][0]:
            docs = results["documents"][0]
            metas = (
                results["metadatas"][0]
                if results.get("metadatas")
                else [{}] * len(docs)
            )
            for doc, meta in zip(docs, metas):
                title = meta.get("title", "Unknown Source")
                context_parts.append(f"[{title}]: {doc}")

        context_string = "\n\n".join(context_parts)
        if not context_string:
            context_string = "No relevant context found in Notion database."

        # Step 3: Generation
        answer = gemini.ask_workmate(
            notion_context=context_string,
            user_question=request.question,
        )

        return ChatResponse(answer=answer)

    except Exception as e:
        logger.error(f"Error processing RAG query: {e}")
        raise HTTPException(status_code=500, detail=str(e))
