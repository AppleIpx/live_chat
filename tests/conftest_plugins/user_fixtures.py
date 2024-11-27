from typing import List

import pytest
from httpx import AsyncClient, Response
from sqlalchemy.ext.asyncio import AsyncSession

from tests.factories import UserFactory


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


registration_payload = {
    "email": "user@example.com",
    "password": "string",
    "is_active": True,
    "is_superuser": False,
    "is_verified": False,
    "first_name": "string",
    "last_name": "string",
    "username": "string",
    "user_image": None,
}


@pytest.fixture
async def registered_user(client: AsyncClient) -> Response:
    """Fixture for user registration."""
    return await client.post("/api/auth/register", json=registration_payload)
