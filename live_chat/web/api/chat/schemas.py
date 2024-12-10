from datetime import datetime
from typing import List
from uuid import UUID

from pydantic import BaseModel, HttpUrl

from live_chat.db.models.enums import ChatType
from live_chat.web.api.users.schemas import UserRead


class ReadStatusSchema(BaseModel):
    """Represents a get command for a read status in chat."""

    id: UUID
    last_read_message_id: UUID | None
    user_id: UUID
    chat_id: UUID
    count_unread_msg: int


class UpdateReadStatusSchema(BaseModel):
    """Represents a patch command for a read status in chat."""

    last_read_message_id: UUID
    count_unread_msg: int = 0


class BaseChatSchema(BaseModel):
    """Base class to represent the chat."""

    id: UUID
    chat_type: ChatType
    image: HttpUrl | None
    name: str | None
    created_at: datetime
    updated_at: datetime
    users: list[UserRead]  # type: ignore[type-arg]


class ChatSchema(BaseChatSchema):
    """Represents a get command for a direct/group chat."""

    read_statuses: ReadStatusSchema

    class Config:
        from_attributes = True


class DeletedChatSchema(BaseChatSchema):
    """Represents a get command for a deleted chat."""


class CreateDirectChatSchema(BaseModel):
    """Represents a create command for a direct chat."""

    recipient_user_id: UUID


class CreateGroupChatSchema(BaseModel):
    """Represents a create command for a group chat."""

    recipient_user_ids: List[UUID]
    name_group: str
    image_group: HttpUrl | None
