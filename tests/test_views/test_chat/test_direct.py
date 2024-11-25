import uuid
from typing import AsyncGenerator

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from tests.factories import ChatFactory, UserFactory
from tests.utils import get_first_chat_from_db, get_first_user_from_db


@pytest.mark.anyio
async def test_create_direct_chat(
    authorized_client: AsyncClient,
    user: UserFactory,
    override_get_async_session: AsyncGenerator[AsyncSession, None],
    dbsession: AsyncSession,
) -> None:
    """Test create and check user's direct chat."""
    response = await authorized_client.post(
        "/api/chats/create/direct/",
        json={"recipient_user_id": f"{user.id}"},
    )
    chat = await get_first_chat_from_db(dbsession)
    sender = await get_first_user_from_db(dbsession)
    assert response.status_code == status.HTTP_201_CREATED
    assert response.json() == {
        "id": str(chat.id),
        "chat_type": chat.chat_type.value,
        "created_at": chat.created_at.isoformat().replace("+00:00", "Z"),
        "updated_at": chat.updated_at.isoformat().replace("+00:00", "Z"),
        "users": [
            {
                "id": str(sender.id),
                "email": sender.email,
                "is_active": sender.is_active,
                "is_superuser": sender.is_superuser,
                "is_verified": sender.is_verified,
                "first_name": sender.first_name,
                "last_name": sender.last_name,
                "username": sender.username,
                "user_image": sender.user_image,
            },
            {
                "id": str(user.id),
                "email": user.email,
                "is_active": user.is_active,
                "is_superuser": user.is_superuser,
                "is_verified": user.is_verified,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "username": user.username,
                "user_image": user.user_image,
            },
        ],
        "last_message_content": None,
    }


@pytest.mark.anyio
async def test_create_direct_chat_with_failed_user(
    authorized_client: AsyncClient,
    override_get_async_session: AsyncGenerator[AsyncSession, None],
) -> None:
    """Test that handles an error with a non-existent user."""
    random_recipients_id = uuid.uuid4()
    response = await authorized_client.post(
        "/api/chats/create/direct/",
        json={"recipient_user_id": f"{random_recipients_id}"},
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {
        "detail": f"There is no recipient user with id [{random_recipients_id}]",
    }


@pytest.mark.anyio
async def test_create_direct_chat_with_existing_user(
    authorized_client: AsyncClient,
    direct_chat_with_users: ChatFactory,
    override_get_async_session: AsyncGenerator[AsyncSession, None],
    dbsession: AsyncSession,
) -> None:
    """Test create direct chat with existing user."""
    recipients_id = direct_chat_with_users.users[1].id
    response = await authorized_client.post(
        "/api/chats/create/direct/",
        json={"recipient_user_id": f"{recipients_id}"},
    )
    assert response.status_code == status.HTTP_409_CONFLICT
    assert response.json() == {
        "detail": f"Chat with recipient user exists [{recipients_id}]",
    }


@pytest.mark.anyio
async def test_create_direct_chat_without_auth(
    client: AsyncClient,
    user: UserFactory,
) -> None:
    """Testing to create a direct chat without auth."""
    response = await client.post(
        "/api/chats/create/direct/",
        json={"recipient_user_id": f"{user.id}"},
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.json() == {"detail": "Unauthorized"}
