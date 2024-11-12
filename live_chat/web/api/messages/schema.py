from pydantic import BaseModel

from live_chat.db.models.enums import ChatType
from live_chat.web.websocket.mixins import ActionTypeMixin


class ChatMessage(ActionTypeMixin, BaseModel):
    """Simple message model."""

    chat_type: ChatType
    chat_id: str
    content: str
    sender_id: str


class GroupUsage(ActionTypeMixin, BaseModel):
    """Usage with groups."""

    group_id: str
    sender_id: str
