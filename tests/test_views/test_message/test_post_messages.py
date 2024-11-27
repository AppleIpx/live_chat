import json
import uuid
from typing import AsyncGenerator
from unittest.mock import AsyncMock

import pytest
from fastapi.encoders import jsonable_encoder
from httpx import AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from live_chat.db.models.chat import Message
from live_chat.web.api.messages.constants import REDIS_CHANNEL_PREFIX
from tests.factories import ChatFactory


@pytest.mark.anyio
async def test_post_message(
    authorized_client: AsyncClient,
    direct_chat_with_users: ChatFactory,
    override_get_async_session: AsyncGenerator[AsyncSession, None],
    dbsession: AsyncSession,
    mocked_publish_message: AsyncMock,
) -> None:
    """Testing post message."""
    chat_id = direct_chat_with_users.id
    recipient = direct_chat_with_users.users[1]
    sender = direct_chat_with_users.users[0]
    target_channel = f"{REDIS_CHANNEL_PREFIX}:{chat_id!s}:{recipient.id!s}"
    response = await authorized_client.post(
        f"/api/chats/{chat_id}/messages",
        json={"content": "test"},
    )
    query = select(Message).where(Message.chat_id == chat_id)
    message = (await dbsession.execute(query)).scalar_one_or_none()
    message_data = json.dumps(
        jsonable_encoder(
            {
                "id": message.id,
                "user_id": sender.id,
                "chat_id": chat_id,
                "content": "test",
                "created_at": message.created_at,
            },
        ),
    )

    mocked_publish_message.assert_called_with(message_data, channel=target_channel)
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {"status": "Message published"}


@pytest.mark.anyio
async def test_post_message_unauthorized_user(
    client: AsyncClient,
    direct_chat_with_users: ChatFactory,
    override_get_async_session: AsyncGenerator[AsyncSession, None],
    dbsession: AsyncSession,
    mocked_publish_message: AsyncMock,
) -> None:
    """Testing post message from unauthorized user."""
    chat_id = direct_chat_with_users.id
    response = await client.post(
        f"/api/chats/{chat_id}/messages",
        json={"content": "test"},
    )

    mocked_publish_message.assert_not_called()
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.json() == {"detail": "Unauthorized"}


@pytest.mark.anyio
async def test_post_message_nonexistent_user(
    authorized_client: AsyncClient,
    chat: ChatFactory,
    override_get_async_session: AsyncGenerator[AsyncSession, None],
    dbsession: AsyncSession,
    mocked_publish_message: AsyncMock,
) -> None:
    """Testing post message from nonexistent user in chat."""
    response = await authorized_client.post(
        f"/api/chats/{chat.id}/messages",
        json={"content": "test"},
    )

    mocked_publish_message.assert_not_called()
    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert response.json() == {"detail": "User is not part of the chat"}


@pytest.mark.anyio
async def test_post_message_nonexistent_chat(
    authorized_client: AsyncClient,
    override_get_async_session: AsyncGenerator[AsyncSession, None],
    dbsession: AsyncSession,
    mocked_publish_message: AsyncMock,
) -> None:
    """Testing post message in nonexistent chat."""
    response = await authorized_client.post(
        f"/api/chats/{uuid.uuid4()}/messages",
        json={"content": "test"},
    )

    mocked_publish_message.assert_not_called()
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {"detail": "Chat not found"}
