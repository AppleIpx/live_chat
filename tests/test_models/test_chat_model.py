from typing import AsyncGenerator

import pytest
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from live_chat.db.models.chat import Chat
from tests.factories import ChatFactory


@pytest.mark.anyio
class TestChat:
    """Testing the Chat model."""

    async def test_check_fields_chat(
        self,
        chat_factory: ChatFactory,
        dbsession: AsyncGenerator[AsyncSession, None],
    ) -> None:
        """Checking chat fields."""
        chat = chat_factory.create()

        expected_attributes = {
            "id": chat.id,
            "created_at": chat.created_at,
            "updated_at": chat.updated_at,
            "chat_type": chat.chat_type,
        }
        for attr, expected_value in expected_attributes.items():
            assert getattr(chat, attr) == expected_value

    async def test_check_save_chat(
        self,
        chat_factory: ChatFactory,
        dbsession: AsyncGenerator[AsyncSession, None],
    ) -> None:
        """Checking whether the chat is saved in the db."""
        chat_factory.create()
        count = await dbsession.execute(select(func.count(Chat.id)))
        count = count.scalar()

        assert count == 1

    async def test_check_chat_init(
        self,
        chat_factory: ChatFactory,
        dbsession: AsyncGenerator[AsyncSession, None],
    ) -> None:
        """Checking the string representation of the chat."""
        chat = chat_factory.create()
        expected_init = f"{chat.chat_type.value.title()} {chat.id}"
        assert str(chat) == expected_init
