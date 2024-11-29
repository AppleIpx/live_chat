from datetime import datetime
from uuid import UUID

from pydantic import BaseModel

from live_chat.web.api.chat.schemas import ChatSchema


class GetMessageSchema(BaseModel):
    """Represents a get command for a message."""

    id: UUID
    user_id: UUID
    chat_id: UUID
    content: str
    created_at: datetime
    updated_at: datetime


class GetListMessagesSchema(ChatSchema):
    """Represents a get command for a messages."""

    messages: list[GetMessageSchema]


class PostMessageSchema(BaseModel):
    """Represents a message for create."""

    content: str


class UpdateMessageSchema(PostMessageSchema):
    """Represents a message for update."""
