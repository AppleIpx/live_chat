from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from live_chat.db.models.chat import DraftMessage  # type: ignore[attr-defined]


async def get_draft_message_by_chat_and_user_ids(
    db_session: AsyncSession,
    chat_id: UUID,
    user_id: UUID,
) -> DraftMessage:
    """Helper function to get draft message by chat and user ids."""
    query = select(DraftMessage).where(
        DraftMessage.user_id == user_id,
        DraftMessage.chat_id == chat_id,
    )
    result = await db_session.execute(query)
    return result.scalar_one_or_none()
