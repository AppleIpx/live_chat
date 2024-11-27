import uuid
from operator import attrgetter
from typing import AsyncGenerator, List

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from tests.factories import ChatFactory, MessageFactory


@pytest.mark.anyio
async def test_get_messages(
    authorized_client: AsyncClient,
    many_messages: List[MessageFactory],
    override_get_async_session: AsyncGenerator[AsyncSession, None],
    dbsession: AsyncSession,
) -> None:
    """Test get list messages in chat."""
    response = await authorized_client.get(
        f"api/chats/{many_messages[0].chat.id}/messages",
    )

    assert response.status_code == status.HTTP_200_OK
    assert len(response.json()["items"]) == len(many_messages[0].chat.messages)
    assert response.json()["items"] == [
        {
            "id": f"{message.id}",
            "user_id": f"{message.user_id}",
            "chat_id": f"{message.chat_id}",
            "content": message.content,
            "created_at": message.created_at.isoformat(),
        }
        for message in sorted(many_messages, key=attrgetter("created_at"), reverse=True)
    ]


@pytest.mark.anyio
async def test_get_messages_unauthorized_user(
    client: AsyncClient,
    many_messages: List[MessageFactory],
    override_get_async_session: AsyncGenerator[AsyncSession, None],
    dbsession: AsyncSession,
) -> None:
    """Test get list messages in chat from unauthorized user."""
    response = await client.get(f"api/chats/{many_messages[0].chat.id}/messages")

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.json() == {"detail": "Unauthorized"}


@pytest.mark.anyio
async def test_get_messages_nonexistent_user(
    authorized_client: AsyncClient,
    many_messages: List[MessageFactory],
    chat: ChatFactory,
    override_get_async_session: AsyncGenerator[AsyncSession, None],
    dbsession: AsyncSession,
) -> None:
    """Testing get messages from nonexistent user in chat."""
    response = await authorized_client.get(f"/api/chats/{chat.id}/messages")

    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert response.json() == {"detail": "User is not part of the chat"}


@pytest.mark.anyio
async def test_get_messages_nonexistent_chat(
    authorized_client: AsyncClient,
    many_messages: List[MessageFactory],
    override_get_async_session: AsyncGenerator[AsyncSession, None],
    dbsession: AsyncSession,
) -> None:
    """Testing get messages in nonexistent chat."""
    response = await authorized_client.get(f"/api/chats/{uuid.uuid4()}/messages")

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {"detail": "Chat not found"}
