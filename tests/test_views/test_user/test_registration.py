import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

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
    user = await get_first_user_from_db(dbsession)
    assert response.status_code == status.HTTP_201_CREATED
    assert response.json() == {
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
    payload.pop(missing_field)
    response = await client.post("/api/auth/register", json=payload)
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    json_response = response.json()
    assert any(
        detail["loc"] == ["body", missing_field] and detail["type"] == "missing"
        for detail in json_response.get("detail", [])
    )
