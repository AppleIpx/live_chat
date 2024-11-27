import uuid
from typing import AsyncGenerator, List

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

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

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {
        "id": f"{many_messages[-1].id}",
        "user_id": f"{many_messages[-1].user.id}",
        "chat_id": f"{many_messages[-1].chat.id}",
        "content": many_messages[-1].content,
        "created_at": many_messages[-1].created_at.isoformat(),
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
