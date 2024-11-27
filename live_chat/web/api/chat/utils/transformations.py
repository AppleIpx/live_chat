from live_chat.db.models.chat import Chat  # type: ignore[attr-defined]
from live_chat.web.api.chat import ChatSchema


async def transformation_chat(chat: Chat) -> ChatSchema:
    """Transform a  Chat objects into a ChatSchema objects."""
    return ChatSchema(
        id=chat.id,
        chat_type=chat.chat_type,
        name=chat.name,
        image=chat.image,
        created_at=chat.created_at,
        updated_at=chat.updated_at,
        users=chat.users,
    )
