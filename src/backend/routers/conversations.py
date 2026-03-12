import json
import logging
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from sse_starlette.sse import EventSourceResponse

from src.backend.database import get_db
from src.backend.dependencies.auth import get_current_user
from src.backend.dependencies.services import get_chroma_manager, get_gemini_client
from src.backend.load.chroma_manager import ChromaManager
from src.backend.llm.gemini_client import GeminiClient
from src.backend.models.conversation import Conversation, MessageRecord
from src.backend.models.user import User
from src.backend.schemas.conversation import (
    ConversationDetail,
    ConversationSummary,
    SendMessageRequest,
    SendMessageResponse,
    UpdateConversationRequest,
)

router = APIRouter(prefix="/api/conversations", tags=["conversations"])
logger = logging.getLogger(__name__)


@router.post("/", response_model=ConversationSummary)
async def create_conversation(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    conv = Conversation(user_id=current_user.id)
    db.add(conv)
    db.commit()
    db.refresh(conv)
    return conv


@router.get("/", response_model=list[ConversationSummary])
async def list_conversations(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return (
        db.query(Conversation)
        .filter(Conversation.user_id == current_user.id)
        .order_by(Conversation.updated_at.desc())
        .all()
    )


@router.get("/{conversation_id}", response_model=ConversationDetail)
async def get_conversation(
    conversation_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    conv = (
        db.query(Conversation)
        .filter(Conversation.id == conversation_id, Conversation.user_id == current_user.id)
        .first()
    )
    if not conv:
        raise HTTPException(status_code=404, detail="Conversation not found")
    return conv


@router.post("/{conversation_id}/messages", response_model=SendMessageResponse)
async def send_message(
    conversation_id: int,
    request: SendMessageRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    chroma: ChromaManager = Depends(get_chroma_manager),
    gemini: GeminiClient = Depends(get_gemini_client),
):
    conv = (
        db.query(Conversation)
        .filter(Conversation.id == conversation_id, Conversation.user_id == current_user.id)
        .first()
    )
    if not conv:
        raise HTTPException(status_code=404, detail="Conversation not found")

    # Save user message
    user_msg = MessageRecord(
        conversation_id=conv.id, role="user", content=request.question
    )
    db.add(user_msg)

    # Build conversation history from last 6 messages
    conversation_history = [
        {"role": m.role, "content": m.content}
        for m in (conv.messages or [])[-6:]
    ]

    # RAG pipeline
    try:
        results = chroma.query(request.question, n_results=3)

        chunks = []
        if results and results.get("documents") and results["documents"][0]:
            docs = results["documents"][0]
            metas = results["metadatas"][0] if results.get("metadatas") else [{}] * len(docs)
            ids = results["ids"][0] if results.get("ids") else [str(i) for i in range(len(docs))]
            for doc, meta, doc_id in zip(docs, metas, ids):
                chunks.append({
                    "chunk_id": doc_id,
                    "page_title": meta.get("title", "Unknown Source"),
                    "text": doc,
                })

        answer = gemini.ask_workmate(
            chunks=chunks,
            user_question=request.question,
            debug=request.debug,
            conversation_history=conversation_history,
        )
    except Exception as e:
        logger.error(f"RAG pipeline error: {e}")
        answer = "Sorry, I encountered an error processing your question. Please try again."

    # Save assistant message
    assistant_msg = MessageRecord(
        conversation_id=conv.id, role="assistant", content=answer
    )
    db.add(assistant_msg)

    # Auto-title on first message
    if conv.title == "New Chat":
        conv.title = request.question[:50] + ("..." if len(request.question) > 50 else "")

    conv.updated_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(user_msg)
    db.refresh(assistant_msg)

    return SendMessageResponse(user_message=user_msg, assistant_message=assistant_msg)


@router.patch("/{conversation_id}", response_model=ConversationSummary)
async def update_conversation(
    conversation_id: int,
    request: UpdateConversationRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    conv = (
        db.query(Conversation)
        .filter(Conversation.id == conversation_id, Conversation.user_id == current_user.id)
        .first()
    )
    if not conv:
        raise HTTPException(status_code=404, detail="Conversation not found")
    conv.title = request.title
    conv.updated_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(conv)
    return conv


@router.post("/{conversation_id}/messages/stream")
async def stream_message(
    conversation_id: int,
    request: SendMessageRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    chroma: ChromaManager = Depends(get_chroma_manager),
    gemini: GeminiClient = Depends(get_gemini_client),
):
    conv = (
        db.query(Conversation)
        .filter(Conversation.id == conversation_id, Conversation.user_id == current_user.id)
        .first()
    )
    if not conv:
        raise HTTPException(status_code=404, detail="Conversation not found")

    # Save user message immediately
    user_msg = MessageRecord(
        conversation_id=conv.id, role="user", content=request.question
    )
    db.add(user_msg)
    db.commit()
    db.refresh(user_msg)

    # RAG retrieval
    try:
        results = chroma.query(request.question, n_results=3)
        chunks = []
        if results and results.get("documents") and results["documents"][0]:
            docs = results["documents"][0]
            metas = results["metadatas"][0] if results.get("metadatas") else [{}] * len(docs)
            ids = results["ids"][0] if results.get("ids") else [str(i) for i in range(len(docs))]
            for doc, meta, doc_id in zip(docs, metas, ids):
                chunks.append({
                    "chunk_id": doc_id,
                    "page_title": meta.get("title", "Unknown Source"),
                    "text": doc,
                })
    except Exception as e:
        logger.error(f"RAG retrieval error: {e}")
        chunks = []

    # Load conversation history (last 6 messages before the new user message)
    conversation_history = [
        {"role": m.role, "content": m.content}
        for m in (conv.messages or [])[-7:-1]  # exclude the just-added user msg
    ]

    async def event_generator():
        full_answer = ""
        try:
            async for text_chunk in gemini.ask_workmate_stream(
                chunks=chunks,
                user_question=request.question,
                debug=request.debug,
                conversation_history=conversation_history,
            ):
                full_answer += text_chunk
                yield {"data": json.dumps({"chunk": text_chunk})}
        except Exception as e:
            logger.error(f"Streaming error: {e}")
            error_msg = "Sorry, something went wrong while generating a response."
            full_answer = error_msg
            yield {"data": json.dumps({"chunk": error_msg})}

        # Save the full assembled answer
        assistant_msg = MessageRecord(
            conversation_id=conv.id, role="assistant", content=full_answer
        )
        db.add(assistant_msg)

        # Auto-title if still "New Chat"
        if conv.title == "New Chat":
            conv.title = request.question[:50] + ("..." if len(request.question) > 50 else "")

        conv.updated_at = datetime.now(timezone.utc)
        db.commit()
        db.refresh(assistant_msg)

        # Only send sources if the LLM actually used them (not "cannot find")
        sources = []
        if "cannot find" not in full_answer.lower():
            sources = [
                {
                    "title": c.get("page_title", "Unknown Source"),
                    "excerpt": (c.get("text") or "")[:200],
                }
                for c in chunks
            ]
        yield {"data": json.dumps({"done": True, "message_id": assistant_msg.id, "sources": sources})}

    return EventSourceResponse(event_generator())


@router.delete("/{conversation_id}")
async def delete_conversation(
    conversation_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    conv = (
        db.query(Conversation)
        .filter(Conversation.id == conversation_id, Conversation.user_id == current_user.id)
        .first()
    )
    if not conv:
        raise HTTPException(status_code=404, detail="Conversation not found")
    db.delete(conv)
    db.commit()
    return {"message": "Conversation deleted"}
