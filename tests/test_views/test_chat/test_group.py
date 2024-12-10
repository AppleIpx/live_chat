import secrets
import uuid
from typing import AsyncGenerator, List

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from live_chat.web.api.read_status.utils import get_read_status_by_user_chat_ids
from tests.factories import ChatFactory, UserFactory
from tests.utils import get_first_chat_from_db, get_first_user_from_db


@pytest.mark.anyio
async def test_create_group_chat(
    authorized_client: AsyncClient,
    some_users: List[UserFactory],
    override_get_async_session: AsyncGenerator[AsyncSession, None],
    dbsession: AsyncSession,
) -> None:
    """Testing to create a group chat and users in it."""
    recipient_user_ids = [str(user.id) for user in some_users]
    response = await authorized_client.post(
        "/api/chats/create/group",
        json={
            "recipient_user_ids": recipient_user_ids,
            "name_group": "string",
            "image_group": None,
        },
    )
    chat = await get_first_chat_from_db(dbsession)
    sender = await get_first_user_from_db(dbsession)
    read_status = await get_read_status_by_user_chat_ids(
        chat_id=chat.id,
        user_id=sender.id,
        db_session=dbsession,
    )
    expected_users = [
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
        }
        for user in [sender, *some_users]
    ]

    assert response.status_code == status.HTTP_201_CREATED
    assert response.json() == {
        "id": str(chat.id),
        "chat_type": chat.chat_type.value,
        "created_at": chat.created_at.isoformat().replace("+00:00", "Z"),
        "updated_at": chat.updated_at.isoformat().replace("+00:00", "Z"),
        "users": expected_users,
        "image": chat.image,
        "name": chat.name,
        "read_statuses": {
            "id": str(read_status.id),
            "chat_id": str(read_status.chat_id),
            "count_unread_msg": read_status.count_unread_msg,
            "last_read_message_id": read_status.last_read_message_id,
            "user_id": str(read_status.user_id),
        },
    }


@pytest.mark.anyio
async def test_create_group_chat_with_failed_user(
    authorized_client: AsyncClient,
    some_users: List[UserFactory],
    override_get_async_session: AsyncGenerator[AsyncSession, None],
    dbsession: AsyncSession,
) -> None:
    """Test that handles an error with a non-existent user."""
    recipient_user_ids = [str(user.id) for user in some_users]
    random_recipients_id = uuid.uuid4()
    recipient_user_ids[secrets.randbelow(5)] = str(random_recipients_id)
    response = await authorized_client.post(
        "/api/chats/create/group",
        json={
            "recipient_user_ids": recipient_user_ids,
            "name_group": "string",
            "image_group": None,
        },
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {
        "detail": f"There is no recipient user with id [{random_recipients_id}]",
    }


@pytest.mark.anyio
async def test_create_group_chat_with_existing_user(
    authorized_client: AsyncClient,
    group_chat_with_users: ChatFactory,
    override_get_async_session: AsyncGenerator[AsyncSession, None],
) -> None:
    """Testing to create a group chat with existing user."""
    recipient_user_ids = [str(user.id) for user in group_chat_with_users.users]
    response = await authorized_client.post(
        "/api/chats/create/group",
        json={
            "recipient_user_ids": recipient_user_ids[1::],
            "name_group": "string",
            "image_group": None,
        },
    )
    assert response.status_code == status.HTTP_201_CREATED


@pytest.mark.anyio
async def test_create_group_chat_without_auth(
    client: AsyncClient,
    some_users: List[UserFactory],
) -> None:
    """Testing to create a group chat without auth."""
    recipient_user_ids = [str(user.id) for user in some_users]
    response = await client.post(
        "/api/chats/create/group",
        json={
            "recipient_user_ids": recipient_user_ids,
            "name_group": "string",
            "image_group": None,
        },
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.json() == {"detail": "Unauthorized"}
