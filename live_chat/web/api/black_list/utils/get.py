from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from live_chat.db.models.chat import BlackList, User  # type: ignore[attr-defined]


async def get_black_list_by_owner(
    owner: User,
    db_session: AsyncSession,
) -> BlackList | None:
    """Function for getting blacklist of a current user."""
    query = select(BlackList).where(BlackList.owner_id == owner.id)
    result = await db_session.execute(query)
    black_list: BlackList | None = result.scalar_one_or_none()

    return black_list
