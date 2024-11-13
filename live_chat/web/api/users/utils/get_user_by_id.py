from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from live_chat.db.models.chat import User  # type: ignore[attr-defined]


async def get_user_by_id(
    db_session: AsyncSession,
    *,
    user_id: UUID,
) -> User | None:
    """Function to get a user by his id from db."""
    query = select(User).where(User.id == user_id)
    result = await db_session.execute(query)
    user: User | None = result.scalar_one_or_none()

    return user
