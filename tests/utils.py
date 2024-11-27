from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from live_chat.db.models.chat import Chat, User

payload = {
    "email": "user1@example.com",
    "password": "string_123",
    "is_active": True,
    "is_superuser": False,
    "is_verified": False,
    "first_name": "string",
    "last_name": "string",
    "username": "username123!",
    "user_image": None,
}

new_payload = {
    "email": "new_user@example.com",
    "password": "new_string_123",
    "is_active": True,
    "is_superuser": True,
    "is_verified": True,
    "first_name": "new_string",
    "last_name": "new_string",
    "username": "new_string",
    "user_image": None,
}


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
