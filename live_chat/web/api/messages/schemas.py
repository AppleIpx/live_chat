from datetime import datetime
from uuid import UUID

from pydantic import BaseModel

from live_chat.web.api.chat.schemas import ChatDirectSchema
from live_chat.web.api.users.schemas import UserRead


class GetMessageSchema(BaseModel):
    """Represents a get command for a message."""

    message_id: UUID
    user_id: UUID
    chat_id: UUID
    content: str
    created_at: datetime


class GetListMessagesDirectSchema(ChatDirectSchema):
    """Represents a get command for a messages."""

    messages: list[GetMessageSchema]


class PostMessageSchema(BaseModel):
    """Represents a message for create."""

    content: str
