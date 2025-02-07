import enum


class ChatType(enum.Enum):
    """Select chat type."""

    DIRECT = "direct"
    GROUP = "group"


class MessageType(enum.Enum):
    """Select message type."""

    TEXT = "text"
    FILE = "file"


class TaskType(enum.Enum):
    """Select task type."""

    SUMMARIZATION = "summarization"


class TaskStatus(enum.Enum):
    """Select task status."""

    IN_PROGRESS = "in_progress"
    SUCCESS = "success"
    ERROR = "error"
