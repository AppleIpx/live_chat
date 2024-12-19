from datetime import datetime
from uuid import UUID

from pydantic import BaseModel

from live_chat.db.models.enums import MessageType


class GetMessageSchema(BaseModel):
    """Represents a get command for a message."""

    id: UUID
    user_id: UUID
    chat_id: UUID
    message_type: MessageType
    file_name: str | None
    file_path: str | None
    content: str | None
    created_at: datetime
    updated_at: datetime
    is_deleted: bool


class PostMessageSchema(BaseModel):
    """Represents a message for create."""

    message_type: MessageType = MessageType.TEXT
    content: str | None = None
    file_name: str | None = None
    file_path: str | None = None


class UpdateMessageSchema(PostMessageSchema):
    """Represents a message for update."""
