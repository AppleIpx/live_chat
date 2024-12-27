from typing import AsyncGenerator

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from live_chat.web.api.black_list.utils import get_blocked_users
from live_chat.web.api.users.utils import get_user_by_id
from tests.factories import BlackListFactory


@pytest.mark.anyio
async def test_get_black_list(
    authorized_client: AsyncClient,
    black_list_with_users: BlackListFactory,
    override_get_async_session: AsyncGenerator[AsyncSession, None],
    dbsession: AsyncSession,
) -> None:
    """Test to getting list blocked users."""
    response = await authorized_client.get("/api/black-list")
    blocked_users = await get_blocked_users(
        black_list=black_list_with_users,
        db_session=dbsession,
    )
    blocked_users_db = {
        str(blocked_user.id): await get_user_by_id(
            user_id=blocked_user.id,
            db_session=dbsession,
        )
        for blocked_user in blocked_users
    }
    assert response.status_code == status.HTTP_200_OK
    for block_user in response.json()["items"]:
        block_user_db = blocked_users_db[str(block_user["id"])]
        assert block_user == {
            "first_name": block_user_db.first_name,
            "last_name": block_user_db.last_name,
            "username": block_user_db.username,
            "user_image": block_user_db.user_image,
            "last_online": (
                block_user_db.last_online.isoformat().replace("+00:00", "Z")
                if block_user_db.last_online
                else None
            ),
            "id": str(block_user_db.id),
            "is_deleted": block_user_db.is_deleted,
        }
    assert len(response.json()["items"]) == len(blocked_users)


@pytest.mark.anyio
async def test_get_empty_black_list(
    authorized_client: AsyncClient,
    override_get_async_session: AsyncGenerator[AsyncSession, None],
    dbsession: AsyncSession,
) -> None:
    """Test to getting empty list blocked users if there is no blacklist."""
    response = await authorized_client.get("/api/black-list")
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == []
