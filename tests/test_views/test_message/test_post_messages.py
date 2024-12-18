import json
import uuid
from typing import AsyncGenerator
from unittest.mock import AsyncMock

import pytest
from httpx import AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from live_chat.db.models.chat import Message
from live_chat.web.api.messages.constants import REDIS_CHANNEL_PREFIX
from tests.factories import ChatFactory, ReadStatusFactory
from tests.utils import transformation_message_data


@pytest.mark.anyio
async def test_post_message(
    authorized_client: AsyncClient,
    direct_chat_with_users: ChatFactory,
    override_get_async_session: AsyncGenerator[AsyncSession, None],
    dbsession: AsyncSession,
    mocked_publish_message: AsyncMock,
) -> None:
    """Testing post message."""
    chat_id = direct_chat_with_users.id
    recipient = direct_chat_with_users.users[1]
    ReadStatusFactory._meta.sqlalchemy_session = dbsession  # noqa: SLF001
    read_status = ReadStatusFactory(
        chat_id=chat_id,
        chat=direct_chat_with_users,
        user=recipient,
        user_id=recipient.id,
        last_read_message_id=None,
        count_unread_msg=0,
    )
    target_channel = f"{REDIS_CHANNEL_PREFIX}:{chat_id!s}:{recipient.id!s}"
    response = await authorized_client.post(
        f"/api/chats/{chat_id}/messages",
        json={"content": "test"},
    )
    query = select(Message).where(Message.chat_id == chat_id)
    message = (await dbsession.execute(query)).scalar_one_or_none()
    message_data = await transformation_message_data(message)
    mocked_publish_message.assert_called_with(
        json.dumps({"event": "new_message", "data": message_data}),
        channel=target_channel,
    )
    assert read_status.count_unread_msg == 1
    assert direct_chat_with_users.last_message_content == "test"
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {
        "id": f"{message.id}",
        "chat_id": f"{chat_id}",
        "message_type": message.message_type.value,
        "content": "test",
        "file_name": message.file_name,
        "file_path": message.file_path,
        "created_at": message.created_at.isoformat().replace("+00:00", "Z"),
        "is_deleted": False,
        "updated_at": message.updated_at.isoformat().replace("+00:00", "Z"),
        "user_id": f"{direct_chat_with_users.users[0].id}",
    }


@pytest.mark.anyio
async def test_post_message_unauthorized_user(
    client: AsyncClient,
    direct_chat_with_users: ChatFactory,
    override_get_async_session: AsyncGenerator[AsyncSession, None],
    dbsession: AsyncSession,
    mocked_publish_message: AsyncMock,
) -> None:
    """Testing post message from unauthorized user."""
    chat_id = direct_chat_with_users.id
    response = await client.post(
        f"/api/chats/{chat_id}/messages",
        json={"content": "test"},
    )

    mocked_publish_message.assert_not_called()
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.json() == {"detail": "Unauthorized"}


@pytest.mark.anyio
async def test_post_message_nonexistent_user(
    authorized_client: AsyncClient,
    chat: ChatFactory,
    override_get_async_session: AsyncGenerator[AsyncSession, None],
    dbsession: AsyncSession,
    mocked_publish_message: AsyncMock,
) -> None:
    """Testing post message from nonexistent user in chat."""
    response = await authorized_client.post(
        f"/api/chats/{chat.id}/messages",
        json={"content": "test"},
    )

    mocked_publish_message.assert_not_called()
    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert response.json() == {"detail": "User is not part of the chat"}


@pytest.mark.anyio
async def test_post_message_nonexistent_chat(
    authorized_client: AsyncClient,
    override_get_async_session: AsyncGenerator[AsyncSession, None],
    dbsession: AsyncSession,
    mocked_publish_message: AsyncMock,
) -> None:
    """Testing post message in nonexistent chat."""
    response = await authorized_client.post(
        f"/api/chats/{uuid.uuid4()}/messages",
        json={"content": "test"},
    )

    mocked_publish_message.assert_not_called()
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {"detail": "Chat not found"}
