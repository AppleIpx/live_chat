import uuid
from typing import AsyncGenerator

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from live_chat.web.api.read_status.utils import get_read_status_by_user_chat_ids
from tests.factories import ChatFactory, MessageFactory


@pytest.mark.anyio
async def test_update_read_status(
    authorized_client: AsyncClient,
    message_in_chat: MessageFactory,
    override_get_async_session: AsyncGenerator[AsyncSession, None],
    dbsession: AsyncSession,
) -> None:
    """Testing read status update."""
    read_status = await get_read_status_by_user_chat_ids(
        db_session=dbsession,
        chat_id=message_in_chat.chat.id,
        user_id=message_in_chat.user.id,
    )
    response = await authorized_client.patch(
        f"/api/read_status/{message_in_chat.chat.id}/update",
        json={
            "last_read_message_id": str(message_in_chat.id),
            "count_unread_msg": 0,
        },
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
    message_in_chat: MessageFactory,
    override_get_async_session: AsyncGenerator[AsyncSession, None],
    dbsession: AsyncSession,
) -> None:
    """Testing update read status from unauthorized user."""
    response = await client.patch(
        f"/api/read_status/{message_in_chat.chat.id}/update",
        json={
            "last_read_message_id": str(message_in_chat.id),
            "count_unread_msg": 0,
        },
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.json() == {"detail": "Unauthorized"}


@pytest.mark.anyio
async def test_update_read_status_nonexistent_chat(
    authorized_client: AsyncClient,
    message_in_chat: MessageFactory,
    override_get_async_session: AsyncGenerator[AsyncSession, None],
    dbsession: AsyncSession,
) -> None:
    """Testing update read status in nonexistent chat."""
    response = await authorized_client.patch(
        f"/api/read_status/{uuid.uuid4()}/update",
        json={
            "last_read_message_id": str(message_in_chat.id),
            "count_unread_msg": 0,
        },
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {"detail": "Chat not found"}


@pytest.mark.anyio
async def test_update_read_status_nonexistent_user(
    authorized_client: AsyncClient,
    message_in_chat: MessageFactory,
    override_get_async_session: AsyncGenerator[AsyncSession, None],
    dbsession: AsyncSession,
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
    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert response.json() == {"detail": "User is not part of the chat"}


@pytest.mark.anyio
async def test_update_read_status_nonexistent_read_status(
    authorized_client: AsyncClient,
    direct_chat_with_users: ChatFactory,
    message_in_chat: MessageFactory,
    override_get_async_session: AsyncGenerator[AsyncSession, None],
    dbsession: AsyncSession,
) -> None:
    """Testing update read status in nonexistent read status."""
    response = await authorized_client.patch(
        f"/api/read_status/{direct_chat_with_users.id}/update",
        json={
            "last_read_message_id": str(message_in_chat.id),
            "count_unread_msg": 0,
        },
    )
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
) -> None:
    """Testing update read status in nonexistent message."""
    response = await authorized_client.patch(
        f"/api/read_status/{message_in_chat.chat.id}/update",
        json={
            "last_read_message_id": str(uuid.uuid4()),
            "count_unread_msg": 0,
        },
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {"detail": "Message not found"}
