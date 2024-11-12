from live_chat.web.api.chat.schemas import CreateMessageSchema
from live_chat.web.websocket.mixins import ActionTypeMixin


class SendMessageWebSocketSchema(ActionTypeMixin, CreateMessageSchema):
    """Represents a message for create in WebSocket."""
