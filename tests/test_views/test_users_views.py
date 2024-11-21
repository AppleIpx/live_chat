import secrets
from typing import AsyncGenerator, List

import pytest
from fastapi import status
from httpx import AsyncClient, Response
from sqlalchemy.ext.asyncio import AsyncSession

from live_chat.web.api.users.utils.get_user_by_id import get_user_by_id
from tests.factories import UserFactory
from tests.utils import get_first_user_from_db

payload = {
    "email": "user@example.com",
    "password": "string",
    "is_active": True,
    "is_superuser": False,
    "is_verified": False,
    "first_name": "string",
    "last_name": "string",
    "username": "string",
    "user_image": None,
}


@pytest.mark.anyio
async def test_registrations_users(
    client: AsyncClient,
    dbsession: AsyncSession,
) -> None:
    """Test registration and check user's fields."""
    response = await client.post("/api/auth/register", json=payload)
    data = response.json()
    user = await get_first_user_from_db(dbsession)
    assert response.status_code == status.HTTP_201_CREATED
    assert data == {
        "id": str(user.id),
        "email": user.email,
        "is_active": user.is_active,
        "is_superuser": user.is_superuser,
        "is_verified": user.is_verified,
        "first_name": user.first_name,
        "last_name": user.last_name,
        "username": user.username,
        "user_image": user.user_image,
    }


@pytest.mark.anyio
async def test_login_users(
    client: AsyncClient,
    registered_user: Response,
    dbsession: AsyncSession,
) -> None:
    """Test to verify user login."""
    user = await get_first_user_from_db(dbsession)
    response = await client.post(
        "/api/auth/jwt/login",
        data={
            "username": user.email,
            "password": "string",
        },
    )
    data = response.json()
    assert response.status_code == status.HTTP_200_OK
    assert "access_token" in data
    assert data["access_token"] is not None


@pytest.mark.anyio
async def test_users_me(
    authorized_client: AsyncClient,
    dbsession: AsyncSession,
) -> None:
    """Test get users me."""
    response = await authorized_client.get("/api/users/me")
    user = await get_first_user_from_db(dbsession)
    data = response.json()
    assert response.status_code == status.HTTP_200_OK
    assert data == {
        "id": str(user.id),
        "email": user.email,
        "is_active": user.is_active,
        "is_superuser": user.is_superuser,
        "is_verified": user.is_verified,
        "first_name": user.first_name,
        "last_name": user.last_name,
        "username": user.username,
        "user_image": user.user_image,
    }


@pytest.mark.anyio
async def test_get_all_users(
    authorized_client: AsyncClient,
    some_users: List[UserFactory],
    override_get_async_session: AsyncGenerator[AsyncSession, None],
    dbsession: AsyncSession,
) -> None:
    """Test get all users."""
    response = await authorized_client.get("/api/users")
    data = response.json()
    assert response.status_code == status.HTTP_200_OK
    assert len(data["users"]) == 6
    for user_data in data["users"]:
        user = await get_user_by_id(user_id=user_data["id"], db_session=dbsession)
        assert user_data == {
            "id": str(user.id),
            "email": user.email,
            "is_active": user.is_active,
            "is_superuser": user.is_superuser,
            "is_verified": user.is_verified,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "username": user.username,
            "user_image": user.user_image,
        }


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
    data = response.json()
    assert response.status_code == status.HTTP_200_OK
    user = await get_user_by_id(user_id=selected_user.id, db_session=dbsession)
    assert data == {
        "id": str(user.id),
        "email": user.email,
        "is_active": user.is_active,
        "is_superuser": user.is_superuser,
        "is_verified": user.is_verified,
        "first_name": user.first_name,
        "last_name": user.last_name,
        "username": user.username,
        "user_image": user.user_image,
    }
