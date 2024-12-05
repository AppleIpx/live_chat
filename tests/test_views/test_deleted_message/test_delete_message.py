import json
import uuid
from typing import AsyncGenerator
from unittest.mock import AsyncMock

import pytest
from fastapi.encoders import jsonable_encoder
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from live_chat.web.api.chat.utils import get_message_by_id
from live_chat.web.api.chat.utils.get_message_by_id import (
    get_deleted_by_orig_message_id,
)
from live_chat.web.api.messages.constants import REDIS_CHANNEL_PREFIX
from tests.factories import MessageFactory, UserFactory
from tests.utils import get_first_deleted_message


@pytest.mark.anyio
async def test_mark_messages_is_deleted(
    authorized_client: AsyncClient,
    message_in_chat: MessageFactory,
    override_get_async_session: AsyncGenerator[AsyncSession, None],
    mocked_publish_message: AsyncMock,
) -> None:
    """Test mark messages as deleted."""
    chat = message_in_chat.chat
    response = await authorized_client.delete(
        f"/api/chats/{chat.id}/messages/{message_in_chat.id}",
    )
    message_data = json.dumps(jsonable_encoder({"id": message_in_chat.id}))

    mocked_publish_message.assert_called_with(
        json.dumps({"event": "delete_message", "data": message_data}),
        channel=f"{REDIS_CHANNEL_PREFIX}:{chat.id!s}:{chat.users[1].id!s}",
    )
    assert response.status_code == status.HTTP_202_ACCEPTED
    assert response.json() == {"detail": "Сообщение помещено в недавно удаленные"}


@pytest.mark.anyio
async def test_delete_message(
    authorized_client: AsyncClient,
    message_in_chat: MessageFactory,
    override_get_async_session: AsyncGenerator[AsyncSession, None],
    mocked_publish_message: AsyncMock,
) -> None:
    """Test delete message."""
    message_in_chat.is_deleted = True
    chat = message_in_chat.chat
    response = await authorized_client.delete(
        f"/api/chats/{chat.id}/messages/{message_in_chat.id}",
    )
    message_data = json.dumps(jsonable_encoder({"id": message_in_chat.id}))

    mocked_publish_message.assert_called_with(
        json.dumps({"event": "delete_message", "data": message_data}),
        channel=f"{REDIS_CHANNEL_PREFIX}:{chat.id!s}:{chat.users[1].id!s}",
    )
    assert response.status_code == status.HTTP_204_NO_CONTENT


@pytest.mark.anyio
async def test_delete_orig_message(
    authorized_client: AsyncClient,
    message_in_chat: MessageFactory,
    override_get_async_session: AsyncGenerator[AsyncSession, None],
    mocked_publish_message: AsyncMock,
    dbsession: AsyncSession,
) -> None:
    """Testing deleting the original message."""
    message_in_chat.is_deleted = True
    chat = message_in_chat.chat
    response = await authorized_client.delete(
        f"/api/chats/{chat.id}/messages/{message_in_chat.id}",
    )
    message_db = await get_message_by_id(
        db_session=dbsession,
        message_id=message_in_chat.id,
    )
    assert response.status_code == status.HTTP_204_NO_CONTENT
    assert message_db is None


@pytest.mark.anyio
async def test_delete_deleted_message(
    authorized_client: AsyncClient,
    message_in_chat: MessageFactory,
    override_get_async_session: AsyncGenerator[AsyncSession, None],
    mocked_publish_message: AsyncMock,
    dbsession: AsyncSession,
) -> None:
    """Testing deleting an entry in deleteMessage."""
    message_in_chat.is_deleted = True
    chat = message_in_chat.chat
    response = await authorized_client.delete(
        f"/api/chats/{chat.id}/messages/{message_in_chat.id}",
    )
    deleted_message_db = await get_deleted_by_orig_message_id(
        db_session=dbsession,
        orig_message_id=message_in_chat.id,
    )
    assert response.status_code == status.HTTP_204_NO_CONTENT
    assert deleted_message_db is None


@pytest.mark.anyio
async def test_create_deleted_message(
    authorized_client: AsyncClient,
    message_in_chat: MessageFactory,
    override_get_async_session: AsyncGenerator[AsyncSession, None],
    mocked_publish_message: AsyncMock,
    dbsession: AsyncSession,
) -> None:
    """Testing to create a deleted message when a message is deleted."""
    chat = message_in_chat.chat
    response = await authorized_client.delete(
        f"/api/chats/{chat.id}/messages/{message_in_chat.id}",
    )
    deleted_message = await get_first_deleted_message(db_session=dbsession)
    assert response.status_code == status.HTTP_202_ACCEPTED
    assert response.json() == {"detail": "Сообщение помещено в недавно удаленные"}
    assert deleted_message.message_type == message_in_chat.message_type
    assert deleted_message.is_deleted is True
    assert deleted_message.user == message_in_chat.user
    assert deleted_message.user_id == message_in_chat.user_id
    assert deleted_message.content == message_in_chat.content
    assert deleted_message.file_name == message_in_chat.file_name
    assert deleted_message.file_path == message_in_chat.file_path


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
    mocked_publish_message: AsyncMock,
    is_forever: bool,
    expected_status: int,
    expected_response: dict | None,
) -> None:
    """Test delete message with query parameter is_forever."""
    chat = message_in_chat.chat
    response = await authorized_client.delete(
        f"/api/chats/{message_in_chat.chat.id}/messages/{message_in_chat.id}",
        params={"is_forever": is_forever},
    )
    message_data = json.dumps(jsonable_encoder({"id": message_in_chat.id}))

    mocked_publish_message.assert_called_with(
        json.dumps({"event": "delete_message", "data": message_data}),
        channel=f"{REDIS_CHANNEL_PREFIX}:{chat.id!s}:{chat.users[1].id!s}",
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
