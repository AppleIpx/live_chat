from uuid import UUID

from sqlalchemy import delete
from sqlalchemy.ext.asyncio import AsyncSession

from live_chat.db.models.enums import SummarizationStatus
from live_chat.db.models.summarization import Summarization


async def delete_active_summarizations(
    db_session: AsyncSession,
    *,
    chat_id: UUID,
    user_id: UUID,
) -> None:
    """Function to delete summarizations in progress to this chat from this user."""
    query = delete(Summarization).where(
        Summarization.user_id == user_id,
        Summarization.chat_id == chat_id,
        Summarization.status == SummarizationStatus.IN_PROGRESS,
    )
    await db_session.execute(query)
