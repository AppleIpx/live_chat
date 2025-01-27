import json
import uuid
from typing import AsyncGenerator
from unittest.mock import AsyncMock

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from live_chat.web.api.messages.constants import REDIS_CHANNEL_PREFIX
from live_chat.web.api.messages.utils import get_message_by_id
from tests.factories import ChatFactory, MessageFactory, UserFactory
from tests.utils import transformation_message_data


@pytest.mark.anyio
async def test_update_message(
    authorized_client: AsyncClient,
    message_in_chat: MessageFactory,
    dbsession: AsyncSession,
    mocked_publish_message: AsyncMock,
    override_get_async_session: AsyncGenerator[AsyncSession, None],
) -> None:
    """Test update message."""
    created_chat = message_in_chat.chat
    response = await authorized_client.patch(
        f"/api/chats/{created_chat.id}/messages/{message_in_chat.id}",
        json={"content": "test"},
    )
    target_channel = (
        f"{REDIS_CHANNEL_PREFIX}:{created_chat.id!s}:{created_chat.users[1].id!s}"
    )
    message_data = await transformation_message_data(message_in_chat)

    mocked_publish_message.assert_called_with(
        json.dumps({"event": "update_message", "data": message_data}),
        channel=target_channel,
    )
    updated_message = await get_message_by_id(
        db_session=dbsession,
        message_id=message_in_chat.id,
    )

    assert created_chat.last_message_content == "test"
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {
        "id": str(updated_message.id),
        "user_id": str(updated_message.user.id),
        "chat_id": str(created_chat.id),
        "message_type": updated_message.message_type.value,
        "content": updated_message.content,
        "file_name": updated_message.file_name,
        "file_path": updated_message.file_path,
        "parent_message_id": updated_message.parent_message_id,
        "created_at": updated_message.created_at.isoformat().replace("+00:00", "Z"),
        "updated_at": updated_message.updated_at.isoformat().replace("+00:00", "Z"),
        "is_deleted": updated_message.is_deleted,
        "reactions": [],
    }


@pytest.mark.anyio
async def test_update_message_with_fail_chat(
    authorized_client: AsyncClient,
    message: MessageFactory,
    dbsession: AsyncSession,
) -> None:
    """Test message update test with non-existent chat."""
    response = await authorized_client.patch(
        f"/api/chats/{uuid.uuid4()}/messages/{message.id}",
        json={"content": "test"},
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {"detail": "Chat not found"}


@pytest.mark.anyio
async def test_update_message_with_fail_message(
    authorized_client: AsyncClient,
    any_chat_with_users: ChatFactory,
    dbsession: AsyncSession,
    override_get_async_session: AsyncGenerator[AsyncSession, None],
) -> None:
    """Test message update test with non-existent message."""
    response = await authorized_client.patch(
        f"/api/chats/{any_chat_with_users.id}/messages/{uuid.uuid4()}",
        json={"content": "test"},
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {"detail": "Message not found"}


@pytest.mark.anyio
async def test_update_message_for_non_member(
    authorized_client: AsyncClient,
    message_in_chat: MessageFactory,
    dbsession: AsyncSession,
    override_get_async_session: AsyncGenerator[AsyncSession, None],
) -> None:
    """Test for updating a message by a user who is not a member of the group."""
    del message_in_chat.chat.users[0]
    response = await authorized_client.patch(
        f"/api/chats/{message_in_chat.chat.id}/messages/{message_in_chat.id}",
        json={"content": "test"},
    )
    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert response.json() == {"detail": "User is not part of the chat"}


@pytest.mark.anyio
async def test_update_message_with_non_author(
    authorized_client: AsyncClient,
    user: UserFactory,
    message_in_chat: MessageFactory,
    dbsession: AsyncSession,
    override_get_async_session: AsyncGenerator[AsyncSession, None],
) -> None:
    """Test for update a message by a user who is not a author message."""
    message_in_chat.user = user
    response = await authorized_client.patch(
        f"/api/chats/{message_in_chat.chat.id}/messages/{message_in_chat.id}",
        json={"content": "test"},
    )
    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert response.json() == {"detail": "User is not the author of this message"}


@pytest.mark.anyio
async def test_update_message_by_deleted_user(
    authorized_deleted_client: AsyncClient,
    message_in_chat: MessageFactory,
    dbsession: AsyncSession,
    override_get_async_session: AsyncGenerator[AsyncSession, None],
) -> None:
    """Testing to update message by a deleted user."""
    chat = message_in_chat.chat
    response = await authorized_deleted_client.patch(
        f"/api/chats/{chat.id}/messages/{message_in_chat.id}",
        json={"content": "test"},
    )
    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert response.json() == {"detail": "You are deleted."}


@pytest.mark.anyio
async def test_update_message_by_banned_user(
    authorized_banned_client: AsyncClient,
    message_in_chat: MessageFactory,
    dbsession: AsyncSession,
    override_get_async_session: AsyncGenerator[AsyncSession, None],
) -> None:
    """Testing to update message by a banned user."""
    chat = message_in_chat.chat
    response = await authorized_banned_client.patch(
        f"/api/chats/{chat.id}/messages/{message_in_chat.id}",
        json={"content": "test"},
    )
    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert response.json() == {
        "detail": {
            "reason": None,
            "status": "banned",
        },
    }
