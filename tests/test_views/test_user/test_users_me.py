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
        "username": user.username,
        "user_image": user.user_image,
    }


@pytest.mark.anyio
async def test_patch_users_me_400(
    authorized_client: AsyncClient,
    user: UserFactory,
) -> None:
    """Test patch with exists email."""
    new_data = {
        "email": f"{user.email}",
        "password": "new_string",
        "is_active": True,
        "is_superuser": True,
        "is_verified": True,
        "first_name": "new_string",
        "last_name": "new_string",
        "username": "string",
        "user_image": None,
    }
    response = await authorized_client.patch("/api/users/me", json=new_data)
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json() == {"detail": "UPDATE_USER_EMAIL_ALREADY_EXISTS"}


# TODO нужно будет доделать после обновления ручки patch(/api/users/me)
# TODO не обновляются is_active, username
@pytest.mark.anyio
async def test_patch_users_me_200(
    authorized_client: AsyncClient,
    dbsession: AsyncSession,
) -> None:
    """Test patch users me."""
    user = await get_first_user_from_db(dbsession)
    response = await authorized_client.patch("/api/users/me", json=new_payload)
    assert response.status_code == 200
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
async def test_patch_users_me_401(
    client: AsyncClient,
) -> None:
    """Test patch users me without authentication."""
    response = await client.patch("/api/users/me", json=new_payload)
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.json() == {"detail": "Unauthorized"}
