from fastapi_users_db_sqlalchemy import UUID_ID
from pydantic import BaseModel, ConfigDict, Field
from starlette.websockets import WebSocket


class UserConnection(BaseModel):
    """Schema for storing the user's connection."""

    websocket: WebSocket
    is_online: bool = True
    model_config = ConfigDict(arbitrary_types_allowed=True)


class ChatConnections(BaseModel):
    """Schema for storing the chat's connection."""

    chat_id: UUID_ID
    users: dict[str, UserConnection] = Field(default_factory=dict)
