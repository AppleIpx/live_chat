from enum import Enum


class MessageType(str, Enum):
    """Выбор для типа сообщения."""

    group = "group"
    user = "user"
