import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from tests.factories import ChatFactory, ReadStatusFactory, UserFactory


@pytest.fixture
async def read_status(
    dbsession: AsyncSession,
    user: UserFactory,
    chat: ChatFactory,
) -> ReadStatusFactory:
    """Fixture for creating a read status."""
    ReadStatusFactory._meta.sqlalchemy_session = dbsession  # noqa: SLF001
    return ReadStatusFactory(
        user=user,
        chat=chat,
        user_id=user.id,
        chat_id=chat.id,
    )
