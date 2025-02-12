from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel

from live_chat.db.models.enums import MessageType
from live_chat.web.api.users.schemas import UserShortRead


class GetReactionSchema(BaseModel):
    """Represents a get message reaction."""

    id: UUID
    reaction_type: str
    user_id: UUID
    message_id: UUID
    updated_at: datetime


class PostReactionSchema(BaseModel):
    """Represents a post message reaction."""

    reaction_type: str


class GetParentMessageSchema(BaseModel):
    """Represents a get parent message."""

    id: UUID
    message_type: MessageType
    file_name: str | None
    file_path: str | None
    content: str | None


class GetBaseMessageSchema(BaseModel):
    """Represents a base get command for a message."""

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


class GetForwardMessageSchema(BaseModel):
    """Represents a get command for a forward message."""

    id: UUID
    user: UserShortRead


class GetMessageSchema(GetBaseMessageSchema):
    """Represents a get command for a message."""

    reactions: list[GetReactionSchema]
    forwarded_message: GetForwardMessageSchema | None
    parent_message: GetParentMessageSchema | None


class GetDeletedMessageSchema(GetBaseMessageSchema):
    """Represents a get command for a message."""


class PostMessageSchema(BaseModel):
    """Represents a message for create."""

    message_type: MessageType = MessageType.TEXT
    content: Optional[str] = None
    parent_message_id: Optional[UUID] = None
    file_name: Optional[str] = None
    file_path: Optional[str] = None


class UpdateMessageSchema(PostMessageSchema):
    """Represents a message for update."""


class PostDraftMessageSchema(PostMessageSchema):
    """Represents a post command for a draft message."""


class UpdateDraftMessageSchema(PostDraftMessageSchema):
    """Represents a put command for a draft message."""


class GetDraftMessageSchema(GetBaseMessageSchema):
    """Represents a get command for a draft message."""


class PostForwardMessageSchema(BaseModel):
    """Represents a post command for a forward message."""

    to_chat_id: UUID
    messages: list[UUID]


class CreatedForwardMessageSchema(BaseModel):
    """Scheme for displaying the created sent messages."""

    forward_messages: list[GetMessageSchema]
