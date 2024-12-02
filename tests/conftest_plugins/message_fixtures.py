from typing import Any
from unittest.mock import AsyncMock, patch

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from tests.factories import ChatFactory, MessageFactory, UserFactory


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
