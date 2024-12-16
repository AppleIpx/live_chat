from uuid import UUID

from pydantic import BaseModel

from live_chat.web.api.users.schemas import UserRead


class BlackListSchema(BaseModel):
    """Represents a get command for a black list."""

    id: UUID
    owner_id: UUID
    blocked_user: UserRead


class BlackListCreateSchema(BaseModel):
    """Represents a post command for a black list."""

    user_id: UUID


class BlackListDeleteSchema(BlackListCreateSchema):
    """Represents a delete command for a black list."""
