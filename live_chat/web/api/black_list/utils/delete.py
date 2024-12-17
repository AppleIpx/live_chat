from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from live_chat.db.models.chat import (  # type: ignore[attr-defined]
    BlackList,
    BlockedUsers,
    User,
)


async def delete_user_from_black_list(
    black_list_user: User,
    black_list: BlackList,
    db_session: AsyncSession,
) -> None:
    """Function to remove a user from the black list."""
    query = select(BlockedUsers).filter(
        BlockedUsers.blacklist_id == black_list.id,
        BlockedUsers.user_id == black_list_user.id,
    )
    result = await db_session.execute(query)
    if not (user_in_black_list := result.scalars().first()):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found in black list",
        )
    await db_session.delete(user_in_black_list)
    await db_session.commit()
