import uuid
from typing import AsyncGenerator, List

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from live_chat.web.api.messages.utils import (
    get_correct_last_message,
)
from tests.factories import ChatFactory, MessageFactory


@pytest.mark.anyio
async def test_get_last_message(
    authorized_client: AsyncClient,
    many_messages: List[MessageFactory],
    override_get_async_session: AsyncGenerator[AsyncSession, None],
    dbsession: AsyncSession,
) -> None:
    """Test get last message."""
    response = await authorized_client.get(
        f"api/chats/{many_messages[0].chat.id}/messages/last",
    )
    last_message = await get_correct_last_message(messages=many_messages)

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {
        "id": f"{last_message.id}",
        "user_id": f"{last_message.user.id}",
        "chat_id": f"{last_message.chat.id}",
        "content": last_message.content,
        "created_at": last_message.created_at.isoformat(),
        "updated_at": last_message.updated_at.isoformat(),
        "is_deleted": last_message.is_deleted,
    }


@pytest.mark.anyio
async def test_get_last_message_unauthorized_user(
    client: AsyncClient,
    many_messages: List[MessageFactory],
    override_get_async_session: AsyncGenerator[AsyncSession, None],
    dbsession: AsyncSession,
) -> None:
    """Test get last message from unauthorized user."""
    response = await client.get(f"api/chats/{many_messages[0].chat.id}/messages/last")

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.json() == {"detail": "Unauthorized"}


@pytest.mark.anyio
async def test_get_last_message_nonexistent_user(
    authorized_client: AsyncClient,
    many_messages: List[MessageFactory],
    chat: ChatFactory,
    override_get_async_session: AsyncGenerator[AsyncSession, None],
    dbsession: AsyncSession,
) -> None:
    """Testing get last message from nonexistent user in chat."""
    response = await authorized_client.get(f"/api/chats/{chat.id}/messages/last")

    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert response.json() == {"detail": "User is not part of the chat"}


@pytest.mark.anyio
async def test_get_last_message_nonexistent_chat(
    authorized_client: AsyncClient,
    many_messages: List[MessageFactory],
    override_get_async_session: AsyncGenerator[AsyncSession, None],
    dbsession: AsyncSession,
) -> None:
    """Testing get last message in nonexistent chat."""
    response = await authorized_client.get(f"/api/chats/{uuid.uuid4()}/messages/last")

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {"detail": "Chat not found"}
