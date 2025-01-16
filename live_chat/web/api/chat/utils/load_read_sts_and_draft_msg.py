from uuid import UUID

from fastapi_pagination.cursor import CursorPage
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from live_chat.db.models.chat import (  # type: ignore[attr-defined]
    DraftMessage,
    ReadStatus,
    User,
)
from live_chat.web.api.chat import ChatSchema


async def get_read_statuses(
    current_user: User,
    chats: CursorPage[ChatSchema],
    db_session: AsyncSession,
) -> dict[UUID, ReadStatus]:
    """Helper functions for get user's read statuses."""
    read_status_query = select(ReadStatus).where(
        ReadStatus.user_id == current_user.id,
        ReadStatus.chat_id.in_([chat.id for chat in chats.items]),
    )
    read_statuses = await db_session.execute(read_status_query)
    return {status.chat_id: status for status in read_statuses.scalars().all()}


async def get_draft_messages(
    current_user: User,
    chats: CursorPage[ChatSchema],
    db_session: AsyncSession,
) -> dict[UUID, str]:
    """Helper functions for get user's draft messages."""
    draft_messages_query = select(DraftMessage).where(
        DraftMessage.user_id == current_user.id,
        DraftMessage.chat_id.in_([chat.id for chat in chats.items]),
    )
    draft_messages = await db_session.execute(draft_messages_query)
    return {dm.chat_id: dm.content for dm in draft_messages.scalars().all()}
