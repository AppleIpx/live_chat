from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from live_chat.db.models.chat import Chat  # type: ignore[attr-defined]


async def get_chat_by_id(
    db_session: AsyncSession,
    *,
    chat_id: UUID,
) -> Chat | None:
    """Retrieving chat from database by id."""
    query = (
        select(Chat)
        .where(Chat.id == chat_id)
        .options(
            selectinload(Chat.messages),
            selectinload(Chat.users),
        )
    )
    result = await db_session.execute(query)
    chat: Chat | None = result.scalar_one_or_none()

    return chat
