from typing import List

from live_chat.db.models.chat import Message  # type: ignore[attr-defined]
from live_chat.web.api.messages import GetMessageSchema


def transformation_message(messages: List[Message]) -> List[GetMessageSchema]:
    """Transform a list of Message objects into a list of GetMessageSchema objects."""
    return [
        GetMessageSchema(
            id=msg.id,
            content=msg.content,
            created_at=msg.created_at,
            updated_at=msg.updated_at,
            chat_id=msg.chat.id,
            user_id=msg.user.id,
            is_deleted=msg.is_deleted,
        )
        for msg in messages
    ]
