from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel

from live_chat.db.models.enums import ChatType
from live_chat.web.api.users.schemas import UserRead


class ChatSchema(BaseModel):
    """Represents chat."""

    id: UUID
    chat_type: ChatType


class DisplayChatSchema(BaseModel):
    """Schema for displaying the response in swagger."""

    id: UUID
    chat_type: ChatType
    created_at: datetime
    updated_at: datetime
    users: list[UserRead]  # type: ignore[type-arg]


class CreateDirectChatSchema(BaseModel):
    """Represents a create command for a chat."""

    recipient_user_id: UUID


class GetDirectChatSchema(BaseModel):
    """Represents a get command for a direct chat."""

    chat_id: UUID
    chat_type: ChatType
    created_at: datetime
    updated_at: datetime
    users: list[UserRead]  # type: ignore[type-arg]
    new_messages_count: int

    class Config:
        from_attributes = True


class GetDirectChatsSchema(BaseModel):
    """Represents a get command for a direct chats."""

    chats: list[GetDirectChatSchema]
    total_unread_messages_count: int


class ReadMessageSchema(BaseModel):
    """Represents a message for read."""

    id: UUID
    content: str
    created_at: datetime
    updated_at: datetime
    user: UserRead  # type: ignore[type-arg]
    chat: ChatSchema
    is_read: bool | None = False
    is_new: bool | None = True


class CreateMessageSchema(BaseModel):
    """Represents a message for create."""

    content: str
    user: UserRead  # type: ignore[type-arg]
    chat: ChatSchema
    is_read: bool | None = False
    is_new: bool | None = True


class LastReadMessageSchema(BaseModel):
    """Represents a last read message."""

    id: UUID
    content: str
    created_at: datetime


class GetMessageSchema(BaseModel):
    """Represents a get command for a message."""

    message_id: UUID
    user_id: UUID
    chat_id: UUID
    content: str
    created_at: datetime
    is_read: bool | None = False


class GetMessagesSchema(BaseModel):
    """Represents a get command for a messages."""

    messages: list[GetMessageSchema]
    has_more_messages: bool
    last_read_message: Optional[LastReadMessageSchema] = None


class GetOldMessagesSchema(BaseModel):
    """Represents a get command for a old messages."""

    messages: list[GetMessageSchema]
    has_more_messages: bool
