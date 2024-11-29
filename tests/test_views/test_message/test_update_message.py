import uuid
from typing import AsyncGenerator

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from tests.factories import ChatFactory, MessageFactory, UserFactory
from tests.utils import get_first_user_from_db


@pytest.mark.anyio
async def test_update_message(
    authorized_client: AsyncClient,
    chat_with_message: ChatFactory,
    override_get_async_session: AsyncGenerator[AsyncSession, None],
) -> None:
    """Test update message."""
    message = chat_with_message.chat.messages[0]
    response = await authorized_client.patch(
        f"/api/chats/{chat_with_message.chat.id}/messages/{message.id}",
        json={"content": "test"},
    )
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {
        "id": str(message.id),
        "user_id": str(message.user.id),
        "chat_id": str(message.chat.id),
        "content": message.content,
        "created_at": message.created_at.isoformat().replace("+00:00", "Z"),
        "updated_at": message.updated_at.isoformat().replace("+00:00", "Z"),
    }


@pytest.mark.anyio
async def test_update_message_with_fail_chat(
    authorized_client: AsyncClient,
    chat_with_message: ChatFactory,
    override_get_async_session: AsyncGenerator[AsyncSession, None],
) -> None:
    """Test message update test with non-existent chat."""
    message = chat_with_message.chat.messages[0]
    response = await authorized_client.patch(
        f"/api/chats/{uuid.uuid4()}/messages/{message.id}",
        json={"content": "test"},
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {"detail": "Chat not found"}


@pytest.mark.anyio
async def test_update_message_with_fail_message(
    authorized_client: AsyncClient,
    chat_with_message: ChatFactory,
    override_get_async_session: AsyncGenerator[AsyncSession, None],
) -> None:
    """Test message update test with non-existent message."""
    response = await authorized_client.patch(
        f"/api/chats/{chat_with_message.chat.id}/messages/{uuid.uuid4()}",
        json={"content": "test"},
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {"detail": "Message not found"}


@pytest.mark.anyio
async def test_update_message_for_non_member(
    authorized_client: AsyncClient,
    chat_with_message: ChatFactory,
    override_get_async_session: AsyncGenerator[AsyncSession, None],
) -> None:
    """Test for updating a message by a user who is not a member of the group."""
    del chat_with_message.chat.users[0]
    message = chat_with_message.chat.messages[0]
    response = await authorized_client.patch(
        f"/api/chats/{chat_with_message.chat.id}/messages/{message.id}",
        json={"content": "test"},
    )
    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert response.json() == {"detail": "User is not part of the chat"}


@pytest.mark.anyio
async def test_update_message_with_non_author(
    authorized_client: AsyncClient,
    user: UserFactory,
    override_get_async_session: AsyncGenerator[AsyncSession, None],
    dbsession: AsyncSession,
) -> None:
    """Test for update a message by a user who is not a author message."""
    ChatFactory._meta.sqlalchemy_session = dbsession  # noqa: SLF001
    MessageFactory._meta.sqlalchemy_session = dbsession  # noqa: SLF001
    sender = await get_first_user_from_db(dbsession)
    recipient = user
    chat = ChatFactory(users=[sender, recipient])
    message = MessageFactory(
        user=user,
        chat=chat,
        chat_id=chat.id,
        user_id=user.id,
    )
    """Test for updating a message by a user who is not an author message."""
    response = await authorized_client.patch(
        f"/api/chats/{chat.id}/messages/{message.id}",
        json={"content": "test"},
    )
    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert response.json() == {"detail": "User is not the author of this message"}
