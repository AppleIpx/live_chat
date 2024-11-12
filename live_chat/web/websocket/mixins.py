from pydantic import BaseModel

from live_chat.web.websocket.enums import WebSocketMessageActions


class ActionTypeMixin(BaseModel):
    """Adds a field to the schemas for the websocket."""

    action_type: WebSocketMessageActions
