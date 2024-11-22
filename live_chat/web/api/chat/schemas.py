from datetime import datetime
from typing import List
from uuid import UUID

from pydantic import BaseModel, HttpUrl

from live_chat.db.models.enums import ChatType
from live_chat.web.api.users.schemas import UserRead


class ChatDirectSchema(BaseModel):
    """Represents a get command for a direct chat."""

    id: UUID
    chat_type: ChatType
    created_at: datetime
    updated_at: datetime
    users: list[UserRead]  # type: ignore[type-arg]

    class Config:
        from_attributes = True


class ChatGroupSchema(ChatDirectSchema):
    """Represents a get command for a group chat."""

    image_group: HttpUrl | None
    name_group: str | None


class ChatsSchema(BaseModel):
    """Scheme including group and direct chats."""

    directs: List[ChatDirectSchema]
    groups: List[ChatGroupSchema]


class CreateChatDirectSchema(BaseModel):
    """Represents a create command for a direct chat."""

    recipient_user_id: UUID


class CreateGroupChatSchema(BaseModel):
    """Represents a create command for a group chat."""

    recipient_user_ids: List[UUID]
    name_group: str
    image_group: HttpUrl | None


class GetListChatsSchema(BaseModel):
    """Represents a get command for a all user's chats."""

    chats: ChatsSchema
