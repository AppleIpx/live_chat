from typing import List

from live_chat.db.models.chat import Chat  # type: ignore[attr-defined]
from live_chat.web.api.chat.schemas import (
    ChatDirectSchema,
    ChatGroupSchema,
    ChatsSchema,
)


def transformation_list_chats(chats: List[Chat]) -> ChatsSchema:
    """Transform a list of Chat objects into a list of ChatSchema objects."""
    directs = []
    groups = []
    for chat in chats:
        if chat.chat_type.value == "direct":
            directs.append(
                ChatDirectSchema(
                    id=chat.id,
                    chat_type=chat.chat_type,
                    created_at=chat.created_at,
                    updated_at=chat.updated_at,
                    users=chat.users,
                    last_message_content=(
                        chat.messages[-1].content if chat.messages else None
                    ),
                ),
            )
        else:
            groups.append(
                ChatGroupSchema(
                    id=chat.id,
                    image_group=chat.image,
                    name_group=chat.name,
                    chat_type=chat.chat_type,
                    created_at=chat.created_at,
                    updated_at=chat.updated_at,
                    users=chat.users,
                    last_message_content=(
                        chat.messages[-1].content if chat.messages else None
                    ),
                ),
            )
    return ChatsSchema(
        directs=directs,
        groups=groups,
    )


async def transformation_chat_group(chat: Chat) -> ChatGroupSchema:
    """Transform a  Chat objects into a ChatGroupDirectSchema objects."""
    return ChatGroupSchema(
        id=chat.id,
        image_group=chat.image,
        name_group=chat.name,
        chat_type=chat.chat_type,
        created_at=chat.created_at,
        updated_at=chat.updated_at,
        users=chat.users,
        last_message_content=None,
    )


async def transformation_chat_direct(chat: Chat) -> ChatDirectSchema:
    """Transform a  Chat objects into a ChatDirectSchema objects."""
    return ChatDirectSchema(
        id=chat.id,
        chat_type=chat.chat_type,
        created_at=chat.created_at,
        updated_at=chat.updated_at,
        users=chat.users,
        last_message_content=None,
    )
