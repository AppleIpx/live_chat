import enum


class ChatType(enum.Enum):
    """Select chat type."""

    DIRECT = "direct"
    GROUP = "group"


class MessageType(enum.Enum):
    """Select message type."""

    TEXT = "text"
    FILE = "file"


class SummarizationStatus(enum.Enum):
    """Select summarization status."""

    IN_PROGRESS = "in_progress"
    SUCCESS = "success"
    ERROR = "error"
