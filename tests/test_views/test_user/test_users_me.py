import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from tests.factories import UserFactory
from tests.utils import get_first_user_from_db, new_payload


@pytest.mark.anyio
async def test_get_users_me(
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
        "last_online": (
            user.last_online.isoformat().replace("+00:00", "Z")
            if user.last_online
            else None
        ),
        "username": user.username,
        "user_image": user.user_image,
    }


@pytest.mark.anyio
async def test_patch_users_me_correct(
    authorized_client: AsyncClient,
    dbsession: AsyncSession,
) -> None:
    """Test patch users me."""
    user = await get_first_user_from_db(dbsession)
    response = await authorized_client.patch("/api/users/me", json=new_payload)
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {
        "id": str(user.id),
        "email": user.email,
        "is_active": user.is_active,
        "is_superuser": user.is_superuser,
        "is_verified": user.is_verified,
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


@pytest.mark.anyio
async def test_patch_users_me_existing_email(
    authorized_client: AsyncClient,
    user: UserFactory,
) -> None:
    """Test patch users me with existing email."""
    response = await authorized_client.patch(
        "/api/users/me",
        json={"email": user.email},
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json() == {"detail": "UPDATE_USER_EMAIL_ALREADY_EXISTS"}


@pytest.mark.anyio
async def test_patch_users_me_existing_username(
    authorized_client: AsyncClient,
    user: UserFactory,
    dbsession: AsyncSession,
) -> None:
    """Test patch users me with existing username."""
    response = await authorized_client.patch(
        "/api/users/me",
        json={"username": user.username},
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json() == {"detail": "UPDATE_USERNAME_ALREADY_EXISTS"}


@pytest.mark.anyio
@pytest.mark.parametrize(
    "invalid_password, expected_error",
    [
        ("short", "Password must be at least 8 characters long."),
        ("password", "Password must include at least one digit."),
        ("12345678", "Password must include at least one letter."),
        ("password123", "Password must include at least one special character."),
        ("user1@example.com", "Password should not be similar to email."),
        ("username123!", "Password should not be similar to username."),
    ],
)
async def test_patch_users_me_invalid_password(
    authorized_client: AsyncClient,
    dbsession: AsyncSession,
    invalid_password: str,
    expected_error: str,
) -> None:
    """Test patch users me with invalid password."""
    response = await authorized_client.patch(
        "/api/users/me",
        json={"password": invalid_password},
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json() == {
        "detail": {
            "code": "UPDATE_USER_INVALID_PASSWORD",
            "reason": expected_error,
        },
    }


@pytest.mark.anyio
async def test_patch_users_me_unauthorized_user(
    client: AsyncClient,
) -> None:
    """Test patch users me without authentication."""
    response = await client.patch("/api/users/me", json=new_payload)
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.json() == {"detail": "Unauthorized"}
