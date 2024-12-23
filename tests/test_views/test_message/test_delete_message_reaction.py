import json
import uuid
from typing import AsyncGenerator
from unittest.mock import AsyncMock

import pytest
from fastapi.encoders import jsonable_encoder
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from live_chat.web.api.messages.constants import REDIS_CHANNEL_PREFIX
from tests.factories import ChatFactory, MessageFactory, ReactionFactory


@pytest.mark.anyio
async def test_delete_message_reaction(
    authorized_client: AsyncClient,
    reaction: ReactionFactory,
    override_get_async_session: AsyncGenerator[AsyncSession, None],
    dbsession: AsyncSession,
    mocked_publish_message: AsyncMock,
) -> None:
    """Testing post message reaction."""
    message_id = reaction.message.id
    chat = reaction.message.chat
    response = await authorized_client.delete(
        f"/api/chats/{chat.id}/messages/{message_id}/reaction",
    )
    target_channel = f"{REDIS_CHANNEL_PREFIX}:{chat.id!s}:{chat.users[1].id!s}"
    reaction_data = jsonable_encoder(
        {
            "id": reaction.id,
            "reaction_type": reaction.reaction_type,
            "user_id": reaction.user_id,
            "message_id": reaction.message.id,
            "updated_at": reaction.updated_at,
        },
    )

    mocked_publish_message.assert_called_with(
        json.dumps({"event": "delete_reaction", "data": json.dumps(reaction_data)}),
        channel=target_channel,
    )
    assert response.status_code == status.HTTP_204_NO_CONTENT


@pytest.mark.anyio
async def test_delete_reaction_not_found(
    authorized_client: AsyncClient,
    message_in_chat: MessageFactory,
    override_get_async_session: AsyncGenerator[AsyncSession, None],
    mocked_publish_message: AsyncMock,
) -> None:
    """Test message delete test with non-existent message."""
    response = await authorized_client.delete(
        f"/api/chats/{message_in_chat.chat.id}/messages/{message_in_chat.id}/reaction",
    )

    mocked_publish_message.assert_not_called()
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {"detail": "Reaction not found"}


@pytest.mark.anyio
async def test_delete_reaction_nonexistent_chat(
    authorized_client: AsyncClient,
    message: MessageFactory,
    override_get_async_session: AsyncGenerator[AsyncSession, None],
    mocked_publish_message: AsyncMock,
) -> None:
    """Test message delete test with non-existent chat."""
    response = await authorized_client.delete(
        f"/api/chats/{uuid.uuid4()}/messages/{message.id}/reaction",
    )

    mocked_publish_message.assert_not_called()
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {"detail": "Chat not found"}


@pytest.mark.anyio
async def test_delete_reaction_nonexistent_message(
    authorized_client: AsyncClient,
    direct_chat_with_users: ChatFactory,
    override_get_async_session: AsyncGenerator[AsyncSession, None],
    mocked_publish_message: AsyncMock,
) -> None:
    """Test message delete test with non-existent chat."""
    response = await authorized_client.delete(
        f"/api/chats/{direct_chat_with_users.id}/messages/{uuid.uuid4()}/reaction",
    )

    mocked_publish_message.assert_not_called()
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {"detail": "Message not found"}


@pytest.mark.anyio
async def test_delete_message_reaction_nonexistent_user(
    authorized_client: AsyncClient,
    message_in_chat: MessageFactory,
    override_get_async_session: AsyncGenerator[AsyncSession, None],
    dbsession: AsyncSession,
    mocked_publish_message: AsyncMock,
) -> None:
    """Testing post message reaction from nonexistent user in chat."""
    chat = message_in_chat.chat
    del chat.users[0]
    response = await authorized_client.delete(
        f"/api/chats/{chat.id}/messages/{message_in_chat.id}/reaction",
    )

    mocked_publish_message.assert_not_called()
    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert response.json() == {"detail": "User is not part of the chat"}
