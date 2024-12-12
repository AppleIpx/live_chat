from typing import List

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from live_chat.db.models.chat import User
from live_chat.db.models.enums import ChatType
from tests.factories import (
    ChatFactory,
    DeletedMessageFactory,
    MessageFactory,
    ReadStatusFactory,
    UserFactory,
)
from tests.utils import get_first_user_from_db


async def create_read_status_for_chat(
    dbsession: AsyncSession,
    chat: ChatFactory,
    user: User,
) -> None:
    """Helper function for creating read status."""
    ReadStatusFactory(
        chat_id=chat.id,
        chat=chat,
        user=user,
        user_id=user.id,
        last_read_message_id=None,
        count_unread_msg=0,
    )


@pytest.fixture
async def chat(dbsession: AsyncSession) -> ChatFactory:
    """A fixture for generating a chat factory."""
    ChatFactory._meta.sqlalchemy_session = dbsession  # noqa: SLF001
    return ChatFactory()


@pytest.fixture
async def any_chat_with_users(
    user: UserFactory,
    dbsession: AsyncSession,
) -> ChatFactory:
    """A fixture for generating a chat factory with sender and recipient."""
    ChatFactory._meta.sqlalchemy_session = dbsession  # noqa: SLF001
    ReadStatusFactory._meta.sqlalchemy_session = dbsession  # noqa: SLF001
    sender: User | None = await get_first_user_from_db(dbsession)
    recipient = user
    chat = ChatFactory(users=[sender, recipient])
    await create_read_status_for_chat(dbsession=dbsession, chat=chat, user=sender)
    await create_read_status_for_chat(dbsession=dbsession, chat=chat, user=recipient)
    return chat


@pytest.fixture
async def direct_chat_with_users(
    user: UserFactory,
    dbsession: AsyncSession,
) -> ChatFactory:
    """A fixture for generating a chat factory with sender and recipient."""
    ChatFactory._meta.sqlalchemy_session = dbsession  # noqa: SLF001
    sender: User | None = await get_first_user_from_db(dbsession)
    recipient = user
    return ChatFactory(users=[sender, recipient], chat_type=ChatType.DIRECT)


@pytest.fixture
async def group_chat_with_users(
    some_users: UserFactory,
    dbsession: AsyncSession,
) -> ChatFactory:
    """A fixture for generating a chat factory with sender and recipient."""
    ChatFactory._meta.sqlalchemy_session = dbsession  # noqa: SLF001
    sender: User | None = await get_first_user_from_db(dbsession)
    return ChatFactory(users=[sender, *some_users], chat_type=ChatType.GROUP)


@pytest.fixture
async def some_chats_with_users(
    authorized_client: AsyncClient,
    some_users: List[UserFactory],
    dbsession: AsyncSession,
) -> List[ChatFactory]:
    """A fixture for generating five chats factory."""
    sender: User | None = await get_first_user_from_db(dbsession)
    ChatFactory._meta.sqlalchemy_session = dbsession  # noqa: SLF001
    ReadStatusFactory._meta.sqlalchemy_session = dbsession  # noqa: SLF001
    chats: List[ChatFactory] = [
        ChatFactory(
            users=[sender, recipient],
        )
        for recipient in some_users
    ]
    for chat in chats:
        await create_read_status_for_chat(dbsession, chat, sender)
    return chats


@pytest.fixture
async def message_in_chat(
    dbsession: AsyncSession,
    any_chat_with_users: ChatFactory,
) -> MessageFactory:
    """Fixture for creating a chat message."""
    MessageFactory._meta.sqlalchemy_session = dbsession  # noqa: SLF001
    sender = any_chat_with_users.users[0]
    return MessageFactory(
        user=sender,
        user_id=sender.id,
        chat=any_chat_with_users,
        chat_id=any_chat_with_users.id,
        is_deleted=False,
    )


@pytest.fixture
async def deleted_message_in_chat(
    dbsession: AsyncSession,
    message_in_chat: MessageFactory,
) -> DeletedMessageFactory:
    """Fixture for creating a chat with deleted message."""
    message_in_chat.is_deleted = True
    user = message_in_chat.chat.users[0]
    DeletedMessageFactory._meta.sqlalchemy_session = dbsession  # noqa: SLF001
    return DeletedMessageFactory(
        original_message_id=message_in_chat.id,
        user=user,
        user_id=user.id,
        chat=message_in_chat.chat,
        chat_id=message_in_chat.chat.id,
    )


@pytest.fixture
async def many_messages(
    dbsession: AsyncSession,
    any_chat_with_users: ChatFactory,
) -> List[MessageFactory]:
    """Fixture for creating a chat message."""
    MessageFactory._meta.sqlalchemy_session = dbsession  # noqa: SLF001
    sender = any_chat_with_users.users[0]
    return MessageFactory.create_batch(
        10,
        user=sender,
        user_id=sender.id,
        chat=any_chat_with_users,
        chat_id=any_chat_with_users.id,
    )
