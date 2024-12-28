import uuid
from typing import AsyncGenerator

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from live_chat.web.api.black_list.utils import get_blocked_users
from tests.factories import BlackListFactory, UserFactory


@pytest.mark.anyio
async def test_delete_user_from_black_list(
    authorized_client: AsyncClient,
    black_list_with_user: BlackListFactory,
    user: UserFactory,
    override_get_async_session: AsyncGenerator[AsyncSession, None],
    dbsession: AsyncSession,
) -> None:
    """Test for deleting a user from a blacklist."""
    response = await authorized_client.request(
        method="DELETE",
        url="/api/black-list",
        json={"user_id": str(user.id)},
    )
    blocked_users = await get_blocked_users(
        black_list=black_list_with_user,
        db_session=dbsession,
    )
    for blocked_user in blocked_users:
        assert blocked_user != user.id
    assert response.status_code == status.HTTP_204_NO_CONTENT


@pytest.mark.anyio
async def test_delete_not_existing_user(
    authorized_client: AsyncClient,
    black_list_with_user: BlackListFactory,
    override_get_async_session: AsyncGenerator[AsyncSession, None],
    dbsession: AsyncSession,
) -> None:
    """Test for deleting a not existing user from a blacklist."""
    response = await authorized_client.request(
        method="DELETE",
        url="/api/black-list",
        json={"user_id": str(uuid.uuid4())},
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {"detail": "No user with this id found"}


@pytest.mark.anyio
async def test_delete_user_with_not_existing_black_list(
    authorized_client: AsyncClient,
    user: UserFactory,
    override_get_async_session: AsyncGenerator[AsyncSession, None],
    dbsession: AsyncSession,
) -> None:
    """Test for deleting a user from not existing blacklist."""
    response = await authorized_client.request(
        method="DELETE",
        url="/api/black-list",
        json={"user_id": str(user.id)},
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {"detail": "Black list not found"}


@pytest.mark.anyio
async def test_delete_not_existing_user_in_black_list(
    authorized_client: AsyncClient,
    black_list_owner_auth_user: BlackListFactory,
    user: UserFactory,
    override_get_async_session: AsyncGenerator[AsyncSession, None],
    dbsession: AsyncSession,
) -> None:
    """Test for deleting not existing user in blacklist."""
    response = await authorized_client.request(
        method="DELETE",
        url="/api/black-list",
        json={"user_id": str(user.id)},
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {"detail": "User not found in black list"}


@pytest.mark.anyio
async def test_delete_user_from_blacklist_by_deleted_user(
    authorized_deleted_client: AsyncClient,
    user: UserFactory,
    dbsession: AsyncSession,
) -> None:
    """Testing to delete a user from blacklist by a deleted user."""
    response = await authorized_deleted_client.request(
        method="DELETE",
        url="/api/black-list",
        json={"user_id": str(user.id)},
    )
    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert response.json() == {"detail": "You are deleted."}
