from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from live_chat.db.models.black_list import BlackList
from live_chat.db.models.blocked_users import BlockedUsers
from live_chat.db.models.user import User


async def add_user_to_black_list(
    black_list: BlackList,
    black_list_user: User,
    db_session: AsyncSession,
) -> None:
    """Helper function for adding a user to black_list."""
    query = select(BlockedUsers).filter(
        BlockedUsers.blacklist_id == black_list.id,
        BlockedUsers.user_id == black_list_user.id,
    )
    result = await db_session.execute(query)
    user_in_black_list = result.scalars().first()

    if user_in_black_list is not None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"User {black_list_user.id} already blocked",
        )
    blocked_user = BlockedUsers(blacklist_id=black_list.id, user_id=black_list_user.id)
    db_session.add(blocked_user)
    await db_session.commit()
