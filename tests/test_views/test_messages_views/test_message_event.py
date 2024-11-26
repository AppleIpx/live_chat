import asyncio
import uuid
from typing import AsyncGenerator
from unittest.mock import patch

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from live_chat.web.api.messages.utils import message_generator
from tests.factories import ChatFactory, MessageFactory


@pytest.mark.anyio
async def test_get_message_event(
    authorized_client: AsyncClient,
    direct_chat_with_users: ChatFactory,
    message: MessageFactory,
    override_get_async_session: AsyncGenerator[AsyncSession, None],
    dbsession: AsyncSession,
) -> None:
    """Testing get message event."""
    chat_id = direct_chat_with_users.id
    access_token = authorized_client.headers.get("Authorization").split(" ")[1]
    message_data = {
        "event": "new_message",
        "data": {
            "message_id": f"{message.id}",
            "user_id": f"{direct_chat_with_users.users[0].id}",
            "chat_id": f"{chat_id}",
            "content": "Test message",
            "created_at": message.created_at.isoformat(),
        },
    }

    with patch(
        "live_chat.web.api.messages.views.message_generator",
        return_value=iter([message_data]),
    ):
        async with authorized_client.stream(
            "GET",
            f"/api/chats/{chat_id}/events/?token={access_token}",
        ) as response:
            data = await response.aread()

            assert response.status_code == status.HTTP_200_OK
            assert "text/event-stream" in response.headers["content-type"]
            assert data.decode() == (
                f"event: {message_data["event"]}\r\n"
                f"data: {message_data["data"]}\r\n\r\n"
            )


@pytest.mark.anyio
async def test_message_generator() -> None:
    """Testing message generator get data from redis."""
    with patch(
        "live_chat.web.api.messages.utils.sse_generators.redis.lpop",
        return_value=asyncio.Future(),
    ) as mock_redis:
        mock_redis.return_value.set_result("Test message")

        async for event in message_generator("test_key"):
            assert event["event"] == "new_message"
            assert event["data"] == "Test message"
            break


@pytest.mark.anyio
async def test_get_message_event_bad_token(
    authorized_client: AsyncClient,
    direct_chat_with_users: ChatFactory,
    message: MessageFactory,
    override_get_async_session: AsyncGenerator[AsyncSession, None],
    dbsession: AsyncSession,
) -> None:
    """Testing get message event."""
    chat_id = direct_chat_with_users.id
    message_data = {
        "event": "new_message",
        "data": {
            "message_id": f"{message.id}",
            "user_id": f"{direct_chat_with_users.users[0].id}",
            "chat_id": f"{chat_id}",
            "content": "Test message",
            "created_at": message.created_at.isoformat(),
        },
    }

    with patch(
        "live_chat.web.api.messages.views.message_generator",
        return_value=iter([message_data]),
    ):
        async with authorized_client.stream(
            "GET",
            f"/api/chats/{chat_id}/events/?token=invalid token",
        ) as response:
            assert response.status_code == status.HTTP_401_UNAUTHORIZED
            assert (
                await response.aread() == b"""{"detail":"Invalid or expired token."}"""
            )


@pytest.mark.anyio
async def test_get_message_event_nonexistent_user_in_chat(
    authorized_client: AsyncClient,
    chat: ChatFactory,
    message: MessageFactory,
    override_get_async_session: AsyncGenerator[AsyncSession, None],
    dbsession: AsyncSession,
) -> None:
    """Testing get message event."""
    access_token = authorized_client.headers.get("Authorization").split(" ")[1]
    message_data = {
        "event": "new_message",
        "data": {
            "message_id": f"{message.id}",
            "user_id": f"{uuid.uuid4()}",
            "chat_id": f"{chat.id}",
            "content": "Test message",
            "created_at": message.created_at.isoformat(),
        },
    }

    with patch(
        "live_chat.web.api.messages.views.message_generator",
        return_value=iter([message_data]),
    ):
        async with authorized_client.stream(
            "GET",
            f"/api/chats/{chat.id}/events/?token={access_token}",
        ) as response:
            assert response.status_code == status.HTTP_403_FORBIDDEN
            assert (
                await response.aread()
                == b"""{"detail":"User is not part of the chat"}"""
            )


@pytest.mark.anyio
async def test_get_message_event_nonexistent_chat(
    authorized_client: AsyncClient,
    message: MessageFactory,
    override_get_async_session: AsyncGenerator[AsyncSession, None],
    dbsession: AsyncSession,
) -> None:
    """Testing get message event."""
    access_token = authorized_client.headers.get("Authorization").split(" ")[1]
    message_data = {
        "event": "new_message",
        "data": {
            "message_id": f"{message.id}",
            "user_id": f"{uuid.uuid4()}",
            "chat_id": f"{uuid.uuid4()}",
            "content": "Test message",
            "created_at": message.created_at.isoformat(),
        },
    }

    with patch(
        "live_chat.web.api.messages.views.message_generator",
        return_value=iter([message_data]),
    ):
        async with authorized_client.stream(
            "GET",
            f"/api/chats/{uuid.uuid4()}/events/?token={access_token}",
        ) as response:
            assert response.status_code == status.HTTP_404_NOT_FOUND
            assert await response.aread() == b"""{"detail":"Chat not found"}"""
