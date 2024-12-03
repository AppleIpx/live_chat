from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from live_chat.db.models.chat import (  # type: ignore[attr-defined]
    DeletedMessage,
    Message,
)


async def get_message_by_id(
    db_session: AsyncSession,
    *,
    message_id: UUID,
) -> Message | None:
    """Function to get a message by his id from db."""
    query = select(Message).where(Message.id == message_id)
    result = await db_session.execute(query)
    return result.scalar_one_or_none()


async def get_deleted_message_by_id(
    db_session: AsyncSession,
    *,
    deleted_message_id: UUID,
) -> DeletedMessage | None:
    """Function to get a deleted message by his id from db."""
    query = select(DeletedMessage).where(DeletedMessage.id == deleted_message_id)
    result = await db_session.execute(query)
    return result.scalar_one_or_none()
