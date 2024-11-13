from enum import Enum


class WebSocketMessageActions(str, Enum):
    """Websocket Actions."""

    SEND_MESSAGE = "message:send"
    READ_MESSAGE = "message:read"
    EDIT_MESSAGE = "message:edit"
    DELETE_MESSAGE = "message:delete"


class WebSocketDisconnectTypes(str, Enum):
    """Disconnect types."""

    LEAVE_CHAT = "chat:leave"
    DISCONNECT_WEBSOCKET = "websocket:disconnect"
