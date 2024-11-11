import enum


class ChatType(enum.Enum):
    """select chat type."""

    DIRECT = "direct"
    GROUP = "group"


class MessageType(enum.Enum):
    """select message type."""

    TEXT = "text"
    FILE = "file"
