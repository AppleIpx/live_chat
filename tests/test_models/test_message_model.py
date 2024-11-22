from typing import AsyncGenerator

import pytest
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from live_chat.db.models.chat import Message
from live_chat.web.api.chat.utils.get_message_by_id import get_message_by_id
from tests.factories import MessageFactory


@pytest.mark.anyio
async def test_check_fields_message(
    message: MessageFactory,
    dbsession: AsyncSession,
) -> None:
    """Checking message fields."""
    message_db = await get_message_by_id(message_id=message.id, db_session=dbsession)
    assert message.id == message_db.id
    assert message.message_type == message_db.message_type
    assert message.updated_at == message_db.updated_at
    assert message.is_deleted == message_db.is_deleted
    assert message.updated_at == message_db.updated_at
    assert message.user == message_db.user
    assert message.user_id == message_db.user_id
    assert message.content == message_db.content
    assert message.file_name == message_db.file_name
    assert message.file_path == message_db.file_path


@pytest.mark.anyio
async def test_check_save_message(
    message: MessageFactory,
    dbsession: AsyncGenerator[AsyncSession, None],
) -> None:
    """Checking whether the message is saved in the db."""
    count = await dbsession.execute(select(func.count(Message.id)))
    assert count.scalar() == 1


@pytest.mark.anyio
async def test_check_message_init(message: MessageFactory) -> None:
    """Checking the string representation of the message."""
    expected_init = (
        f"Message from {message.user_id} - {message.chat_id} - {message.created_at}"
    )
    assert str(message) == expected_init
