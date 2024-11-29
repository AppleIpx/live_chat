import json
import uuid
from typing import AsyncGenerator
from unittest.mock import AsyncMock

import pytest
from fastapi.encoders import jsonable_encoder
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from live_chat.web.api.messages.constants import REDIS_CHANNEL_PREFIX
from tests.factories import MessageFactory, UserFactory


@pytest.mark.anyio
async def test_update_message(
    authorized_client: AsyncClient,
    message_in_chat: MessageFactory,
    override_get_async_session: AsyncGenerator[AsyncSession, None],
    mocked_publish_message: AsyncMock,
) -> None:
    """Test update message."""
    chat = message_in_chat.chat
    response = await authorized_client.patch(
        f"/api/chats/{chat.id}/messages/{message_in_chat.id}",
        json={"content": "test"},
    )
    target_channel = f"{REDIS_CHANNEL_PREFIX}:{chat.id!s}:{chat.users[1].id!s}"
    message_data = json.dumps(
        jsonable_encoder(
            {
                "id": message_in_chat.id,
                "user_id": message_in_chat.user.id,
                "chat_id": chat.id,
                "content": message_in_chat.content,
                "created_at": message_in_chat.created_at,
                "updated_at": message_in_chat.updated_at,
            },
        ),
    )

    mocked_publish_message.assert_called_with(
        json.dumps({"event": "update_message", "data": message_data}),
        channel=target_channel,
    )
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {
        "id": str(message_in_chat.id),
        "user_id": str(message_in_chat.user.id),
        "chat_id": str(chat.id),
        "content": message_in_chat.content,
        "created_at": message_in_chat.created_at.isoformat().replace("+00:00", "Z"),
        "updated_at": message_in_chat.updated_at.isoformat().replace("+00:00", "Z"),
    }


@pytest.mark.anyio
async def test_update_message_with_fail_chat(
    authorized_client: AsyncClient,
    message_in_chat: MessageFactory,
    override_get_async_session: AsyncGenerator[AsyncSession, None],
) -> None:
    """Test message update test with non-existent chat."""
    response = await authorized_client.patch(
        f"/api/chats/{uuid.uuid4()}/messages/{message_in_chat.id}",
        json={"content": "test"},
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {"detail": "Chat not found"}


@pytest.mark.anyio
async def test_update_message_with_fail_message(
    authorized_client: AsyncClient,
    message_in_chat: MessageFactory,
    override_get_async_session: AsyncGenerator[AsyncSession, None],
) -> None:
    """Test message update test with non-existent message."""
    response = await authorized_client.patch(
        f"/api/chats/{message_in_chat.chat.id}/messages/{uuid.uuid4()}",
        json={"content": "test"},
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {"detail": "Message not found"}


@pytest.mark.anyio
async def test_update_message_for_non_member(
    authorized_client: AsyncClient,
    message_in_chat: MessageFactory,
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
    override_get_async_session: AsyncGenerator[AsyncSession, None],
    dbsession: AsyncSession,
) -> None:
    """Test for update a message by a user who is not a author message."""
    message_in_chat.user = user
    response = await authorized_client.patch(
        f"/api/chats/{message_in_chat.chat.id}/messages/{message_in_chat.id}",
        json={"content": "test"},
    )
    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert response.json() == {"detail": "User is not the author of this message"}
