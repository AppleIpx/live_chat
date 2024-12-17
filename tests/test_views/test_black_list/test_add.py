from typing import AsyncGenerator

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from live_chat.web.api.users.utils import get_user_by_id
from tests.factories import UserFactory
from tests.utils import get_first_black_list_from_db, get_first_user_from_db


@pytest.mark.anyio
async def test_add_user_to_black_list(
    authorized_client: AsyncClient,
    user: UserFactory,
    override_get_async_session: AsyncGenerator[AsyncSession, None],
    dbsession: AsyncSession,
) -> None:
    """Test for adding a user to the blacklist."""
    response = await authorized_client.post(
        "/api/black-list",
        json={"user_id": f"{user.id}"},
    )
    black_list = await get_first_black_list_from_db(db_session=dbsession)
    auth_user = await get_first_user_from_db(db_session=dbsession)
    black_list_user = await get_user_by_id(db_session=dbsession, user_id=user.id)
    assert response.status_code == 200
    assert response.json == {
        "id": black_list.id,
        "owner_id": auth_user.id,
        "blocked_user": {
            "first_name": black_list_user.first_name,
            "last_name": black_list_user.last_name,
            "username": black_list_user.username,
            "user_image": black_list_user.user_image,
            "id": black_list_user.id,
        },
    }
