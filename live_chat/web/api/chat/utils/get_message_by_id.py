from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from live_chat.db.models.chat import Message  # type: ignore[attr-defined]


async def get_message_by_id(
    db_session: AsyncSession,
    *,
    message_id: UUID,
) -> Message | None:
    """Function to get a user by his id from db."""
    query = select(Message).where(Message.id == message_id)
    result = await db_session.execute(query)
    return result.scalar_one_or_none()
