from datetime import datetime
from typing import Any, Sequence
from uuid import UUID

from fastapi import HTTPException
from sqlalchemy import Row, RowMapping, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from starlette import status

from live_chat.db.models.enums import MessageType
from live_chat.db.models.messages import DeletedMessage, Message


async def get_message_by_id(
    db_session: AsyncSession,
    *,
    message_id: UUID,
) -> Message | None:
    """Function to get a message by his id from db."""
    query = (
        select(Message)
        .options(
            selectinload(Message.reactions),
            selectinload(Message.forwarded_message),
        )
        .where(Message.id == message_id)
    )
    result = await db_session.execute(query)
    return result.scalar_one_or_none()


async def check_parent_message(
    db_session: AsyncSession,
    message_id: UUID | None,
) -> None:
    """Function to check if a message is parent of a message."""
    if (
        message_id is not None
        and await get_message_by_id(
            db_session=db_session,
            message_id=message_id,
        )
        is None
    ):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Parent message does not exist.",
        )


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


async def get_messages_range(
    db_session: AsyncSession,
    *,
    from_date: datetime,
    to_date: datetime,
    chat_id: UUID,
) -> list[Message]:
    """Function to get messages between two dates."""
    query = (
        select(Message)
        .options(selectinload(Message.reactions))
        .where(
            Message.chat_id == chat_id,
            Message.created_at >= from_date,
            Message.created_at <= to_date,
        )
    )
    result = await db_session.execute(query)
    return list(result.scalars().all())


async def get_messages_by_date(
    db_session: AsyncSession,
    *,
    chat_id: UUID,
    date_limit: datetime,
) -> Sequence[Row[Any] | RowMapping | Any]:
    """Function to get a messages by chat_id in selected date limit."""
    query = (
        select(Message.content, Message.user_id, Message.created_at)
        .where(
            Message.chat_id == chat_id,
            Message.message_type == MessageType.TEXT,
            Message.created_at >= date_limit,
        )
        .order_by(Message.created_at)
    )
    result = await db_session.execute(query)
    return result.all()
