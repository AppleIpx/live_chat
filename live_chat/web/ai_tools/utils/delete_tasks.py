from uuid import UUID

from sqlalchemy import delete
from sqlalchemy.ext.asyncio import AsyncSession

from live_chat.db.models.chat import Task  # type: ignore[attr-defined]
from live_chat.db.models.enums import TaskStatus


async def delete_active_tasks_by_chat_and_user(
    db_session: AsyncSession,
    *,
    chat_id: UUID,
    user_id: UUID,
) -> None:
    """Function to delete tasks in progress to this chat from this user."""
    query = delete(Task).where(
        Task.user_id == user_id,
        Task.chat_id == chat_id,
        Task.status == TaskStatus.IN_PROGRESS,
    )
    await db_session.execute(query)
