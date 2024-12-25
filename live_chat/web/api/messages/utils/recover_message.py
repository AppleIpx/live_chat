from datetime import datetime, timezone

from sqlalchemy import delete
from sqlalchemy.ext.asyncio import AsyncSession

from live_chat.db.models.chat import (  # type:ignore[attr-defined]
    DeletedMessage,
    Message,
)
from live_chat.web.api.messages.utils import get_message_by_id


async def restore_message(
    db_session: AsyncSession,
    deleted_message: DeletedMessage,
) -> Message | None:
    """Recover original message from deleted messages."""
    if message := await get_message_by_id(
        db_session,
        message_id=deleted_message.original_message_id,
    ):
        delete_statement = delete(DeletedMessage).where(
            DeletedMessage.id == deleted_message.id,
        )
        await db_session.execute(delete_statement)
        message.is_deleted = False
        message.updated_at = datetime.now(timezone.utc)
        db_session.add(message)
        await db_session.commit()
        return message
    return None
