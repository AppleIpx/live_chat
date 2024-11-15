from typing import AsyncGenerator

import pytest
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from live_chat.db.models.chat import Chat, Message, ReadStatus, User
from tests.factories import ChatFactory, MessageFactory, ReadStatusFactory, UserFactory


@pytest.mark.anyio
class TestUser:
    """Testing the User model."""

    async def test_check_fields_user(
        self,
        user_factory: UserFactory,
        dbsession: AsyncGenerator[AsyncSession, None],
    ) -> None:
        """Checking user fields."""
        user = user_factory.create()

        expected_attributes = {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "last_login": user.last_login,
            "created_at": user.created_at,
            "updated_at": user.updated_at,
            "is_active": user.is_active,
            "is_superuser": user.is_superuser,
            "is_verified": user.is_verified,
        }

        for attr, expected_value in expected_attributes.items():
            assert getattr(user, attr) == expected_value

    async def test_check_save_user(
        self,
        user_factory: UserFactory,
        dbsession: AsyncGenerator[AsyncSession, None],
    ) -> None:
        """Checking whether the user is saved in the db."""
        user_factory.create()
        count = await dbsession.execute(select(func.count(User.id)))
        count = count.scalar()

        assert count == 1

    async def test_check_user_init(
        self,
        user_factory: UserFactory,
        dbsession: AsyncGenerator[AsyncSession, None],
    ) -> None:
        """Checking the string representation of the user."""
        user = user_factory.create()
        expected_init = f"{user.username}"
        assert str(user) == expected_init


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


@pytest.mark.anyio
class TestReadStatus:
    """Testing the ReadStatus model."""

    async def test_check_fields_read_status(
        self,
        create_read_status: ReadStatusFactory,
    ) -> None:
        """Checking ReadStatus fields."""
        read_status = create_read_status
        expected_attributes = {
            "id": read_status.id,
            "created_at": read_status.created_at,
            "updated_at": read_status.updated_at,
            "is_deleted": read_status.is_deleted,
            "last_read_message_id": read_status.last_read_message_id,
            "user": read_status.user,
            "chat": read_status.chat,
        }
        for attr, expected_value in expected_attributes.items():
            assert getattr(read_status, attr) == expected_value

    async def test_check_save_read_status(
        self,
        create_read_status: ReadStatusFactory,
        dbsession: AsyncGenerator[AsyncSession, None],
    ) -> None:
        """Checking whether the ReadStatus is saved in the db."""
        _ = create_read_status
        count = await dbsession.execute(select(func.count(ReadStatus.id)))
        count = count.scalar()
        assert count == 1

    async def test_check_readstatus_init(
        self,
        create_read_status: ReadStatusFactory,
    ) -> None:
        """Checking the string representation of the readstatus."""
        read_status = create_read_status
        expected_init = (
            f"User: {read_status.user_id}, Message: {read_status.last_read_message_id}"
        )
        assert str(read_status) == expected_init
