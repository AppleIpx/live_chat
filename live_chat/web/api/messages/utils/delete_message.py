import uuid

from sqlalchemy import delete
from sqlalchemy.ext.asyncio import AsyncSession

from live_chat.db.models.chat import Message  # type: ignore[attr-defined]


async def delete_message_by_id(
    db_session: AsyncSession,
    *,
    message_id: uuid.UUID,
) -> None:
    """Function to delete a message by its ID from the database."""
    delete_statement = delete(Message).where(Message.id == message_id)
    await db_session.execute(delete_statement)
    await db_session.commit()
