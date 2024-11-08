from pydantic import BaseModel

from live_chat.enums import MessageType


class ChatMessage(BaseModel):
    """Simple message model."""

    type: MessageType
    message: str
    recipient_id: str
    sender_id: str
