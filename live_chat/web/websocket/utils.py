from fastapi_users_db_sqlalchemy import UUID_ID
from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from live_chat.db.models.chat import Chat  # type: ignore[attr-defined]


async def get_chat_by_id(
    db_session: AsyncSession,
    *,
    chat_id: UUID_ID,
) -> Chat | None:
    """Getting a chat by id."""

    query = select(Chat).where(or_(Chat.id == chat_id))
    result = await db_session.execute(query)
    return result.scalar_one_or_none()
