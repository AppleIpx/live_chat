from typing import List, cast
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from live_chat.db.models.read_status import ReadStatus


async def get_read_status_by_id(
    db_session: AsyncSession,
    *,
    read_status_id: UUID,
) -> ReadStatus | None:
    """Function to get a read status by his id from db."""
    query = select(ReadStatus).where(ReadStatus.id == read_status_id)
    result = await db_session.execute(query)
    return result.scalar_one_or_none()


async def get_read_status_by_user_chat_ids(
    db_session: AsyncSession,
    *,
    user_id: UUID,
    chat_id: UUID,
) -> ReadStatus | None:
    """Function to get a read status by user_id and chat_id ids from db."""
    query = select(ReadStatus).where(
        ReadStatus.user_id == user_id,
        ReadStatus.chat_id == chat_id,
    )
    result = await db_session.execute(query)
    return result.scalar_one_or_none()


async def get_read_statuses_by_chat_id(
    db_session: AsyncSession,
    *,
    chat_id: UUID,
) -> List[ReadStatus]:
    """Function to get a list of read statuses of all users in this chat."""
    query = select(ReadStatus).where(ReadStatus.chat_id == chat_id)
    result = await db_session.execute(query)
    return cast(List[ReadStatus], result.scalars().all())
