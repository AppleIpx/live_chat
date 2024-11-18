from typing import AsyncGenerator

import pytest
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from live_chat.db.models.chat import Message
from tests.factories import MessageFactory


@pytest.mark.anyio
class TestMessage:
    """Testing the Message model."""

    async def test_check_fields_message(self, create_message: MessageFactory) -> None:
        """Проверка полей сообщения."""
        message = create_message
        expected_attributes = {
            "id": message.id,
            "created_at": message.created_at,
            "updated_at": message.updated_at,
            "is_deleted": message.is_deleted,
            "message_type": message.message_type,
            "content": message.content,
            "user": message.user,
            "chat": message.chat,
        }
        for attr, expected_value in expected_attributes.items():
            assert getattr(message, attr) == expected_value

    async def test_check_save_message(
        self,
        create_message: MessageFactory,
        dbsession: AsyncGenerator[AsyncSession, None],
    ) -> None:
        """Checking whether the message is saved in the db."""
        _ = create_message
        count = await dbsession.execute(select(func.count(Message.id)))
        count = count.scalar()
        assert count == 1

    async def test_check_message_init(self, create_message: MessageFactory) -> None:
        """Checking the string representation of the message."""
        message = create_message
        expected_init = (
            f"Message from {message.user_id} - {message.chat_id} - {message.created_at}"
        )
        assert str(message) == expected_init
