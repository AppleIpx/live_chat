from typing import AsyncGenerator

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from tests.utils import get_first_user_from_db


@pytest.mark.anyio
async def test_recover_user(
    authorized_deleted_client: AsyncClient,
    override_get_async_session: AsyncGenerator[AsyncSession, None],
    dbsession: AsyncSession,
) -> None:
    """Testing to recover deleted user."""
    response = await authorized_deleted_client.post("/api/recover/me")
    user = await get_first_user_from_db(db_session=dbsession)
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {
        "first_name": user.first_name,
        "last_name": user.last_name,
        "username": user.username,
        "user_image": user.user_image,
        "last_online": user.last_online,
        "is_deleted": False,
        "id": str(user.id),
    }


@pytest.mark.anyio
async def test_recovering_not_deleted_user(
    authorized_client: AsyncClient,
    override_get_async_session: AsyncGenerator[AsyncSession, None],
    dbsession: AsyncSession,
) -> None:
    """Testing to recover not deleted user."""
    response = await authorized_client.post("/api/recover/me")
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json() == {"detail": "You are not deleted."}
