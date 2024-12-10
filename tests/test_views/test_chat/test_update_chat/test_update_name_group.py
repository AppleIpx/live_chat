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
async def test_update_name_group(
    authorized_client: AsyncClient,
    group_chat_with_users: ChatFactory,
    override_get_async_session: AsyncGenerator[AsyncSession, None],
    mocked_publish_message: AsyncMock,
    dbsession: AsyncSession,
) -> None:
    """Testing update name group."""
    chat_id = group_chat_with_users.id
    recipient = group_chat_with_users.users[-1]
    target_channel = f"{REDIS_CHANNEL_PREFIX}:{chat_id!s}:{recipient.id!s}"
    response = await authorized_client.patch(
        f"/api/chats/{chat_id}",
        json={"name_group": "New name"},
    )
    event_data = jsonable_encoder({"group_name": "New name"})

    mocked_publish_message.assert_called_with(
        json.dumps({"event": "update_group_name", "data": json.dumps(event_data)}),
        channel=target_channel,
    )
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == "Chat name updated"
    assert group_chat_with_users.name == "New name"


@pytest.mark.anyio
async def test_update_name_group_unauthorized_user(
    client: AsyncClient,
    group_chat_with_users: ChatFactory,
    override_get_async_session: AsyncGenerator[AsyncSession, None],
    dbsession: AsyncSession,
    mocked_publish_message: AsyncMock,
) -> None:
    """Testing update name group from unauthorized user."""
    chat_id = group_chat_with_users.id
    response = await client.patch(
        f"/api/chats/{chat_id}",
        json={"name_group": "New name"},
    )

    mocked_publish_message.assert_not_called()
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.json() == {"detail": "Unauthorized"}


@pytest.mark.anyio
async def test_update_name_group_nonexistent_user(
    authorized_client: AsyncClient,
    chat: ChatFactory,
    override_get_async_session: AsyncGenerator[AsyncSession, None],
    dbsession: AsyncSession,
    mocked_publish_message: AsyncMock,
) -> None:
    """Testing update name group from nonexistent user in chat."""
    response = await authorized_client.patch(
        f"/api/chats/{chat.id}",
        json={"name_group": "New name"},
    )

    mocked_publish_message.assert_not_called()
    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert response.json() == {"detail": "User is not part of the chat"}


@pytest.mark.anyio
async def test_update_name_group_nonexistent_group(
    authorized_client: AsyncClient,
    override_get_async_session: AsyncGenerator[AsyncSession, None],
    dbsession: AsyncSession,
    mocked_publish_message: AsyncMock,
) -> None:
    """Testing update name group in nonexistent group."""
    response = await authorized_client.patch(
        f"/api/chats/{uuid.uuid4()}",
        json={"name_group": "New name"},
    )

    mocked_publish_message.assert_not_called()
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {"detail": "Chat not found"}


@pytest.mark.anyio
async def test_update_name_group_in_direct_chat(
    authorized_client: AsyncClient,
    direct_chat_with_users: ChatFactory,
    override_get_async_session: AsyncGenerator[AsyncSession, None],
    mocked_publish_message: AsyncMock,
) -> None:
    """Testing update name group in direct chat."""
    response = await authorized_client.patch(
        f"/api/chats/{direct_chat_with_users.id}",
        json={"name_group": "New name"},
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json() == {
        "detail": "You can't specify a name chat for direct chat",
    }
