import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from tests.utils import get_first_user_from_db, payload


@pytest.mark.anyio
async def test_registration_user(
    client: AsyncClient,
    dbsession: AsyncSession,
) -> None:
    """Test registration and check user's fields."""
    response = await client.post("/api/auth/register", json=payload)
    user = await get_first_user_from_db(dbsession)
    assert response.status_code == status.HTTP_201_CREATED
    assert response.json() == {
        "id": str(user.id),
        "is_deleted": user.is_deleted,
        "is_banned": user.is_banned,
        "ban_reason": None,
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
        "is_warning": user.is_warning,
        "username": user.username,
        "user_image": user.user_image,
    }


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
async def test_registration_user_invalid_password(
    client: AsyncClient,
    dbsession: AsyncSession,
    invalid_password: str,
    expected_error: str,
) -> None:
    """Test registration user with invalid password."""
    payload["password"] = invalid_password
    response = await client.post("/api/auth/register", json=payload)
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json() == {
        "detail": {
            "code": "REGISTER_INVALID_PASSWORD",
            "reason": expected_error,
        },
    }


@pytest.mark.anyio
@pytest.mark.parametrize(
    "missing_field",
    ["email", "password", "first_name", "last_name", "username", "user_image"],
)
async def test_register_missing_fields(
    client: AsyncClient,
    dbsession: AsyncSession,
    missing_field: str,
) -> None:
    """Test registration with missing required fields."""
    new_payload = {
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
    new_payload.pop(missing_field)
    response = await client.post("/api/auth/register", json=new_payload)
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    json_response = response.json()
    assert any(
        detail["loc"] == ["body", missing_field] and detail["type"] == "missing"
        for detail in json_response.get("detail", [])
    )
