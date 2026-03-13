import logging

from fastapi import APIRouter, Depends, HTTPException

from src.backend.dependencies.services import get_chroma_manager, get_gemini_client
from src.backend.load.chroma_manager import ChromaManager
from src.backend.llm.gemini_client import GeminiClient
from src.backend.schemas.chat import ChatRequest, ChatResponse

router = APIRouter(prefix="/api/chat", tags=["Chat"])
logger = logging.getLogger(__name__)

MAX_CONTEXT_CHARS = 4000

@router.post("/ask", response_model=ChatResponse)
async def ask_question(
    request: ChatRequest,
    chroma: ChromaManager = Depends(get_chroma_manager),
    gemini: GeminiClient = Depends(get_gemini_client),
):
    """
    RAG Pipeline Endpoint:
    1. Retrieves relevant documents from the ChromaDB vector store.
    2. Expands context by fetching sibling chunks from the same parent.
    3. Combines them into a structured chunks list.
    4. Calls Gemini LLM using the WorkMate prompt.
    """
    try:
        # Step 1: Initial Retrieval
        results = chroma.query(request.question, n_results=5)

        # Collect initial results into a dict keyed by chunk ID for deduplication
        seen_ids = set()
        chunks_with_meta = []  # list of (doc_text, metadata, chunk_id)
        source_titles = set()

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

            for doc, meta, chunk_id in zip(docs, metas, ids):
                if chunk_id not in seen_ids:
                    seen_ids.add(chunk_id)
                    chunks_with_meta.append((doc, meta, chunk_id))
                    source_titles.add(meta.get("title", "Unknown Source"))

        # Step 2: Sibling Expansion — only for very short chunks (likely incomplete)
        parent_ids_to_expand = set()
        for doc_text, meta, chunk_id in chunks_with_meta:
            if len(doc_text.strip()) < 100:  # Only expand short/incomplete chunks
                parent_id = meta.get("parent_id")
                if parent_id:
                    parent_ids_to_expand.add(parent_id)

        for parent_id in parent_ids_to_expand:
            sibling_results = chroma.get_by_parent(parent_id, limit=5)
            if sibling_results and sibling_results.get("documents"):
                sib_docs = sibling_results["documents"]
                sib_metas = sibling_results.get("metadatas", [{}] * len(sib_docs))
                sib_ids = sibling_results.get("ids", [str(i) for i in range(len(sib_docs))])

                for doc, meta, chunk_id in zip(sib_docs, sib_metas, sib_ids):
                    if chunk_id not in seen_ids:
                        seen_ids.add(chunk_id)
                        chunks_with_meta.append((doc, meta, chunk_id))
                        source_titles.add(meta.get("title", "Unknown Source"))

        # Step 3: Build formatted context list for Gemini
        chunks = []
        total_chars = 0
        for doc, meta, chunk_id in chunks_with_meta:
            clean_doc = doc.strip().replace("\r\n", "\n")

            # Respect context cap
            if total_chars + len(clean_doc) > MAX_CONTEXT_CHARS:
                remaining = MAX_CONTEXT_CHARS - total_chars
                if remaining > 100:
                    clean_doc = clean_doc[:remaining] + "... [truncated]"
                else:
                    break

            chunks.append({
                "chunk_id": chunk_id,
                "page_title": meta.get("title", "Unknown Source"),
                "section": meta.get("parent_title", ""),
                "text": clean_doc,
            })
            total_chars += len(clean_doc)
            
        sources_list = sorted(source_titles)

        # Step 4: Generation
        answer = gemini.ask_workmate(
            chunks=chunks,
            user_question=request.question,
            debug=request.debug,
        )

        return ChatResponse(
            answer=answer,
            sources=sources_list,
        )

    except Exception as e:
        logger.error(f"Error processing RAG query: {e}")
        raise HTTPException(status_code=500, detail=str(e))
