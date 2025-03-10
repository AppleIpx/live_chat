from typing import AsyncGenerator

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from tests.utils import get_first_user_from_db


@pytest.mark.anyio
async def test_delete_me(
    authorized_client: AsyncClient,
    override_get_async_session: AsyncGenerator[AsyncSession, None],
    dbsession: AsyncSession,
) -> None:
    """Testing to delete user."""
    response = await authorized_client.delete("/api/users/me/delete")
    user = await get_first_user_from_db(db_session=dbsession)
    assert response.status_code == status.HTTP_204_NO_CONTENT
    assert user.is_deleted is True


@pytest.mark.anyio
async def test_delete_me_by_deleted_user(
    authorized_deleted_client: AsyncClient,
    override_get_async_session: AsyncGenerator[AsyncSession, None],
    dbsession: AsyncSession,
) -> None:
    """Testing deleting a remote user."""
    response = await authorized_deleted_client.delete("/api/users/me/delete")
    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert response.json() == {"detail": "You are deleted."}


@pytest.mark.anyio
async def test_delete_me_by_banned_user(
    authorized_banned_client: AsyncClient,
    override_get_async_session: AsyncGenerator[AsyncSession, None],
    dbsession: AsyncSession,
) -> None:
    """Testing deleting a remote user."""
    response = await authorized_banned_client.delete("/api/users/me/delete")
    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert response.json() == {
        "detail": {
            "reason": None,
            "status": "banned",
        },
    }
