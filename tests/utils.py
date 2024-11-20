from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from live_chat.db.models.chat import Chat, User


async def get_first_chat_from_db(
    db_session: AsyncSession,
) -> Chat | None:
    """Helper function for getting first chat from DB."""
    query = select(Chat)
    result = await db_session.execute(query)
    return result.scalars().first()


async def get_first_user_from_db(
    db_session: AsyncSession,
) -> User | None:
    """Helper function that returns the user who submitted the request."""
    query = select(User)
    result = await db_session.execute(query)
    return result.scalars().first()
