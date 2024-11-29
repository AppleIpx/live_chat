from typing import List

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from live_chat.db.models.chat import User
from live_chat.db.models.enums import ChatType
from tests.factories import ChatFactory, MessageFactory, UserFactory
from tests.utils import get_first_user_from_db


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
    sender: User | None = await get_first_user_from_db(dbsession)
    recipient = user
    return ChatFactory(users=[sender, recipient])


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
    return [ChatFactory(users=[sender, recipient]) for recipient in some_users]


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
