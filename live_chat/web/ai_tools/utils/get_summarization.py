from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from live_chat.db.models.enums import SummarizationStatus
from live_chat.db.models.summarization import Summarization
from live_chat.db.utils import async_session_maker


async def get_summarization_by_chat_and_user(
    chat_id: UUID,
    user_id: UUID,
) -> Summarization | None:
    """Function for get a summarization by chat_id and user_id."""
    async with async_session_maker() as db_session:
        query = select(Summarization).where(
            Summarization.user_id == user_id,
            Summarization.chat_id == chat_id,
        )
        result = await db_session.execute(query)
        return result.scalar_one_or_none()


async def get_summarizations_by_user(
    db_session: AsyncSession,
    status: SummarizationStatus,
    user_id: UUID,
) -> list[Summarization]:
    """Function to get a summarizations by user."""
    query = select(Summarization).where(
        Summarization.user_id == user_id,
        Summarization.status == status,
    )
    result = await db_session.execute(query)
    return list(result.scalars().all())
