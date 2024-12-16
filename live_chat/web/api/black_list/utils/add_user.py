from sqlalchemy.ext.asyncio import AsyncSession

from live_chat.db.models.chat import (  # type: ignore[attr-defined]
    BlackList,
    BlockedUsers,
    User,
)


async def add_user_to_black_list(
    black_list: BlackList,
    black_list_user: User,
    db_session: AsyncSession,
) -> None:
    """Helper function for adding a user to black_list."""
    blocked_user = BlockedUsers(blacklist_id=black_list.id, user_id=black_list_user.id)
    db_session.add(blocked_user)
    await db_session.commit()
