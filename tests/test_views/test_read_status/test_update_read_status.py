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
from live_chat.web.api.read_status.utils import get_read_status_by_user_chat_ids
from tests.factories import ChatFactory, MessageFactory


@pytest.mark.anyio
async def test_update_read_status(
    authorized_client: AsyncClient,
    message_in_chat: MessageFactory,
    override_get_async_session: AsyncGenerator[AsyncSession, None],
    dbsession: AsyncSession,
    mocked_publish_message: AsyncMock,
) -> None:
    """Testing read status update."""
    chat = message_in_chat.chat
    read_status = await get_read_status_by_user_chat_ids(
        db_session=dbsession,
        chat_id=chat.id,
        user_id=message_in_chat.user.id,
    )
    target_channel = f"{REDIS_CHANNEL_PREFIX}:{chat.id!s}:{chat.users[1].id!s}"

    response = await authorized_client.patch(
        f"/api/read_status/{chat.id}/update",
        json={
            "last_read_message_id": str(message_in_chat.id),
            "count_unread_msg": 0,
        },
    )
    event_data = jsonable_encoder(
        {
            "id": read_status.id,
            "last_read_message_id": read_status.last_read_message_id,
            "user_id": read_status.user_id,
            "chat_id": read_status.chat_id,
            "count_unread_msg": read_status.count_unread_msg,
        },
    )

    mocked_publish_message.assert_called_with(
        json.dumps({"event": "update_read_status", "data": json.dumps(event_data)}),
        channel=target_channel,
    )
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {
        "id": str(read_status.id),
        "last_read_message_id": str(message_in_chat.id),
        "user_id": str(message_in_chat.chat.users[0].id),
        "chat_id": str(message_in_chat.chat.id),
        "count_unread_msg": 0,
    }


@pytest.mark.anyio
async def test_update_read_status_unauthorized_user(
    client: AsyncClient,
    chat: ChatFactory,
    dbsession: AsyncSession,
    mocked_publish_message: AsyncMock,
) -> None:
    """Testing update read status from unauthorized user."""
    response = await client.patch(
        f"/api/read_status/{chat.id}/update",
        json={
            "last_read_message_id": str(chat.id),
            "count_unread_msg": 0,
        },
    )

    mocked_publish_message.assert_not_called()
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.json() == {"detail": "Unauthorized"}


@pytest.mark.anyio
async def test_update_read_status_nonexistent_chat(
    authorized_client: AsyncClient,
    message_in_chat: MessageFactory,
    override_get_async_session: AsyncGenerator[AsyncSession, None],
    dbsession: AsyncSession,
    mocked_publish_message: AsyncMock,
) -> None:
    """Testing update read status in nonexistent chat."""
    response = await authorized_client.patch(
        f"/api/read_status/{uuid.uuid4()}/update",
        json={
            "last_read_message_id": str(message_in_chat.id),
            "count_unread_msg": 0,
        },
    )

    mocked_publish_message.assert_not_called()
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {"detail": "Chat not found"}


@pytest.mark.anyio
async def test_update_read_status_nonexistent_user(
    authorized_client: AsyncClient,
    message_in_chat: MessageFactory,
    override_get_async_session: AsyncGenerator[AsyncSession, None],
    dbsession: AsyncSession,
    mocked_publish_message: AsyncMock,
) -> None:
    """Testing update read status in nonexistent user."""
    del message_in_chat.chat.users[0]
    response = await authorized_client.patch(
        f"/api/read_status/{message_in_chat.chat.id}/update",
        json={
            "last_read_message_id": str(message_in_chat.id),
            "count_unread_msg": 0,
        },
    )

    mocked_publish_message.assert_not_called()
    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert response.json() == {"detail": "User is not part of the chat"}


@pytest.mark.anyio
async def test_update_read_status_nonexistent_read_status(
    authorized_client: AsyncClient,
    direct_chat_with_users: ChatFactory,
    message_in_chat: MessageFactory,
    override_get_async_session: AsyncGenerator[AsyncSession, None],
    dbsession: AsyncSession,
    mocked_publish_message: AsyncMock,
) -> None:
    """Testing update read status in nonexistent read status."""
    response = await authorized_client.patch(
        f"/api/read_status/{direct_chat_with_users.id}/update",
        json={
            "last_read_message_id": str(message_in_chat.id),
            "count_unread_msg": 0,
        },
    )

    mocked_publish_message.assert_not_called()
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {
        "detail": "Read status not found for the given chat and user.",
    }


@pytest.mark.anyio
async def test_update_read_status_nonexistent_message(
    authorized_client: AsyncClient,
    message_in_chat: MessageFactory,
    override_get_async_session: AsyncGenerator[AsyncSession, None],
    dbsession: AsyncSession,
    mocked_publish_message: AsyncMock,
) -> None:
    """Testing update read status in nonexistent message."""
    response = await authorized_client.patch(
        f"/api/read_status/{message_in_chat.chat.id}/update",
        json={
            "last_read_message_id": str(uuid.uuid4()),
            "count_unread_msg": 0,
        },
    )

    mocked_publish_message.assert_not_called()
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {"detail": "Message not found"}


@pytest.mark.anyio
async def test_update_read_status_by_deleted_user(
    authorized_deleted_client: AsyncClient,
    message_in_chat: MessageFactory,
    dbsession: AsyncSession,
    override_get_async_session: AsyncGenerator[AsyncSession, None],
) -> None:
    """Testing to update read status by a deleted user."""
    chat = message_in_chat.chat
    await get_read_status_by_user_chat_ids(
        db_session=dbsession,
        chat_id=chat.id,
        user_id=message_in_chat.user.id,
    )
    response = await authorized_deleted_client.patch(
        f"/api/read_status/{chat.id}/update",
        json={
            "last_read_message_id": str(message_in_chat.id),
            "count_unread_msg": 0,
        },
    )
    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert response.json() == {"detail": "You are deleted."}


@pytest.mark.anyio
async def test_update_read_status_by_banned_user(
    authorized_banned_client: AsyncClient,
    message_in_chat: MessageFactory,
    override_get_async_session: AsyncGenerator[AsyncSession, None],
    dbsession: AsyncSession,
) -> None:
    """Testing to update read status by a banned user."""
    chat = message_in_chat.chat
    await get_read_status_by_user_chat_ids(
        db_session=dbsession,
        chat_id=chat.id,
        user_id=message_in_chat.user.id,
    )
    response = await authorized_banned_client.patch(
        f"/api/read_status/{chat.id}/update",
        json={
            "last_read_message_id": str(message_in_chat.id),
            "count_unread_msg": 0,
        },
    )
    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert response.json() == {
        "detail": {
            "reason": None,
            "status": "banned",
        },
    }
