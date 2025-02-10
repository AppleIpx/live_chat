from datetime import datetime
from typing import Any
from uuid import UUID

from sqlalchemy import update

from live_chat.db.models.enums import SummarizationStatus
from live_chat.db.models.summarization import Summarization
from live_chat.db.utils import async_session_maker


async def update_summarization(
    summarization_id: UUID,
    **updated_fields: dict[str, Any] | datetime | SummarizationStatus | float,
) -> None:
    """Update summarization."""
    if not updated_fields:
        return
    async with async_session_maker() as db_session:
        query = (
            update(Summarization)
            .where(Summarization.id == summarization_id)
            .values(**updated_fields)
        )
        await db_session.execute(query)
        await db_session.commit()
