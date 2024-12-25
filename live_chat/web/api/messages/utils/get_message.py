from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from live_chat.db.models.chat import (  # type: ignore[attr-defined]
    DeletedMessage,
    Message,
)


async def get_message_by_id(
    db_session: AsyncSession,
    *,
    message_id: UUID,
) -> Message | None:
    """Function to get a message by his id from db."""
    query = (
        select(Message)
        .options(selectinload(Message.reactions))
        .where(Message.id == message_id)
    )
    result = await db_session.execute(query)
    return result.scalar_one_or_none()


async def get_deleted_message_by_id(
    db_session: AsyncSession,
    *,
    deleted_message_id: UUID,
) -> DeletedMessage | None:
    """Function to get a deleted message by his id from db."""
    query = select(DeletedMessage).where(DeletedMessage.id == deleted_message_id)
    result = await db_session.execute(query)
    return result.scalar_one_or_none()


async def get_deleted_by_orig_message_id(
    db_session: AsyncSession,
    *,
    orig_message_id: UUID,
) -> DeletedMessage | None:
    """Function to get a deleted message by original_message_id from db."""
    query = select(DeletedMessage).where(
        DeletedMessage.original_message_id == orig_message_id,
    )
    result = await db_session.execute(query)
    return result.scalar_one_or_none()
