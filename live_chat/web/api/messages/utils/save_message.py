from datetime import datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from live_chat.db.models.chat import (  # type: ignore[attr-defined]
    Chat,
    DeletedMessage,
    Message,
    User,
)


async def save_message_to_db(
    db_session: AsyncSession,
    message_content: str,
    chat: Chat,
    current_user: User,
) -> Message | None:
    """Save the message to the database."""
    message = Message(
        content=message_content,
        chat_id=chat.id,
        user_id=current_user.id,
    )
    chat.updated_at = datetime.now()
    chat.last_message_content = message_content[:100]
    db_session.add_all([message, chat])
    await db_session.commit()
    await db_session.refresh(message)

    return message


async def save_deleted_message_to_db(
    db_session: AsyncSession,
    message: Message,
    chat: Chat,
) -> DeletedMessage | None:
    """Save the message to the database."""
    deleted_message = DeletedMessage(
        content=message.content,
        chat_id=message.chat_id,
        user_id=message.user_id,
        original_message_id=message.id,
        is_deleted=True,
    )
    query = (
        select(Message)
        .where(Message.chat_id == chat.id, Message.is_deleted == False)  # noqa: E712
        .order_by(Message.created_at.desc())
        .limit(1)
    )
    prev_message = (await db_session.execute(query)).scalar_one_or_none()
    chat.last_message_content = prev_message.content[:100] if prev_message else None
    db_session.add_all([deleted_message, chat])
    await db_session.commit()
    await db_session.refresh(deleted_message)

    return deleted_message
