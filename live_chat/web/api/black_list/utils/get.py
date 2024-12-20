from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from live_chat.db.models.chat import (  # type: ignore[attr-defined]
    BlackList,
    BlockedUsers,
    User,
)


async def get_black_list_by_owner(
    owner: User,
    db_session: AsyncSession,
) -> BlackList | None:
    """Function for getting blacklist of a current user."""
    query = select(BlackList).where(BlackList.owner_id == owner.id)
    result = await db_session.execute(query)
    return result.scalar_one_or_none()


async def get_user_in_black_list(
    black_list: BlackList,
    user_id: UUID,
    db_session: AsyncSession,
) -> User | None:
    """Function for getting user in black list."""
    query = select(BlockedUsers).filter(
        BlockedUsers.blacklist_id == black_list.id,
        BlockedUsers.user_id == user_id,
    )
    result = await db_session.execute(query)
    return result.scalar_one_or_none()
