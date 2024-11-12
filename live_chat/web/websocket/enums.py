from enum import Enum


class WebSocketActionType(str, Enum):
    """Websocket Actions."""

    JOIN_GROUP = "group_join"
    REMOVE_GROUP = "group_remove"
    SEND_MESSAGE = "message:send"
