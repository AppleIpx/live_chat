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
