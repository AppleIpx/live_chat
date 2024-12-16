from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from live_chat.db.models.chat import (  # type: ignore[attr-defined]
    BlackList,
    BlockedUsers,
)


async def check_user_in_black_list(
    black_list: BlackList,
    user_id_black_list: UUID,
    db_session: AsyncSession,
) -> bool:
    """Function that checks whether the user is on the black list."""
    query = select(BlockedUsers).filter(
        BlockedUsers.blacklist_id == black_list.id,
        BlockedUsers.user_id == user_id_black_list,
    )
    result = await db_session.execute(query)
    user_in_black_list = result.scalars().first()

    return user_in_black_list is not None
