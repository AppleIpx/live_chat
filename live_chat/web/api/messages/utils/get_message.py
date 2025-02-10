from typing import Any
from uuid import UUID

from fastapi import HTTPException
from sqlalchemy import select
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
        .options(selectinload(Message.reactions))
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


async def get_formatted_messages_by_chat(
    db_session: AsyncSession,
    *,
    chat_id: UUID,
    current_user_id: UUID,
) -> dict[Any, str]:
    """Function to get a formatted messages by chat_id from db."""
    query = (
        select(Message.content, Message.user_id, Message.created_at)
        .where(Message.chat_id == chat_id, Message.message_type == MessageType.TEXT)
        .order_by(Message.created_at)
    )
    result = await db_session.execute(query)
    messages = result.all()
    formatted_messages: dict[str, list[str]] = {}
    previous_date = None
    for content, user_id, created_at in messages:
        formatted_user = "Я" if user_id == current_user_id else "Другой пользователь"
        message_date = created_at.date().isoformat()
        if previous_date != message_date:
            previous_date = message_date
        if message_date not in formatted_messages:
            formatted_messages[message_date] = []
        formatted_messages[message_date].append(f"{formatted_user}: {content}")
    return {date: "\n".join(messages) for date, messages in formatted_messages.items()}
