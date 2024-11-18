from typing import AsyncGenerator

import pytest
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from live_chat.db.models.chat import User
from tests.factories import UserFactory


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
