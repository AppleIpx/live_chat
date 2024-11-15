from typing import List

from live_chat.db.models.chat import Chat, Message  # type: ignore[attr-defined]
from live_chat.web.api.chat.schemas import ChatSchema, GetMessageSchema


def transformation_message(messages: List[Message]) -> List[GetMessageSchema]:
    """Transform a list of Message objects into a list of GetMessageSchema objects."""
    return [
        GetMessageSchema(
            message_id=msg.id,
            content=msg.content,
            created_at=msg.created_at,
            chat_id=msg.chat.id,
            user_id=msg.user.id,
        )
        for msg in messages
    ]


def transformation_list_chats(chats: List[Chat]) -> List[ChatSchema]:
    """Transform a list of Chat objects into a list of ChatSchema objects."""
    return [
        ChatSchema(
            id=chat.id,
            chat_type=chat.chat_type,
            created_at=chat.created_at,
            updated_at=chat.updated_at,
            users=chat.users,
        )
        for chat in chats
    ]


def transformation_chat(chat: Chat) -> ChatSchema:
    """Transform a  Chat objects into a ChatSchema objects."""
    return ChatSchema(
        id=chat.id,
        chat_type=chat.chat_type,
        created_at=chat.created_at,
        updated_at=chat.updated_at,
        users=chat.users,
    )
