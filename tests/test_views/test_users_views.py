import secrets
from typing import AsyncGenerator, List

import pytest
from fastapi import status
from httpx import AsyncClient, Response
from sqlalchemy.ext.asyncio import AsyncSession

from tests.factories import UserFactory

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
class TestUsersViews:
    """Testing the User view."""

    async def test_registrations_users(
        self,
        client: AsyncClient,
        registered_user: Response,
        dbsession: AsyncGenerator[AsyncSession, None],
    ) -> None:
        """Test registration and check user's fields."""
        assert registered_user.status_code == status.HTTP_201_CREATED
        data = registered_user.json()
        for key, value in payload.items():
            if key == "password":
                continue
            assert data[key] == value

    async def test_login_users(
        self,
        client: AsyncClient,
        registered_user: Response,
        dbsession: AsyncGenerator[AsyncSession, None],
    ) -> None:
        """Test to verify user login."""
        data = registered_user.json()

        login_payload = {
            "username": data["email"],
            "password": "string",
        }

        response = await client.post(
            "/api/auth/jwt/login",
            data=login_payload,
        )

        assert response.status_code == status.HTTP_200_OK

        response_data = response.json()
        assert "access_token" in response_data
        assert response_data["access_token"] is not None

    async def test_users_me(
        self,
        authorized_client: AsyncClient,
        dbsession: AsyncGenerator[AsyncSession, None],
    ) -> None:
        """Test get users me."""
        response = await authorized_client.get("/api/users/me")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        for key, value in payload.items():
            if key == "password":
                continue
            assert data[key] == value

    async def test_get_all_users(
        self,
        authorized_client: AsyncClient,
        some_users: List[UserFactory],
        override_get_async_session: AsyncGenerator[AsyncSession, None],
    ) -> None:
        """Test get all users."""
        response = await authorized_client.get("/api/users")
        assert response.status_code == status.HTTP_200_OK
        returned_users = response.json()
        assert len(returned_users["users"]) == 6

    async def test_get_user_by_id(
        self,
        authorized_client: AsyncClient,
        some_users: List[UserFactory],
        override_get_async_session: AsyncGenerator[AsyncSession, None],
    ) -> None:
        """Test get user by id."""
        selected_user = secrets.choice(some_users)
        response = await authorized_client.get(f"/api/users/read/{selected_user.id}")
        data = response.json()
        assert response.status_code == status.HTTP_200_OK
        for key, value in data.items():
            assert data[key] == value
