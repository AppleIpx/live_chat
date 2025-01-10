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


async def get_rs_and_dm(
    current_user: User,
    chats: CursorPage[ChatSchema],
    db_session: AsyncSession,
) -> tuple[dict[UUID, ReadStatus], dict[UUID, str]]:
    """Function for getting read statuses and draft messages."""
    read_status_query = select(ReadStatus).where(
        ReadStatus.user_id == current_user.id,
        ReadStatus.chat_id.in_([chat.id for chat in chats.items]),
    )
    read_statuses = await db_session.execute(read_status_query)
    read_status_dict = {
        status.chat_id: status for status in read_statuses.scalars().all()
    }
    draft_messages_query = select(DraftMessage).where(
        DraftMessage.user_id == current_user.id,
        DraftMessage.chat_id.in_([chat.id for chat in chats.items]),
    )
    draft_messages = await db_session.execute(draft_messages_query)
    draft_messages_dict = {
        dm.chat_id: dm.content for dm in draft_messages.scalars().all()
    }
    return read_status_dict, draft_messages_dict
