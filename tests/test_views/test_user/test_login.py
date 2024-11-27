from unittest.mock import Mock

import pytest
from httpx import AsyncClient, Response
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from tests.utils import get_first_user_from_db, new_payload


@pytest.mark.anyio
async def test_login_users(
    client: AsyncClient,
    registered_user: Response,
    dbsession: AsyncSession,
    mocker: Mock,
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
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {
        "access_token": mocker.ANY,
        "token_type": "bearer",
    }


@pytest.mark.anyio
@pytest.mark.parametrize(
    "username, password",
    [
        ("wrong_email@example.com", "string"),
        ("user@example.com", "wrong_password"),
        ("wrong_email@example.com", "wrong_password"),
    ],
)
async def test_login_invalid_credentials(
    client: AsyncClient,
    dbsession: AsyncSession,
    username: str,
    password: str,
) -> None:
    """Test to verify user login with invalid credentials."""
    response = await client.post(
        "/api/auth/jwt/login",
        data={
            "username": username,
            "password": password,
        },
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json() == {
        "detail": "LOGIN_BAD_CREDENTIALS",
    }


@pytest.mark.anyio
@pytest.mark.parametrize(
    "missing_field",
    [
        "username",
        "password",
    ],
)
async def test_login_missing_fields(
    client: AsyncClient,
    missing_field: str,
) -> None:
    """Test login request with missing required fields."""
    payload = {
        "username": "user@example.com",
        "password": "string",
    }
    payload.pop(missing_field)
    response = await client.post("/api/auth/jwt/login", data=payload)
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    assert any(
        detail.get("loc") == ["body", missing_field]
        for detail in response.json()["detail"]
    )


@pytest.mark.anyio
async def test_login_with_changed_data(
    authorized_client: AsyncClient,
    dbsession: AsyncSession,
    mocker: Mock,
) -> None:
    """Testing to receive a token after changing fields in patch users/me."""
    user = await get_first_user_from_db(dbsession)
    response = await authorized_client.patch("/api/users/me", json=new_payload)
    assert response.status_code == 200
    response = await authorized_client.post(
        "/api/auth/jwt/login",
        data={
            "username": user.email,
            "password": new_payload["password"],
        },
    )
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {
        "access_token": mocker.ANY,
        "token_type": "bearer",
    }
