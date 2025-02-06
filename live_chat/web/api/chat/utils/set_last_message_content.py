from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from live_chat.db.models.chat import Chat
from live_chat.db.models.messages import Message


async def set_previous_message_content(chat: Chat, db_session: AsyncSession) -> None:
    """Set previous message content at last_message content in chat."""
    query = (
        select(Message)
        .where(
            Message.chat_id == chat.id,
            Message.is_deleted == False,  # noqa: E712
            Message.content != None,  # noqa: E711
        )
        .order_by(Message.created_at.desc())
        .limit(1)
    )
    prev_message = (await db_session.execute(query)).scalar_one_or_none()
    chat.last_message_content = prev_message.content[:100] if prev_message else None  # type: ignore[index]
    await db_session.commit()
