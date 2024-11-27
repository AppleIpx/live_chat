from typing import List

import pytest
from httpx import AsyncClient, Response
from sqlalchemy.ext.asyncio import AsyncSession

from tests.factories import UserFactory
from tests.utils import payload


@pytest.fixture
async def user(dbsession: AsyncSession) -> UserFactory:
    """A fixture for generating a user factory."""
    UserFactory._meta.sqlalchemy_session = dbsession  # noqa: SLF001
    return UserFactory()


@pytest.fixture
async def some_users(dbsession: AsyncSession) -> List[UserFactory]:
    """A fixture for generating five users factory."""
    UserFactory._meta.sqlalchemy_session = dbsession  # noqa: SLF001
    return UserFactory.create_batch(5)


@pytest.fixture
async def registered_user(client: AsyncClient) -> Response:
    """Fixture for user registration."""
    return await client.post("/api/auth/register", json=payload)
