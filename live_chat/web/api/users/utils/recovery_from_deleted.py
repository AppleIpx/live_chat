from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from live_chat.db.models.user import User


async def recover_me(
    user: User,
    db_session: AsyncSession,
) -> None:
    """User recovery function."""
    if not user.is_deleted:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You are not deleted.",
        )
    user.is_deleted = False
    await db_session.merge(user)
    await db_session.commit()
