from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from live_chat.db.models.chat import Task  # type: ignore[attr-defined]
from live_chat.db.models.enums import TaskStatus
from live_chat.db.utils import async_session_maker


async def get_task_by_chat_and_user(
    chat_id: UUID,
    user_id: UUID,
    status: TaskStatus | None = None,
) -> Task | None:
    """Function for get a task by chat_id and user_id."""
    async with async_session_maker() as db_session:
        query = select(Task).where(Task.user_id == user_id, Task.chat_id == chat_id)
        if status:
            query = query.where(Task.status == status)
        result = await db_session.execute(query)
        return result.scalar_one_or_none() if status else result.scalars().first()


async def get_tasks_by_user(
    db_session: AsyncSession,
    user_id: UUID,
) -> list[Task]:
    """Function to get a task by chat_id and user_id."""
    query = select(Task).where(Task.user_id == user_id)
    result = await db_session.execute(query)
    return list(result.scalars().all())
