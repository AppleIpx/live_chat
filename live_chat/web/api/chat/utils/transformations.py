from live_chat.db.models.chat import Chat, ReadStatus  # type: ignore[attr-defined]
from live_chat.web.api.chat import ChatSchema
from live_chat.web.api.chat.schemas import ReadStatusSchema


async def transformation_chat(chat: Chat, read_status: ReadStatus) -> ChatSchema:
    """Transform a  Chat objects into a ChatSchema objects."""
    return ChatSchema(
        id=chat.id,
        chat_type=chat.chat_type,
        name=chat.name,
        image=chat.image,
        created_at=chat.created_at,
        updated_at=chat.updated_at,
        users=chat.users,
        read_statuses=ReadStatusSchema(
            id=read_status.id,
            chat_id=read_status.chat_id,
            user_id=read_status.user_id,
            last_read_message_id=read_status.last_read_message_id,
            count_unread_msg=0,
        ),
    )
