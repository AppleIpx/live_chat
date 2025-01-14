import json
import uuid
from typing import AsyncGenerator
from unittest.mock import AsyncMock

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from live_chat.web.api.chat.utils import get_deleted_message_by_id, get_message_by_id
from live_chat.web.api.messages.constants import REDIS_CHANNEL_PREFIX
from tests.factories import DeletedMessageFactory, MessageFactory, UserFactory
from tests.utils import transformation_message_data


@pytest.mark.anyio
async def test_recover_deleted_message(
    authorized_client: AsyncClient,
    deleted_message_in_chat: DeletedMessageFactory,
    override_get_async_session: AsyncGenerator[AsyncSession, None],
    dbsession: AsyncSession,
    mocked_publish_message: AsyncMock,
) -> None:
    """Testing recover_deleted_message."""
    chat = deleted_message_in_chat.chat
    response = await authorized_client.post(
        f"/api/chats/{chat.id}/messages/{deleted_message_in_chat.id}/recover",
    )
    deleted_mesage_db = await get_deleted_message_by_id(
        db_session=dbsession,
        deleted_message_id=deleted_message_in_chat.id,
    )
    orig_message = await get_message_by_id(
        db_session=dbsession,
        message_id=deleted_message_in_chat.original_message_id,
    )
    target_channel = f"{REDIS_CHANNEL_PREFIX}:{chat.id!s}:{chat.users[1].id!s}"
    message_data = await transformation_message_data(orig_message)

    mocked_publish_message.assert_called_with(
        json.dumps({"event": "recover_message", "data": message_data}),
        channel=target_channel,
    )
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {"detail": "Message restored"}
    assert deleted_mesage_db is None
    assert orig_message is not None
    assert orig_message.is_deleted is False
    assert chat.last_message_content == orig_message.content[:100]


@pytest.mark.anyio
async def test_invalid_deleted_message(
    authorized_client: AsyncClient,
    message_in_chat: MessageFactory,
    override_get_async_session: AsyncGenerator[AsyncSession, None],
    dbsession: AsyncSession,
    mocked_publish_message: AsyncMock,
) -> None:
    """
    Testing the error.

    That occurs when restoring a message if there is no entry
    about it in the DeletedMessage
    """
    chat = message_in_chat.chat
    response = await authorized_client.post(
        f"/api/chats/{chat.id}/messages/{message_in_chat.id}/recover",
    )

    mocked_publish_message.assert_not_called()
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json() == {"detail": "Instance is not deleted message"}


@pytest.mark.anyio
async def test_recover_message_with_failed_chat(
    authorized_client: AsyncClient,
    deleted_message_in_chat: DeletedMessageFactory,
    override_get_async_session: AsyncGenerator[AsyncSession, None],
    dbsession: AsyncSession,
    mocked_publish_message: AsyncMock,
) -> None:
    """Testing recovery of a message indicating the wrong chat."""
    response = await authorized_client.post(
        f"/api/chats/{uuid.uuid4()}/messages/{deleted_message_in_chat.id}/recover",
    )

    mocked_publish_message.assert_not_called()
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {"detail": "Chat not found"}


@pytest.mark.anyio
async def test_recover_message_with_failed_message(
    authorized_client: AsyncClient,
    deleted_message_in_chat: DeletedMessageFactory,
    override_get_async_session: AsyncGenerator[AsyncSession, None],
    dbsession: AsyncSession,
    mocked_publish_message: AsyncMock,
) -> None:
    """Testing recovery of a message indicating the wrong message."""
    response = await authorized_client.post(
        f"/api/chats/{deleted_message_in_chat.chat.id}/messages/{uuid.uuid4()}/recover",
    )

    mocked_publish_message.assert_not_called()
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {"detail": "Message not found"}


@pytest.mark.anyio
async def test_recover_message_for_non_member(
    authorized_client: AsyncClient,
    deleted_message_in_chat: DeletedMessageFactory,
    override_get_async_session: AsyncGenerator[AsyncSession, None],
    dbsession: AsyncSession,
    mocked_publish_message: AsyncMock,
) -> None:
    """Test for recover a message by a user who is not a member of the group."""
    del deleted_message_in_chat.chat.users[0]
    chat = deleted_message_in_chat.chat
    response = await authorized_client.post(
        f"/api/chats/{chat.id}/messages/{deleted_message_in_chat.id}/recover",
    )

    mocked_publish_message.assert_not_called()
    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert response.json() == {"detail": "User is not part of the chat"}


@pytest.mark.anyio
async def test_recover_message_with_non_author(
    authorized_client: AsyncClient,
    deleted_message_in_chat: DeletedMessageFactory,
    user: UserFactory,
    override_get_async_session: AsyncGenerator[AsyncSession, None],
    dbsession: AsyncSession,
    mocked_publish_message: AsyncMock,
) -> None:
    """Test for recover a message by a user who is not a author message."""
    deleted_message_in_chat.user = user
    chat = deleted_message_in_chat.chat
    response = await authorized_client.post(
        f"/api/chats/{chat.id}/messages/{deleted_message_in_chat.id}/recover",
    )

    mocked_publish_message.assert_not_called()
    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert response.json() == {"detail": "User is not the author of this message"}


@pytest.mark.anyio
async def test_recover_message_by_deleted_user(
    authorized_deleted_client: AsyncClient,
    deleted_message_in_chat: DeletedMessageFactory,
    override_get_async_session: AsyncGenerator[AsyncSession, None],
    dbsession: AsyncSession,
) -> None:
    """Testing recover deleted message by a deleted user."""
    chat = deleted_message_in_chat.chat
    response = await authorized_deleted_client.post(
        f"/api/chats/{chat.id}/messages/{deleted_message_in_chat.id}/recover",
    )
    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert response.json() == {"detail": "You are deleted."}


@pytest.mark.anyio
async def test_recover_message_by_banned_user(
    authorized_banned_client: AsyncClient,
    deleted_message_in_chat: DeletedMessageFactory,
    override_get_async_session: AsyncGenerator[AsyncSession, None],
    dbsession: AsyncSession,
) -> None:
    """Testing recover deleted message by a banned user."""
    chat = deleted_message_in_chat.chat
    response = await authorized_banned_client.post(
        f"/api/chats/{chat.id}/messages/{deleted_message_in_chat.id}/recover",
    )
    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert response.json() == {
        "detail": {
            "reason": None,
            "status": "banned",
        },
    }
