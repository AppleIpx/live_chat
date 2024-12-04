import logging
from datetime import datetime
from uuid import UUID

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
    chat_id: UUID,
    current_user: User,
) -> Message | None:
    """Save the message to the database."""
    chat = await db_session.get(Chat, chat_id)

    if not chat:
        logging.error("Data error. Chat or user not found.", exc_info=True)
        return None

    message = Message(
        content=message_content,
        chat_id=chat_id,
        user_id=current_user.id,
    )
    chat.updated_at = datetime.now()

    db_session.add(message)
    await db_session.commit()
    await db_session.refresh(message)

    return message


async def save_deleted_message_to_db(
    db_session: AsyncSession,
    message: Message,
) -> DeletedMessage | None:
    """Save the message to the database."""
    chat = await db_session.get(Chat, message.chat_id)

    if not chat:
        logging.error("Data error. Chat not found.", exc_info=True)
        return None

    deleted_message = DeletedMessage(
        content=message.content,
        chat_id=message.chat_id,
        user_id=message.user_id,
        original_message_id=message.id,
        is_deleted=True,
    )

    db_session.add(deleted_message)
    await db_session.commit()
    await db_session.refresh(deleted_message)

    return deleted_message
