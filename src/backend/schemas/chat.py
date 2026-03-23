# from typing import Optional

# from pydantic import BaseModel, Field


# class ChatRequest(BaseModel):
#     question: str = Field(
#         ..., description="The user's question to ask the RAG pipeline."
#     )
#     debug: bool = Field(
#         False, description="Enable debug mode to include chunk IDs in the response."
#     )


# class ChatResponse(BaseModel):
#     answer: str = Field(
#         ..., description="The generated context-aware answer from the Gemini LLM."
#     )
#     sources: Optional[list[str]] = Field(
#         default=None,
#         description="List of Notion page titles used as context for the answer.",
#     )
#     chunks: Optional[list[dict]] = Field(
#         default=None,
#         description="The raw context chunks sent to the LLM.",
#     )
#     unfiltered_chunks: Optional[list[dict]] = Field(
#         default=None,
#         description="The raw context chunks retrieved from ChromaDB before LLM filtering.",
#     )
