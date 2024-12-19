"""Messages API."""

from live_chat.web.api.messages.schemas import GetMessageSchema, PostMessageSchema
from live_chat.web.api.messages.views import message_router

__all__ = (
    "PostMessageSchema",
    "GetMessageSchema",
    "message_router",
)
