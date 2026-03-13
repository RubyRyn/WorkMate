from datetime import datetime

from pydantic import BaseModel, Field


class MessageSchema(BaseModel):
    id: int
    role: str
    content: str
    created_at: datetime

    model_config = {"from_attributes": True}


class ConversationSummary(BaseModel):
    id: int
    title: str
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class ConversationDetail(BaseModel):
    id: int
    title: str
    messages: list[MessageSchema]
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class UpdateConversationRequest(BaseModel):
    title: str


class SendMessageRequest(BaseModel):
    question: str = Field(..., description="The user's question.")
    debug: bool = Field(False, description="Include chunk IDs in citations.")


class SendMessageResponse(BaseModel):
    user_message: MessageSchema
    assistant_message: MessageSchema
