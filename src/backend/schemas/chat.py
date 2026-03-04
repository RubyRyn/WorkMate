from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    question: str = Field(..., description="The user's question to ask the RAG pipeline.")


class ChatResponse(BaseModel):
    answer: str = Field(..., description="The generated context-aware answer from the Gemini LLM.")
