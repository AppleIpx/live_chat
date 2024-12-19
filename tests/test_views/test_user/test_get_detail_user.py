import secrets
import uuid
from typing import AsyncGenerator, List

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from live_chat.web.api.users.utils import get_user_by_id
from tests.factories import BlackListFactory, UserFactory


@pytest.mark.anyio
async def test_get_user_by_id(
    authorized_client: AsyncClient,
    some_users: List[UserFactory],
    override_get_async_session: AsyncGenerator[AsyncSession, None],
    dbsession: AsyncSession,
) -> None:
    """Test get user by id."""
    selected_user = secrets.choice(some_users)
    response = await authorized_client.get(f"/api/users/read/{selected_user.id}")
    assert response.status_code == status.HTTP_200_OK
    user = await get_user_by_id(user_id=selected_user.id, db_session=dbsession)
    assert response.json() == {
        "id": str(user.id),
        "email": user.email,
        "is_active": user.is_active,
        "is_superuser": user.is_superuser,
        "is_verified": user.is_verified,
        "first_name": user.first_name,
        "last_name": user.last_name,
        "username": user.username,
        "user_image": user.user_image,
        "is_blocked": False,
    }


@pytest.mark.anyio
async def test_get_user_blocked_by_sender(
    authorized_client: AsyncClient,
    user: UserFactory,
    black_list_with_user: BlackListFactory,
    override_get_async_session: AsyncGenerator[AsyncSession, None],
    dbsession: AsyncSession,
) -> None:
    """Testing to get a user who is blocked by a sender."""
    response = await authorized_client.get(f"/api/users/read/{user.id}")
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json() == {
        "detail": "You can't perform this action, because he's blocked",
    }


@pytest.mark.anyio
async def test_get_user_blocked_by_recipient(
    authorized_client: AsyncClient,
    user: UserFactory,
    black_list_with_auth_user: BlackListFactory,
    override_get_async_session: AsyncGenerator[AsyncSession, None],
    dbsession: AsyncSession,
) -> None:
    """Testing to get a user who is blocked by a recipient."""
    response = await authorized_client.get(f"/api/users/read/{user.id}")
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json() == {
        "detail": "You can't perform this action, you are on the black list",
    }


@pytest.mark.anyio
async def test_get_not_existing_user(
    authorized_client: AsyncClient,
    override_get_async_session: AsyncGenerator[AsyncSession, None],
    dbsession: AsyncSession,
) -> None:
    """Test get not existing user by id."""
    response = await authorized_client.get(f"/api/users/read/{uuid.uuid4()}")
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {
        "detail": "User not found",
    }
