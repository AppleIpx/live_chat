import uuid
from typing import AsyncGenerator

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from live_chat.web.api.read_status.utils import get_read_status_by_user_chat_ids
from tests.factories import ChatFactory, MessageFactory, UserFactory
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
        "/api/chats/create/direct",
        json={"recipient_user_id": f"{user.id}"},
    )
    chat = await get_first_chat_from_db(dbsession)
    sender = await get_first_user_from_db(dbsession)
    read_status_sender = await get_read_status_by_user_chat_ids(
        chat_id=chat.id,
        user_id=sender.id,
        db_session=dbsession,
    )
    read_status_recipient = await get_read_status_by_user_chat_ids(
        chat_id=chat.id,
        user_id=user.id,
        db_session=dbsession,
    )
    assert response.status_code == status.HTTP_201_CREATED
    assert response.json() == {
        "id": str(chat.id),
        "chat_type": chat.chat_type.value,
        "image": chat.image,
        "last_message_content": None,
        "name": chat.name,
        "created_at": chat.created_at.isoformat().replace("+00:00", "Z"),
        "updated_at": chat.updated_at.isoformat().replace("+00:00", "Z"),
        "users": [
            {
                "id": str(sender.id),
                "is_deleted": sender.is_deleted,
                "first_name": sender.first_name,
                "last_name": sender.last_name,
                "last_online": (
                    sender.last_online.isoformat().replace("+00:00", "Z")
                    if sender.last_online
                    else None
                ),
                "username": sender.username,
                "user_image": sender.user_image,
            },
            {
                "id": str(user.id),
                "is_deleted": user.is_deleted,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "last_online": user.last_online.isoformat().replace("+00:00", "Z"),
                "username": user.username,
                "user_image": user.user_image,
            },
        ],
        "read_statuses": [
            {
                "id": str(read_status_sender.id),
                "chat_id": str(read_status_sender.chat_id),
                "count_unread_msg": read_status_sender.count_unread_msg,
                "last_read_message_id": read_status_sender.last_read_message_id,
                "user_id": str(read_status_sender.user_id),
            },
            {
                "id": str(read_status_recipient.id),
                "chat_id": str(read_status_recipient.chat_id),
                "count_unread_msg": read_status_recipient.count_unread_msg,
                "last_read_message_id": read_status_recipient.last_read_message_id,
                "user_id": str(read_status_recipient.user_id),
            },
        ],
    }


@pytest.mark.anyio
async def test_create_direct_chat_with_failed_user(
    authorized_client: AsyncClient,
    override_get_async_session: AsyncGenerator[AsyncSession, None],
) -> None:
    """Test that handles an error with a non-existent user."""
    random_recipients_id = uuid.uuid4()
    response = await authorized_client.post(
        "/api/chats/create/direct",
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
        "/api/chats/create/direct",
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
        "/api/chats/create/direct",
        json={"recipient_user_id": f"{user.id}"},
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.json() == {"detail": "Unauthorized"}


@pytest.mark.anyio
async def test_create_direct_chat_with_deleted_user(
    authorized_client: AsyncClient,
    user: UserFactory,
    override_get_async_session: AsyncGenerator[AsyncSession, None],
    dbsession: AsyncSession,
) -> None:
    """Test create direct chat with deleted user."""
    user.is_deleted = True
    response = await authorized_client.post(
        "/api/chats/create/direct",
        json={"recipient_user_id": f"{user.id}"},
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json() == {"detail": "This user has been deleted."}


@pytest.mark.anyio
async def test_get_detail_chat_by_deleted_user(
    authorized_deleted_client: AsyncClient,
    message_in_chat: MessageFactory,
    dbsession: AsyncSession,
) -> None:
    """Testing to get detail chat by a deleted user."""
    chat_id = message_in_chat.chat.id
    response = await authorized_deleted_client.get(f"api/chats/{chat_id}")

    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert response.json() == {"detail": "You are deleted."}
