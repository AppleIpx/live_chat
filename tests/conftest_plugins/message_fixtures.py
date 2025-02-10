from typing import Any, List
from unittest.mock import AsyncMock, patch

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from live_chat.db.models.chat import User
from live_chat.web.api.users.utils import get_user_by_id
from tests.factories import (
    ChatFactory,
    DeletedMessageFactory,
    DraftMessageFactory,
    MessageFactory,
    ReactionFactory,
    UserFactory,
)
from tests.utils import get_first_user_from_db


@pytest.fixture
async def message(
    dbsession: AsyncSession,
    user: UserFactory,
    chat: ChatFactory,
) -> MessageFactory:
    """Fixture for creating a message."""
    MessageFactory._meta.sqlalchemy_session = dbsession  # noqa: SLF001
    return MessageFactory(
        user=user,
        chat=chat,
        chat_id=chat.id,
        user_id=user.id,
    )


@pytest.fixture
async def draft_message(
    dbsession: AsyncSession,
    any_chat_with_users: ChatFactory,
) -> DraftMessageFactory:
    """Fixture for creating a draft message."""
    DraftMessageFactory._meta.sqlalchemy_session = dbsession  # noqa: SLF001
    auth_user = await get_first_user_from_db(dbsession)
    return DraftMessageFactory(
        user=auth_user,
        chat=any_chat_with_users,
        chat_id=any_chat_with_users.id,
        user_id=auth_user.id,
    )


@pytest.fixture
async def deleted_message(
    dbsession: AsyncSession,
    user: UserFactory,
    chat: ChatFactory,
) -> DeletedMessageFactory:
    """Fixture for creating a deleted message."""
    DeletedMessageFactory._meta.sqlalchemy_session = dbsession  # noqa: SLF001
    return DeletedMessageFactory(
        user=user,
        chat=chat,
        chat_id=chat.id,
        user_id=user.id,
    )


@pytest.fixture
async def some_deleted_messages(
    dbsession: AsyncSession,
    some_chats_with_users: List[ChatFactory],
) -> List[DeletedMessageFactory]:
    """Fixture for creating a list deleted messages."""
    user: User | None = await get_first_user_from_db(dbsession)
    DeletedMessageFactory._meta.sqlalchemy_session = dbsession  # noqa: SLF001
    return [
        DeletedMessageFactory(
            user=user,
            chat=chat,
            user_id=user.id,
            chat_id=chat.id,
        )
        for chat in some_chats_with_users
    ]


@pytest.fixture
def mocked_publish_message() -> AsyncMock:
    """Mock publish message in redis."""
    with patch(
        "live_chat.web.api.messages.utils.publish_message.fast_stream_broker.publish",
        new=AsyncMock(),
    ) as mock_publish:
        yield mock_publish


@pytest.fixture
def message_data(
    message: MessageFactory,
    direct_chat_with_users: ChatFactory,
) -> dict[str, Any]:
    """Return dict with message data."""
    return {
        "message_id": f"{message.id}",
        "user_id": f"{direct_chat_with_users.users[0].id}",
        "chat_id": f"{direct_chat_with_users.id}",
        "content": "Test message",
        "created_at": message.created_at.isoformat(),
    }


@pytest.fixture
async def reaction(
    dbsession: AsyncSession,
    message_in_chat: MessageFactory,
) -> ReactionFactory:
    """Fixture for creating a reaction."""
    ReactionFactory._meta.sqlalchemy_session = dbsession  # noqa: SLF001
    sender_id = message_in_chat.chat.users[0].id
    sender = await get_user_by_id(db_session=dbsession, user_id=sender_id)

    return ReactionFactory(
        user=sender,
        user_id=sender.id,
        message=message_in_chat,
        message_id=message_in_chat.id,
    )
