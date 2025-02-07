from datetime import datetime
from typing import Any
from uuid import UUID

from sqlalchemy import update

from live_chat.db.models.chat import Task  # type: ignore[attr-defined]
from live_chat.db.models.enums import TaskStatus
from live_chat.db.utils import async_session_maker


async def update_summarization_task(
    task_id: UUID,
    **updated_fields: dict[str, Any] | datetime | TaskStatus,
) -> None:
    """Update summarization task."""
    if not updated_fields:
        return
    async with async_session_maker() as db_session:
        query = update(Task).where(Task.id == task_id).values(**updated_fields)
        await db_session.execute(query)
        await db_session.commit()
