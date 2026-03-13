import logging

from fastapi import APIRouter, Depends, HTTPException

from src.backend.dependencies.services import get_chroma_manager, get_gemini_client
from src.backend.load.chroma_manager import ChromaManager
from src.backend.llm.gemini_client import GeminiClient
from src.backend.schemas.chat import ChatRequest, ChatResponse

router = APIRouter(prefix="/api/chat", tags=["Chat"])
logger = logging.getLogger(__name__)


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

        # Step 2: Augmentation – extract chunks
        chunks = []
        if results and results.get("documents") and results["documents"][0]:
            docs = results["documents"][0]
            metas = (
                results["metadatas"][0]
                if results.get("metadatas")
                else [{}] * len(docs)
            )
            ids = (
                results["ids"][0]
                if results.get("ids")
                else [str(i) for i in range(len(docs))]
            )
            for doc, meta, doc_id in zip(docs, metas, ids):
                chunks.append({
                    "chunk_id": doc_id,
                    "page_title": meta.get("title", "Unknown Source"),
                    "text": doc,
                })

        # Step 3: Generation
        answer = gemini.ask_workmate(
            chunks=chunks,
            user_question=request.question,
            debug=request.debug,
        )

        return ChatResponse(answer=answer)

    except Exception as e:
        logger.error(f"Error processing RAG query: {e}")
        raise HTTPException(status_code=500, detail=str(e))
