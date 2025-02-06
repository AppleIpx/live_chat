from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from live_chat.db.models.user import User


async def get_user_by_id(
    db_session: AsyncSession,
    *,
    user_id: UUID,
) -> User | None:
    """Function to get a user by his id from db."""
    query = select(User).where(User.id == user_id)  # type: ignore[arg-type]
    result = await db_session.execute(query)
    return result.scalar_one_or_none()
