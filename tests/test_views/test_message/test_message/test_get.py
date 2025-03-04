import uuid
from _operator import attrgetter
from typing import AsyncGenerator, List

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from live_chat.web.api.messages.utils import get_message_by_id
from live_chat.web.api.users.utils import get_user_by_id
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

    assert response.status_code == status.HTTP_200_OK
    assert len(response.json()["items"]) == len(many_messages)
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
            "parent_message": None,
            "forwarded_message": message.forwarded_message,
            "reactions": [],
        }
        for message in sorted(
            many_messages,
            key=attrgetter("created_at"),
            reverse=True,
        )
    ]


@pytest.mark.anyio
async def test_get_messages_range(
    authorized_client: AsyncClient,
    many_messages: List[MessageFactory],
    override_get_async_session: AsyncGenerator[AsyncSession, None],
    dbsession: AsyncSession,
) -> None:
    """Testing getting a range of messages."""
    response = await authorized_client.get(
        f"api/chats/{many_messages[0].chat.id}/messages/range",
        params={"from_id": many_messages[0].id, "to_id": many_messages[2].id},
    )

    assert response.status_code == status.HTTP_200_OK
    assert len(response.json()) == 3
    assert response.json() == [
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
            "parent_message": None,
            "forwarded_message": message.forwarded_message,
            "reactions": [],
        }
        for message in sorted(many_messages, key=attrgetter("created_at"))[:3]
    ]


@pytest.mark.anyio
async def test_get_message_with_forwarded_message(
    authorized_client: AsyncClient,
    message_in_chat_with_forward_message: MessageFactory,
    override_get_async_session: AsyncGenerator[AsyncSession, None],
    dbsession: AsyncSession,
) -> None:
    """Testing getting a message with forwarded message."""
    message = message_in_chat_with_forward_message
    response = await authorized_client.get(
        f"api/chats/{message.chat.id}/messages",
    )
    forwarding_message = await get_message_by_id(
        db_session=dbsession,
        message_id=message.forwarded_message_id,
    )
    user_forwarded_message = await get_user_by_id(
        db_session=dbsession,
        user_id=forwarding_message.user_id,
    )
    assert response.status_code == status.HTTP_200_OK
    assert forwarding_message is not None
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
            "parent_message": message.parent_message_id,
            "forwarded_message": {
                "id": str(forwarding_message.id),
                "user": {
                    "first_name": user_forwarded_message.first_name,
                    "last_name": user_forwarded_message.last_name,
                    "username": user_forwarded_message.username,
                    "user_image": user_forwarded_message.user_image,
                    "last_online": user_forwarded_message.last_online.isoformat(),
                    "is_deleted": user_forwarded_message.is_deleted,
                    "is_banned": user_forwarded_message.is_banned,
                    "id": str(user_forwarded_message.id),
                },
            },
            "reactions": [],
        },
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
