from datetime import datetime
from typing import List
from uuid import UUID

from pydantic import BaseModel, HttpUrl

from live_chat.db.models.enums import ChatType
from live_chat.web.api.users.schemas import UserRead


class ChatSchema(BaseModel):
    """Represents a get command for a direct/group chat."""

    id: UUID
    chat_type: ChatType
    image: HttpUrl | None
    name: str | None
    created_at: datetime
    updated_at: datetime
    users: list[UserRead]  # type: ignore[type-arg]

    class Config:
        from_attributes = True


class CreateDirectChatSchema(BaseModel):
    """Represents a create command for a direct chat."""

    recipient_user_id: UUID


class CreateGroupChatSchema(BaseModel):
    """Represents a create command for a group chat."""

    recipient_user_ids: List[UUID]
    name_group: str
    image_group: HttpUrl | None


class UpdateGroupChatSchema(BaseModel):
    """Represents a update command for a group chat."""

    name_group: str
