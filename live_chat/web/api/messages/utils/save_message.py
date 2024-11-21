import logging
from datetime import datetime

from sqlalchemy.ext.asyncio import AsyncSession

from live_chat.db.models.chat import Chat, Message, User  # type: ignore[attr-defined]
from live_chat.web.api.messages import CreateMessageSchema


async def save_message_to_db(
    db_session: AsyncSession,
    message: CreateMessageSchema,
) -> Message | None:
    """Save the message to the database."""
    chat = await db_session.get(Chat, message.chat.id)
    user = await db_session.get(User, message.user.id)

    if not chat or not user:
        logging.error("Data error. Chat or user not found.", exc_info=True)
        return None

    message = Message(
        content=message.content,
        chat_id=chat.id,
        user_id=user.id,
    )
    chat.updated_at = datetime.now()

    db_session.add(message)
    await db_session.commit()
    await db_session.refresh(message)

    return message
