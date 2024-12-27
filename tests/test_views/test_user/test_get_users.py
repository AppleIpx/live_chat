from typing import AsyncGenerator, List

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from live_chat.web.api.users.utils import get_user_by_id
from tests.factories import UserFactory


@pytest.mark.anyio
async def test_get_all_users(
    authorized_client: AsyncClient,
    some_users: List[UserFactory],
    override_get_async_session: AsyncGenerator[AsyncSession, None],
    dbsession: AsyncSession,
) -> None:
    """Test get all users."""
    response = await authorized_client.get("/api/users")
    assert response.status_code == status.HTTP_200_OK
    assert len(response.json()["items"]) == 6
    for user_data in response.json()["items"]:
        user = await get_user_by_id(user_id=user_data["id"], db_session=dbsession)
        assert user_data == {
            "id": str(user.id),
            "is_deleted": user.is_deleted,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "last_online": (
                user.last_online.isoformat().replace("+00:00", "Z")
                if user.last_online
                else None
            ),
            "username": user.username,
            "user_image": user.user_image,
        }
