import logging
from datetime import datetime
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from live_chat.db.models.chat import Chat, Message, User  # type: ignore[attr-defined]


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
