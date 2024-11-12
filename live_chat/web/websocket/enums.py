from enum import Enum


class WebSocketMessageActions(str, Enum):
    """Websocket Actions."""

    SEND_MESSAGE = "message:send"
    READ_MESSAGE = "message:read"
    EDIT_MESSAGE = "message:edit"
    DELETE_MESSAGE = "message:delete"


class DisconnectType(str, Enum):
    """Disconnect types."""

    LEAVE_CHAT = "leave_chat"
    DISCONNECT_WEBSOCKET = "disconnect_websocket"
