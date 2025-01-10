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
from tests.factories import ChatFactory


@pytest.mark.anyio
@pytest.mark.parametrize("is_typing", [True, False])
async def test_post_typing_status(
    authorized_client: AsyncClient,
    direct_chat_with_users: ChatFactory,
    override_get_async_session: AsyncGenerator[AsyncSession, None],
    dbsession: AsyncSession,
    mocked_publish_message: AsyncMock,
    is_typing: bool,
) -> None:
    """Testing post user typing status."""
    chat_id = direct_chat_with_users.id
    sender = direct_chat_with_users.users[0]
    recipient = direct_chat_with_users.users[1]
    target_channel = f"{REDIS_CHANNEL_PREFIX}:{chat_id!s}:{recipient.id!s}"
    response = await authorized_client.post(
        f"/api/chats/{chat_id}/typing-status?is_typing={is_typing}",
    )
    event_data = jsonable_encoder(
        {
            "user_id": f"{sender.id!s}",
            "username": f"{sender.username!s}",
            "is_typing": is_typing,
        },
    )
    mocked_publish_message.assert_called_with(
        json.dumps({"event": "user_typing", "data": json.dumps(event_data)}),
        channel=target_channel,
    )
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {"detail": "User typing event send"}


@pytest.mark.anyio
async def test_post_typing_status_unauthorized_user(
    client: AsyncClient,
    direct_chat_with_users: ChatFactory,
    override_get_async_session: AsyncGenerator[AsyncSession, None],
    dbsession: AsyncSession,
    mocked_publish_message: AsyncMock,
) -> None:
    """Testing post typing status from unauthorized user."""
    chat_id = direct_chat_with_users.id
    response = await client.post(f"/api/chats/{chat_id}/typing-status?is_typing=True")

    mocked_publish_message.assert_not_called()
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.json() == {"detail": "Unauthorized"}


@pytest.mark.anyio
async def test_post_typing_status_nonexistent_user(
    authorized_client: AsyncClient,
    chat: ChatFactory,
    override_get_async_session: AsyncGenerator[AsyncSession, None],
    dbsession: AsyncSession,
    mocked_publish_message: AsyncMock,
) -> None:
    """Testing post typing status from nonexistent user in chat."""
    response = await authorized_client.post(
        f"/api/chats/{chat.id}/typing-status?is_typing=True",
    )

    mocked_publish_message.assert_not_called()
    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert response.json() == {"detail": "User is not part of the chat"}


@pytest.mark.anyio
async def test_post_typing_status_nonexistent_chat(
    authorized_client: AsyncClient,
    override_get_async_session: AsyncGenerator[AsyncSession, None],
    dbsession: AsyncSession,
    mocked_publish_message: AsyncMock,
) -> None:
    """Testing post typing status in nonexistent chat."""
    response = await authorized_client.post(
        f"/api/chats/{uuid.uuid4()}/typing-status?is_typing=True",
    )

    mocked_publish_message.assert_not_called()
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {"detail": "Chat not found"}


@pytest.mark.anyio
@pytest.mark.parametrize("is_typing", [True, False])
async def test_post_typing_status_by_deleted_user(
    authorized_deleted_client: AsyncClient,
    direct_chat_with_users: ChatFactory,
    override_get_async_session: AsyncGenerator[AsyncSession, None],
    dbsession: AsyncSession,
    mocked_publish_message: AsyncMock,
    is_typing: bool,
) -> None:
    """Testing to post typing status by a deleted user."""
    chat_id = direct_chat_with_users.id
    response = await authorized_deleted_client.post(
        f"/api/chats/{chat_id}/typing-status?is_typing={is_typing}",
    )
    mocked_publish_message.assert_not_called()
    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert response.json() == {"detail": "You are deleted."}


@pytest.mark.anyio
@pytest.mark.parametrize("is_typing", [True, False])
async def test_post_typing_status_by_banned_user(
    authorized_banned_client: AsyncClient,
    direct_chat_with_users: ChatFactory,
    override_get_async_session: AsyncGenerator[AsyncSession, None],
    dbsession: AsyncSession,
    mocked_publish_message: AsyncMock,
    is_typing: bool,
) -> None:
    """Testing to post typing status by a banned user."""
    chat_id = direct_chat_with_users.id
    response = await authorized_banned_client.post(
        f"/api/chats/{chat_id}/typing-status?is_typing={is_typing}",
    )
    mocked_publish_message.assert_not_called()
    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert response.json() == {
        "detail": {
            "reason": None,
            "status": "banned",
        },
    }
