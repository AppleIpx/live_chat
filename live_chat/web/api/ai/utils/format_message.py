from typing import Any, Final, Sequence
from uuid import UUID

from sqlalchemy import Row, RowMapping

MAX_SUMMARIZATION_SYMBOLS: Final = 10000


async def get_formatted_messages(
    messages: Sequence[Row[Any] | RowMapping | Any],
    current_user_id: UUID,
) -> dict[str, str]:
    """Function to format and limit messages."""
    formatted_messages: dict[str, list[str]] = {}
    previous_date = None
    total_length = 0
    for content, user_id, created_at in messages:
        formatted_user = "Я" if user_id == current_user_id else "Другой пользователь"
        formatted_message = f"{formatted_user}: {content}"
        if total_length + len(formatted_message) > MAX_SUMMARIZATION_SYMBOLS:
            break
        message_date = created_at.date().isoformat()  # type: ignore[union-attr]
        if previous_date != message_date:
            previous_date = message_date
        if message_date not in formatted_messages:
            formatted_messages[message_date] = []
        formatted_messages[message_date].append(formatted_message)
        total_length += len(formatted_message)
    return {date: "\n".join(messages) for date, messages in formatted_messages.items()}
