import uuid
from typing import AsyncGenerator

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from live_chat.web.api.black_list.utils import get_blocked_users
from live_chat.web.api.users.utils import get_user_by_id
from tests.factories import BlackListFactory, BlockedUsersFactory, UserFactory
from tests.utils import get_first_black_list_from_db, get_first_user_from_db


@pytest.mark.anyio
async def test_add_user_to_new_black_list(
    authorized_client: AsyncClient,
    user: UserFactory,
    override_get_async_session: AsyncGenerator[AsyncSession, None],
    dbsession: AsyncSession,
) -> None:
    """Test for adding a user to a blacklist and creating a new blacklist."""
    response = await authorized_client.post(
        "/api/black-list",
        json={"user_id": f"{user.id}"},
    )
    black_list = await get_first_black_list_from_db(db_session=dbsession)
    auth_user = await get_first_user_from_db(db_session=dbsession)
    black_list_user = await get_user_by_id(db_session=dbsession, user_id=user.id)
    assert response.status_code == status.HTTP_201_CREATED
    assert response.json() == {
        "id": str(black_list.id),
        "owner_id": str(auth_user.id),
        "blocked_user": {
            "first_name": black_list_user.first_name,
            "last_name": black_list_user.last_name,
            "username": black_list_user.username,
            "user_image": black_list_user.user_image,
            "last_online": (
                black_list_user.last_online.isoformat().replace("+00:00", "Z")
                if black_list_user.last_online
                else None
            ),
            "id": str(black_list_user.id),
        },
    }


@pytest.mark.anyio
async def test_add_user_to_existing_black_list(
    authorized_client: AsyncClient,
    user: UserFactory,
    black_list_with_users: BlackListFactory,
    override_get_async_session: AsyncGenerator[AsyncSession, None],
    dbsession: AsyncSession,
) -> None:
    """Test for adding a user to existing blacklist and check count of users."""
    response = await authorized_client.post(
        "/api/black-list",
        json={"user_id": f"{user.id}"},
    )
    black_list_with_users = await get_first_black_list_from_db(db_session=dbsession)
    blocked_users = await get_blocked_users(
        black_list=black_list_with_users,
        db_session=dbsession,
    )
    auth_user = await get_first_user_from_db(db_session=dbsession)
    black_list_user = await get_user_by_id(db_session=dbsession, user_id=user.id)
    assert response.status_code == status.HTTP_201_CREATED
    assert response.json() == {
        "id": str(black_list_with_users.id),
        "owner_id": str(auth_user.id),
        "blocked_user": {
            "first_name": black_list_user.first_name,
            "last_name": black_list_user.last_name,
            "username": black_list_user.username,
            "user_image": black_list_user.user_image,
            "last_online": (
                black_list_user.last_online.isoformat().replace("+00:00", "Z")
                if black_list_user.last_online
                else None
            ),
            "id": str(black_list_user.id),
        },
    }
    assert len(blocked_users) == 6


@pytest.mark.anyio
async def test_add_yourself_to_the_black_list(
    authorized_client: AsyncClient,
    override_get_async_session: AsyncGenerator[AsyncSession, None],
    dbsession: AsyncSession,
) -> None:
    """Testing for adding yourself to the black list."""
    auth_user = await get_first_user_from_db(db_session=dbsession)
    response = await authorized_client.post(
        "/api/black-list",
        json={"user_id": f"{auth_user.id}"},
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json() == {
        "detail": "It is impossible to add yourself to the blacklist",
    }


@pytest.mark.anyio
async def test_add_invalid_user_to_black_list(
    authorized_client: AsyncClient,
    override_get_async_session: AsyncGenerator[AsyncSession, None],
    dbsession: AsyncSession,
) -> None:
    """Test for adding invalid user to the blacklist."""
    response = await authorized_client.post(
        "/api/black-list",
        json={"user_id": f"{uuid.uuid4()}"},
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {"detail": "No user with this id found"}


@pytest.mark.anyio
async def test_to_add_an_existing_user_to_the_blacklist(
    authorized_client: AsyncClient,
    user: UserFactory,
    black_list_with_users: BlackListFactory,
    override_get_async_session: AsyncGenerator[AsyncSession, None],
    dbsession: AsyncSession,
) -> None:
    """Test for adding an existing user to the blacklist."""
    black_list_from_db = await get_first_black_list_from_db(db_session=dbsession)
    BlockedUsersFactory(blacklist_id=black_list_from_db.id, user_id=user.id)
    response = await authorized_client.post(
        "/api/black-list",
        json={"user_id": f"{user.id}"},
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json() == {"detail": f"User {user.id} already blocked"}
