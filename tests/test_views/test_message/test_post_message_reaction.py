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
from tests.factories import ChatFactory, MessageFactory
from tests.utils import get_first_reaction_from_db


@pytest.mark.anyio
async def test_post_message_reaction(
    authorized_client: AsyncClient,
    message_in_chat: MessageFactory,
    override_get_async_session: AsyncGenerator[AsyncSession, None],
    dbsession: AsyncSession,
    mocked_publish_message: AsyncMock,
) -> None:
    """Testing post message reaction."""
    chat = message_in_chat.chat
    response = await authorized_client.post(
        f"/api/chats/{chat.id}/messages/{message_in_chat.id}/reaction",
        json={"reaction_type": "😀"},
    )
    target_channel = f"{REDIS_CHANNEL_PREFIX}:{chat.id!s}:{chat.users[1].id!s}"
    reaction = await get_first_reaction_from_db(db_session=dbsession)
    reaction_data = jsonable_encoder(
        {
            "id": reaction.id,
            "reaction_type": "😀",
            "user_id": chat.users[0].id,
            "message_id": message_in_chat.id,
            "updated_at": reaction.updated_at,
        },
    )

    mocked_publish_message.assert_called_with(
        json.dumps({"event": "new_reaction", "data": json.dumps(reaction_data)}),
        channel=target_channel,
    )
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {
        "id": f"{reaction.id}",
        "message_id": f"{message_in_chat.id}",
        "reaction_type": "😀",
        "updated_at": reaction.updated_at.isoformat().replace("+00:00", "Z"),
        "user_id": f"{chat.users[0].id}",
    }


@pytest.mark.anyio
async def test_post_message_reaction_nonexistent_user(
    authorized_client: AsyncClient,
    message_in_chat: MessageFactory,
    override_get_async_session: AsyncGenerator[AsyncSession, None],
    dbsession: AsyncSession,
    mocked_publish_message: AsyncMock,
) -> None:
    """Testing post message reaction from nonexistent user in chat."""
    chat = message_in_chat.chat
    del chat.users[0]
    response = await authorized_client.post(
        f"/api/chats/{chat.id}/messages/{message_in_chat.id}/reaction",
        json={"reaction_type": "😀"},
    )

    mocked_publish_message.assert_not_called()
    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert response.json() == {"detail": "User is not part of the chat"}


@pytest.mark.anyio
async def test_post_message_reaction_nonexistent_chat(
    authorized_client: AsyncClient,
    message_in_chat: MessageFactory,
    override_get_async_session: AsyncGenerator[AsyncSession, None],
    dbsession: AsyncSession,
    mocked_publish_message: AsyncMock,
) -> None:
    """Testing post message reaction in nonexistent chat."""
    response = await authorized_client.post(
        f"/api/chats/{uuid.uuid4()}/messages/{message_in_chat.id}/reaction",
        json={"reaction_type": "😀"},
    )

    mocked_publish_message.assert_not_called()
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {"detail": "Chat not found"}


@pytest.mark.anyio
async def test_post_message_reaction_nonexistent_message(
    authorized_client: AsyncClient,
    direct_chat_with_users: ChatFactory,
    override_get_async_session: AsyncGenerator[AsyncSession, None],
    dbsession: AsyncSession,
    mocked_publish_message: AsyncMock,
) -> None:
    """Testing post message reaction in nonexistent message."""
    response = await authorized_client.post(
        f"/api/chats/{direct_chat_with_users.id}/messages/{uuid.uuid4()}/reaction",
        json={"reaction_type": "😀"},
    )

    mocked_publish_message.assert_not_called()
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {"detail": "Message not found"}


@pytest.mark.anyio
async def test_post_message_reaction_by_deleted_user(
    authorized_deleted_client: AsyncClient,
    message_in_chat: MessageFactory,
    override_get_async_session: AsyncGenerator[AsyncSession, None],
    dbsession: AsyncSession,
) -> None:
    """Testing to post message reaction by a deleted user."""
    chat = message_in_chat.chat
    response = await authorized_deleted_client.post(
        f"/api/chats/{chat.id}/messages/{message_in_chat.id}/reaction",
        json={"reaction_type": "😀"},
    )
    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert response.json() == {"detail": "You are deleted."}
