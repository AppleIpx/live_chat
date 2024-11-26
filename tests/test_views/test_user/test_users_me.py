import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from tests.utils import get_first_user_from_db


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
