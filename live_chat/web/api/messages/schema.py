from pydantic import BaseModel

from live_chat.enums import RecipientType, WebSocketActionType


class ChatMessage(BaseModel):
    """Simple message model."""

    action_type: WebSocketActionType
    recipient_type: RecipientType
    recipient_id: str
    content: str
    sender_id: str


class GroupUsage(BaseModel):
    """Usage with groups."""

    action_type: WebSocketActionType
    group_id: str
    sender_id: str
