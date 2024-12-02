import uuid
from typing import AsyncGenerator

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from tests.factories import MessageFactory, UserFactory


@pytest.mark.anyio
async def test_mark_messages_is_deleted(
    authorized_client: AsyncClient,
    message_in_chat: MessageFactory,
    override_get_async_session: AsyncGenerator[AsyncSession, None],
) -> None:
    """Test mark messages as deleted."""
    response = await authorized_client.delete(
        f"/api/chats/{message_in_chat.chat.id}/messages/{message_in_chat.id}",
    )
    assert response.status_code == status.HTTP_202_ACCEPTED
    assert response.json() == {"detail": "Сообщение помещено в недавно удаленные"}


@pytest.mark.anyio
async def test_delete_message(
    authorized_client: AsyncClient,
    message_in_chat: MessageFactory,
    override_get_async_session: AsyncGenerator[AsyncSession, None],
) -> None:
    """Test delete message."""
    message_in_chat.is_deleted = True
    chat = message_in_chat.chat
    response = await authorized_client.delete(
        f"/api/chats/{chat.id}/messages/{message_in_chat.id}",
    )
    assert response.status_code == status.HTTP_204_NO_CONTENT


@pytest.mark.anyio
@pytest.mark.parametrize(
    "is_forever, expected_status, expected_response",
    [
        (
            False,
            status.HTTP_202_ACCEPTED,
            {"detail": "Сообщение помещено в недавно удаленные"},
        ),
        (True, status.HTTP_204_NO_CONTENT, None),
    ],
)
async def test_delete_message_with_query_param(
    authorized_client: AsyncClient,
    message_in_chat: MessageFactory,
    override_get_async_session: AsyncGenerator[AsyncSession, None],
    is_forever: bool,
    expected_status: int,
    expected_response: dict | None,
) -> None:
    """Test delete message with query parameter is_forever."""
    response = await authorized_client.delete(
        f"/api/chats/{message_in_chat.chat.id}/messages/{message_in_chat.id}",
        params={"is_forever": is_forever},
    )

    assert response.status_code == expected_status
    if expected_response:
        assert response.json() == expected_response
    else:
        assert not response.content


@pytest.mark.anyio
async def test_delete_message_not_found(
    authorized_client: AsyncClient,
    message_in_chat: MessageFactory,
    override_get_async_session: AsyncGenerator[AsyncSession, None],
) -> None:
    """Test message delete test with non-existent message."""
    response = await authorized_client.delete(
        f"/api/chats/{message_in_chat.chat.id}/messages/{uuid.uuid4()}",
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {"detail": "Message not found"}


@pytest.mark.anyio
async def test_delete_message_with_fail_chat(
    authorized_client: AsyncClient,
    message_in_chat: MessageFactory,
    override_get_async_session: AsyncGenerator[AsyncSession, None],
) -> None:
    """Test message delete test with non-existent chat."""
    response = await authorized_client.delete(
        f"/api/chats/{uuid.uuid4()}/messages/{message_in_chat.id}",
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {"detail": "Chat not found"}


@pytest.mark.anyio
async def test_delete_message_for_non_member(
    authorized_client: AsyncClient,
    message_in_chat: MessageFactory,
    override_get_async_session: AsyncGenerator[AsyncSession, None],
) -> None:
    """Test for delete a message by a user who is not a member of the group."""
    del message_in_chat.chat.users[0]
    response = await authorized_client.delete(
        f"/api/chats/{message_in_chat.chat.id}/messages/{message_in_chat.id}",
    )
    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert response.json() == {"detail": "User is not part of the chat"}


@pytest.mark.anyio
async def test_delete_message_with_non_author(
    authorized_client: AsyncClient,
    user: UserFactory,
    message_in_chat: MessageFactory,
    override_get_async_session: AsyncGenerator[AsyncSession, None],
    dbsession: AsyncSession,
) -> None:
    """Test for delete a message by a user who is not a author message."""
    message_in_chat.user = user
    response = await authorized_client.delete(
        f"/api/chats/{message_in_chat.chat.id}/messages/{message_in_chat.id}",
    )
    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert response.json() == {"detail": "User is not the author of this message"}
