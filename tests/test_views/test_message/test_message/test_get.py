import uuid
from _operator import attrgetter
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
    """Testing getting a list of messages with is_deleted=false in chat."""
    response = await authorized_client.get(
        f"api/chats/{many_messages[0].chat.id}/messages",
    )
    non_deleted_messages = [
        message for message in many_messages if not message.is_deleted
    ]
    assert response.status_code == status.HTTP_200_OK
    assert len(response.json()["items"]) == len(non_deleted_messages)
    assert response.json()["items"] == [
        {
            "id": f"{message.id}",
            "user_id": f"{message.user_id}",
            "chat_id": f"{message.chat_id}",
            "content": message.content,
            "message_type": message.message_type.value,
            "file_name": message.file_name,
            "file_path": message.file_path,
            "created_at": message.created_at.isoformat(),
            "updated_at": message.updated_at.isoformat(),
            "is_deleted": message.is_deleted,
            "parent_message_id": message.parent_message_id,
            "forwarded_message": message.forwarded_message,
            "reactions": [],
        }
        for message in sorted(
            non_deleted_messages,
            key=attrgetter("created_at"),
            reverse=True,
        )
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
    override_get_async_session: AsyncGenerator[AsyncSession, None],
    dbsession: AsyncSession,
) -> None:
    """Testing get messages in nonexistent chat."""
    response = await authorized_client.get(f"/api/chats/{uuid.uuid4()}/messages")

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {"detail": "Chat not found"}


@pytest.mark.anyio
async def test_get_messages_by_deleted_user(
    authorized_deleted_client: AsyncClient,
    many_messages: List[MessageFactory],
    override_get_async_session: AsyncGenerator[AsyncSession, None],
    dbsession: AsyncSession,
) -> None:
    """Testing recover message by a deleted user."""
    chat_id = many_messages[0].chat.id
    response = await authorized_deleted_client.get(f"/api/chats/{chat_id}/messages")
    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert response.json() == {"detail": "You are deleted."}


@pytest.mark.anyio
async def test_get_messages_by_banned_user(
    authorized_banned_client: AsyncClient,
    many_messages: List[MessageFactory],
    override_get_async_session: AsyncGenerator[AsyncSession, None],
    dbsession: AsyncSession,
) -> None:
    """Testing recover message by a banned user."""
    chat_id = many_messages[0].chat.id
    response = await authorized_banned_client.get(f"/api/chats/{chat_id}/messages")

    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert response.json() == {
        "detail": {
            "reason": None,
            "status": "banned",
        },
    }
