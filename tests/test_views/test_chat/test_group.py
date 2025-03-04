import secrets
import uuid
from typing import AsyncGenerator, List

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from live_chat.web.api.messages.utils import (
    get_draft_message_by_chat_and_user_ids,
)
from live_chat.web.api.read_status.utils.get_read_status_by_id import (
    get_read_statuses_by_chat_id,
)
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
    read_statuses = await get_read_statuses_by_chat_id(
        chat_id=chat.id,
        db_session=dbsession,
    )
    draft_message = await get_draft_message_by_chat_and_user_ids(
        db_session=dbsession,
        chat_id=chat.id,
        user_id=sender.id,
    )
    expected_users = [
        {
            "id": str(user.id),
            "is_deleted": user.is_deleted,
            "is_banned": user.is_banned,
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
        for user in [sender, *some_users]
    ]
    expected_read_statuses = [
        {
            "id": str(read_status.id),
            "last_read_message_id": read_status.last_read_message_id,
            "user_id": str(read_status.user_id),
            "chat_id": str(read_status.chat_id),
            "count_unread_msg": read_status.count_unread_msg,
        }
        for read_status in read_statuses
    ]

    assert response.status_code == status.HTTP_201_CREATED
    assert response.json() == {
        "id": str(chat.id),
        "chat_type": chat.chat_type.value,
        "created_at": chat.created_at.isoformat().replace("+00:00", "Z"),
        "updated_at": chat.updated_at.isoformat().replace("+00:00", "Z"),
        "draft_message": draft_message.content if draft_message else None,
        "users": expected_users,
        "image": chat.image,
        "last_message_content": None,
        "name": chat.name,
        "read_statuses": expected_read_statuses,
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


@pytest.mark.anyio
async def test_create_group_chat_with_deleted_user(
    authorized_client: AsyncClient,
    some_users: List[UserFactory],
    override_get_async_session: AsyncGenerator[AsyncSession, None],
    dbsession: AsyncSession,
) -> None:
    """Testing to create a group chat with deleted user."""
    deleted_user = secrets.choice(some_users)
    deleted_user.is_deleted = True
    recipient_user_ids = [str(user.id) for user in some_users]
    response = await authorized_client.post(
        "/api/chats/create/group",
        json={
            "recipient_user_ids": recipient_user_ids,
            "name_group": "string",
            "image_group": None,
        },
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json() == {"detail": "This user has been deleted."}


@pytest.mark.anyio
async def test_create_group_chat_by_deleted_user(
    authorized_deleted_client: AsyncClient,
    some_users: List[UserFactory],
    override_get_async_session: AsyncGenerator[AsyncSession, None],
    dbsession: AsyncSession,
) -> None:
    """Testing to create_group_chat by a deleted user."""
    recipient_user_ids = [str(user.id) for user in some_users]
    response = await authorized_deleted_client.post(
        "/api/chats/create/group",
        json={
            "recipient_user_ids": recipient_user_ids,
            "name_group": "string",
            "image_group": None,
        },
    )

    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert response.json() == {"detail": "You are deleted."}


@pytest.mark.anyio
async def test_create_group_chat_with_banned_user(
    authorized_client: AsyncClient,
    some_users: List[UserFactory],
    override_get_async_session: AsyncGenerator[AsyncSession, None],
    dbsession: AsyncSession,
) -> None:
    """Testing to create a group chat with banned user."""
    banned_user = secrets.choice(some_users)
    banned_user.is_banned = True
    recipient_user_ids = [str(user.id) for user in some_users]
    response = await authorized_client.post(
        "/api/chats/create/group",
        json={
            "recipient_user_ids": recipient_user_ids,
            "name_group": "string",
            "image_group": None,
        },
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json() == {"detail": "This user has been banned."}


@pytest.mark.anyio
async def test_create_group_chat_by_banned_user(
    authorized_banned_client: AsyncClient,
    some_users: List[UserFactory],
    override_get_async_session: AsyncGenerator[AsyncSession, None],
    dbsession: AsyncSession,
) -> None:
    """Testing to create_group_chat by a banned user."""
    recipient_user_ids = [str(user.id) for user in some_users]
    response = await authorized_banned_client.post(
        "/api/chats/create/group",
        json={
            "recipient_user_ids": recipient_user_ids,
            "name_group": "string",
            "image_group": None,
        },
    )

    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert response.json() == {
        "detail": {
            "reason": None,
            "status": "banned",
        },
    }
