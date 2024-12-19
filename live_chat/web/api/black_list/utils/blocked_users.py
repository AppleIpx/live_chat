from typing import List

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from live_chat.db.models.chat import BlackList, BlockedUsers, User


async def get_blocked_users(
    black_list: BlackList,
    db_session: AsyncSession,
) -> List[User] | []:
    """Help function gets a list of blocked users."""
    blocked_users_query = (
        select(User)
        .join(BlockedUsers, BlockedUsers.user_id == User.id)
        .where(BlockedUsers.blacklist_id == black_list.id)
        .order_by(User.id)
    )
    result = await db_session.execute(blocked_users_query)
    return result.scalars().all()
