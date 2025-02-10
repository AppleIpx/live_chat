from operator import attrgetter
from typing import List

from live_chat.db.models.messages import Message


async def get_correct_last_message(messages: List[Message]) -> Message | None:
    """Retrieving the last non-deleted message from the message list."""
    for message in sorted(
        messages,
        key=attrgetter("created_at"),
        reverse=True,
    ):
        if not message.is_deleted:
            return message
    return None
