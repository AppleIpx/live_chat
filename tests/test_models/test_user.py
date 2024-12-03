from typing import AsyncGenerator

import pytest
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from live_chat.db.models.chat import User
from live_chat.web.api.users.utils import get_user_by_id
from tests.factories import UserFactory


@pytest.mark.anyio
async def test_check_fields_user(
    user: UserFactory,
    dbsession: AsyncSession,
) -> None:
    """Checking user fields."""
    user_db = await get_user_by_id(user_id=user.id, db_session=dbsession)
    assert user.id == user_db.id
    assert user.username == user_db.username
    assert user.email == user_db.email
    assert user.first_name == user_db.first_name
    assert user.last_name == user_db.last_name
    assert user.created_at == user_db.created_at
    assert user.updated_at == user_db.updated_at
    assert user.last_login == user_db.last_login
    assert user.user_image == user_db.user_image
    assert user.is_active == user_db.is_active
    assert user.is_verified == user_db.is_verified
    assert user.is_superuser == user_db.is_superuser


@pytest.mark.anyio
async def test_check_save_user(
    user: UserFactory,
    dbsession: AsyncGenerator[AsyncSession, None],
) -> None:
    """Checking whether the user is saved in the db."""
    count = await dbsession.execute(select(func.count(User.id)))
    assert count.scalar() == 1


@pytest.mark.anyio
async def test_check_user_init(
    user: UserFactory,
    dbsession: AsyncGenerator[AsyncSession, None],
) -> None:
    """Checking the string representation of the user."""
    expected_init = f"{user.username}"
    assert str(user) == expected_init
