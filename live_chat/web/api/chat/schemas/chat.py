from datetime import datetime
from uuid import UUID

from pydantic import BaseModel

from live_chat.db.models.enums import ChatType
from live_chat.web.api.users.schemas import UserRead


class ChatSchema(BaseModel):
    """Represents a get command for a chat."""

    id: UUID
    chat_type: ChatType
    created_at: datetime
    updated_at: datetime
    users: list[UserRead]  # type: ignore[type-arg]

    class Config:
        from_attributes = True


class CreateDirectChatSchema(BaseModel):
    """Represents a create command for a direct chat."""

    recipient_user_id: UUID


class GetListChatsSchema(BaseModel):
    """Represents a get command for a all user's chats."""

    chats: list[ChatSchema]
