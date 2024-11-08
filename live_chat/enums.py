from enum import Enum


class RecipientType(str, Enum):
    """Выбор для типа сообщения."""

    GROUP = "group"
    USER = "user"


class WebSocketActionType(str, Enum):
    """Выбор действия в вебсокете."""

    JOIN_GROUP = "group:join"
    REMOVE_GROUP = "group:remove"
    SEND_MESSAGE = "message:send"
