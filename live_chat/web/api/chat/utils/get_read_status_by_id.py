from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from live_chat.db.models.chat import ReadStatus  # type: ignore[attr-defined]


async def get_read_status_by_id(
    db_session: AsyncSession,
    *,
    read_status_id: UUID,
) -> ReadStatus | None:
    """Function to get a user by his id from db."""
    query = select(ReadStatus).where(ReadStatus.id == read_status_id)
    result = await db_session.execute(query)
    return result.scalar_one_or_none()
