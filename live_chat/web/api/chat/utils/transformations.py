from typing import List

from live_chat.db.models.chat import Chat  # type: ignore[attr-defined]
from live_chat.web.api.chat import ChatSchema


def transformation_list_chats(chats: List[Chat]) -> list[ChatSchema]:
    """Transform a list of Chat objects into a list of ChatSchema objects."""
    return [
        ChatSchema(
            id=chat.id,
            chat_type=chat.chat_type,
            name_group=chat.name,
            image_group=chat.image,
            created_at=chat.created_at,
            updated_at=chat.updated_at,
            users=chat.users,
            last_message_content=chat.messages[-1].content if chat.messages else None,
        )
        for chat in chats
    ]


async def transformation_chat_group(chat: Chat) -> ChatSchema:
    """Transform a  Chat objects into a ChatGroupDirectSchema objects."""
    return ChatSchema(
        id=chat.id,
        chat_type=chat.chat_type,
        name_group=chat.name,
        image_group=chat.image,
        created_at=chat.created_at,
        updated_at=chat.updated_at,
        users=chat.users,
        last_message_content=None,
    )


async def transformation_chat_direct(chat: Chat) -> ChatSchema:
    """Transform a  Chat objects into a ChatSchema objects."""
    return ChatSchema(
        id=chat.id,
        chat_type=chat.chat_type,
        name_group=chat.name,
        image_group=chat.image,
        created_at=chat.created_at,
        updated_at=chat.updated_at,
        users=chat.users,
        last_message_content=None,
    )
