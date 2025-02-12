import json
import uuid
from typing import AsyncGenerator
from unittest.mock import AsyncMock

import pytest
from faker import Faker
from httpx import AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from live_chat.db.models.messages import Message
from live_chat.web.api.messages.constants import REDIS_CHANNEL_PREFIX
from live_chat.web.api.messages.utils import get_message_by_id
from live_chat.web.api.users.utils import get_user_by_id
from tests.factories import (
    BlackListFactory,
    ChatFactory,
    MessageFactory,
    ReadStatusFactory,
)
from tests.utils import transformation_message_data


@pytest.mark.anyio
async def test_post_text_message(
    authorized_client: AsyncClient,
    direct_chat_with_users: ChatFactory,
    override_get_async_session: AsyncGenerator[AsyncSession, None],
    dbsession: AsyncSession,
    mocked_publish_message: AsyncMock,
) -> None:
    """Testing post text message."""
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
    assert response.status_code == status.HTTP_201_CREATED
    assert response.json() == {
        "id": f"{message.id}",
        "chat_id": f"{chat_id}",
        "message_type": message.message_type.value,
        "content": "test",
        "file_name": message.file_name,
        "file_path": message.file_path,
        "created_at": message.created_at.isoformat().replace("+00:00", "Z"),
        "is_deleted": False,
        "reactions": [],
        "parent_message": None,
        "forwarded_message": message.forwarded_message,
        "updated_at": message.updated_at.isoformat().replace("+00:00", "Z"),
        "user_id": f"{direct_chat_with_users.users[0].id}",
    }


@pytest.mark.anyio
async def test_post_reply_message(
    authorized_client: AsyncClient,
    message_in_chat: MessageFactory,
    override_get_async_session: AsyncGenerator[AsyncSession, None],
    dbsession: AsyncSession,
    mocked_publish_message: AsyncMock,
) -> None:
    """Testing post reply message."""
    chat_id = message_in_chat.chat.id
    recipient = await get_user_by_id(
        db_session=dbsession,
        user_id=message_in_chat.chat.users[1].id,
    )
    target_channel = f"{REDIS_CHANNEL_PREFIX}:{chat_id!s}:{recipient.id!s}"
    response = await authorized_client.post(
        f"/api/chats/{chat_id}/messages",
        json={
            "message_type": "text",
            "content": "test",
            "parent_message": {
                "id": str(message_in_chat.id),
                "message_type": message_in_chat.message_type.value,
                "file_name": message_in_chat.file_name,
                "file_path": message_in_chat.file_path,
                "content": message_in_chat.content,
            },
            "file_name": None,
            "file_path": None,
        },
    )
    new_message_id = response.json()["id"]
    new_message = await get_message_by_id(
        db_session=dbsession,
        message_id=new_message_id,
    )
    message_data = await transformation_message_data(new_message)
    mocked_publish_message.assert_called_with(
        json.dumps({"event": "new_message", "data": message_data}),
        channel=target_channel,
    )
    sender = await get_user_by_id(db_session=dbsession, user_id=new_message.user_id)
    assert response.status_code == status.HTTP_201_CREATED
    assert response.json() == {
        "id": f"{new_message.id}",
        "chat_id": f"{chat_id}",
        "message_type": new_message.message_type.value,
        "content": "test",
        "file_name": new_message.file_name,
        "file_path": new_message.file_path,
        "forwarded_message": new_message.forwarded_message,
        "created_at": new_message.created_at.isoformat().replace("+00:00", "Z"),
        "is_deleted": False,
        "reactions": [],
        "parent_message": None,
        "updated_at": new_message.updated_at.isoformat().replace("+00:00", "Z"),
        "user_id": f"{sender.id}",
    }


@pytest.mark.anyio
async def test_post_reply_message_with_not_exist_parent_message(
    authorized_client: AsyncClient,
    message_in_chat: MessageFactory,
    override_get_async_session: AsyncGenerator[AsyncSession, None],
    dbsession: AsyncSession,
) -> None:
    """Testing post reply message with not exist parent message."""
    chat_id = message_in_chat.chat.id
    response = await authorized_client.post(
        f"/api/chats/{chat_id}/messages",
        json={
            "message_type": "text",
            "content": "test",
            "parent_message_id": str(uuid.uuid4()),
            "file_name": None,
            "file_path": None,
        },
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {"detail": "Parent message does not exist."}


@pytest.mark.anyio
async def test_post_file_message(
    authorized_client: AsyncClient,
    direct_chat_with_users: ChatFactory,
    override_get_async_session: AsyncGenerator[AsyncSession, None],
    dbsession: AsyncSession,
    mocked_publish_message: AsyncMock,
    faker: Faker,
) -> None:
    """Testing post file message."""
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
        json={
            "message_type": "file",
            "file_name": "test",
            "file_path": faker.url(),
        },
    )
    query = select(Message).where(Message.chat_id == chat_id)
    message = (await dbsession.execute(query)).scalar_one_or_none()
    message_data = await transformation_message_data(message)
    mocked_publish_message.assert_called_with(
        json.dumps({"event": "new_message", "data": message_data}),
        channel=target_channel,
    )
    assert read_status.count_unread_msg == 1
    assert direct_chat_with_users.last_message_content is None
    assert response.status_code == status.HTTP_201_CREATED
    assert response.json() == {
        "id": f"{message.id}",
        "chat_id": f"{chat_id}",
        "message_type": message.message_type.value,
        "content": None,
        "file_name": message.file_name,
        "file_path": message.file_path,
        "forwarded_message": message.forwarded_message,
        "created_at": message.created_at.isoformat().replace("+00:00", "Z"),
        "is_deleted": False,
        "reactions": [],
        "parent_message": None,
        "updated_at": message.updated_at.isoformat().replace("+00:00", "Z"),
        "user_id": f"{direct_chat_with_users.users[0].id}",
    }


@pytest.mark.anyio
async def test_post_message_to_blocked_user(
    authorized_client: AsyncClient,
    direct_chat_with_users: ChatFactory,
    black_list_with_user: BlackListFactory,
    override_get_async_session: AsyncGenerator[AsyncSession, None],
    dbsession: AsyncSession,
) -> None:
    """Testing post message to blocked user."""
    chat_id = direct_chat_with_users.id
    response = await authorized_client.post(
        f"/api/chats/{chat_id}/messages",
        json={"content": "test"},
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json() == {
        "detail": "You can't perform this action, because he's blocked",
    }


@pytest.mark.anyio
async def test_post_message_from_blocked_user(
    authorized_client: AsyncClient,
    direct_chat_with_users: ChatFactory,
    black_list_with_auth_user: BlackListFactory,
    override_get_async_session: AsyncGenerator[AsyncSession, None],
    dbsession: AsyncSession,
) -> None:
    """Testing sending a message if the sender is on the recipient black list."""
    chat_id = direct_chat_with_users.id
    response = await authorized_client.post(
        f"/api/chats/{chat_id}/messages",
        json={"content": "test"},
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json() == {
        "detail": "You can't perform this action, you are on the black list",
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


@pytest.mark.anyio
async def test_post_message_by_deleted_user(
    authorized_deleted_client: AsyncClient,
    direct_chat_with_users: ChatFactory,
    override_get_async_session: AsyncGenerator[AsyncSession, None],
    dbsession: AsyncSession,
) -> None:
    """Testing to post message by a deleted user."""
    response = await authorized_deleted_client.post(
        f"/api/chats/{direct_chat_with_users.id}/messages",
        json={"content": "test"},
    )

    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert response.json() == {"detail": "You are deleted."}


@pytest.mark.anyio
async def test_post_message_to_deleted_user(
    authorized_client: AsyncClient,
    direct_chat_with_users: ChatFactory,
    override_get_async_session: AsyncGenerator[AsyncSession, None],
    dbsession: AsyncSession,
) -> None:
    """Testing to post message to a deleted user."""
    reciepent = direct_chat_with_users.users[1]
    reciepent.is_deleted = True
    response = await authorized_client.post(
        f"/api/chats/{direct_chat_with_users.id}/messages",
        json={"content": "test"},
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json() == {"detail": "This user has been deleted."}


@pytest.mark.anyio
async def test_post_message_by_banned_user(
    authorized_banned_client: AsyncClient,
    direct_chat_with_users: ChatFactory,
    override_get_async_session: AsyncGenerator[AsyncSession, None],
    dbsession: AsyncSession,
) -> None:
    """Testing to post message by a banned user."""
    response = await authorized_banned_client.post(
        f"/api/chats/{direct_chat_with_users.id}/messages",
        json={"content": "test"},
    )

    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert response.json() == {
        "detail": {
            "reason": None,
            "status": "banned",
        },
    }


@pytest.mark.anyio
async def test_post_message_to_banned_user(
    authorized_client: AsyncClient,
    direct_chat_with_users: ChatFactory,
    override_get_async_session: AsyncGenerator[AsyncSession, None],
    dbsession: AsyncSession,
) -> None:
    """Testing to post message to a banned user."""
    reciepent = direct_chat_with_users.users[1]
    reciepent.is_banned = True
    response = await authorized_client.post(
        f"/api/chats/{direct_chat_with_users.id}/messages",
        json={"content": "test"},
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json() == {"detail": "This user has been banned."}


@pytest.mark.anyio
async def test_post_forwarding_messages(
    authorized_client: AsyncClient,
    message_in_chat: MessageFactory,
    direct_chat_with_users: ChatFactory,
    dbsession: AsyncSession,
    override_get_async_session: AsyncGenerator[AsyncSession, None],
) -> None:
    """Testing to post forward messages in other chat."""
    response = await authorized_client.post(
        f"/api/chats/{message_in_chat.chat.id}/messages/forward",
        json={
            "to_chat_id": f"{direct_chat_with_users.id}",
            "messages": [
                f"{message_in_chat.id}",
            ],
        },
    )
    new_message = await get_message_by_id(
        db_session=dbsession,
        message_id=response.json()["forward_messages"][0]["id"],
    )
    assert response.status_code == status.HTTP_201_CREATED
    assert response.json() == {
        "forward_messages": [
            {
                "id": str(new_message.id),
                "user_id": str(new_message.user.id),
                "chat_id": str(new_message.chat.id),
                "message_type": new_message.message_type.value,
                "file_name": new_message.file_name,
                "file_path": new_message.file_path,
                "content": new_message.content,
                "created_at": new_message.created_at.isoformat().replace("+00:00", "Z"),
                "updated_at": new_message.updated_at.isoformat().replace("+00:00", "Z"),
                "parent_message": new_message.parent_message_id,
                "is_deleted": new_message.is_deleted,
                "reactions": new_message.reactions,
                "forwarded_message": {
                    "id": str(message_in_chat.id),
                    "user": {
                        "first_name": message_in_chat.user.first_name,
                        "last_name": message_in_chat.user.last_name,
                        "username": message_in_chat.user.username,
                        "user_image": message_in_chat.user.user_image,
                        "last_online": message_in_chat.user.last_online,
                        "is_deleted": message_in_chat.user.is_deleted,
                        "is_banned": message_in_chat.user.is_banned,
                        "id": str(message_in_chat.user.id),
                    },
                },
            },
        ],
    }


@pytest.mark.anyio
async def test_post_forwarding_messages_with_not_existent_chat(
    authorized_client: AsyncClient,
    message_in_chat: MessageFactory,
) -> None:
    """Testing to post forward messages in non-existent chat."""
    response = await authorized_client.post(
        f"/api/chats/{message_in_chat.chat.id}/messages/forward",
        json={
            "to_chat_id": f"{uuid.uuid4()}",
            "messages": [
                f"{message_in_chat.id}",
            ],
        },
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {"detail": "Chat not found"}


@pytest.mark.anyio
async def test_post_forwarding_messages_with_existent_from_chat(
    authorized_client: AsyncClient,
    message_in_chat: MessageFactory,
    direct_chat_with_users: ChatFactory,
    dbsession: AsyncSession,
    override_get_async_session: AsyncGenerator[AsyncSession, None],
) -> None:
    """Testing to post forward messages from non-existent chat."""
    response = await authorized_client.post(
        f"/api/chats/{uuid.uuid4()}/messages/forward",
        json={
            "to_chat_id": f"{direct_chat_with_users.id}",
            "messages": [
                f"{message_in_chat.id}",
            ],
        },
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {"detail": "Chat not found"}


@pytest.mark.anyio
async def test_post_forwarding_messages_with_non_part_user_in_chat(
    authorized_client: AsyncClient,
    message_in_chat: MessageFactory,
    chat: ChatFactory,
    dbsession: AsyncSession,
    override_get_async_session: AsyncGenerator[AsyncSession, None],
) -> None:
    """
    Testing to post forward messages to chat where user is not part of the chat.

    This test checks that the user cannot forward a message to a chat
    in which he does not consist
    """
    response = await authorized_client.post(
        f"/api/chats/{chat.id}/messages/forward",
        json={
            "to_chat_id": f"{message_in_chat.chat.id}",
            "messages": [
                f"{message_in_chat.id}",
            ],
        },
    )
    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert response.json() == {"detail": "User is not part of the chat"}


@pytest.mark.anyio
async def test_post_forwarding_messages_with_non_part_user_from_chat(
    authorized_client: AsyncClient,
    message_in_chat: MessageFactory,
    chat: ChatFactory,
    dbsession: AsyncSession,
    override_get_async_session: AsyncGenerator[AsyncSession, None],
) -> None:
    """
    Testing to post forward messages to chat where user is not part of the chat.

    In this test it is checked that the user does not have access to the chat,
    where does it want to forward a message from
    """
    response = await authorized_client.post(
        f"/api/chats/{chat.id}/messages/forward",
        json={
            "to_chat_id": f"{message_in_chat.chat.id}",
            "messages": [
                f"{message_in_chat.id}",
            ],
        },
    )
    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert response.json() == {
        "detail": "User is not part of the chat",
    }


@pytest.mark.anyio
async def test_post_forwarding_messages_with_non_part_message_from_chat(
    authorized_client: AsyncClient,
    message_in_chat: MessageFactory,
    message: MessageFactory,
    direct_chat_with_users: ChatFactory,
    dbsession: AsyncSession,
    override_get_async_session: AsyncGenerator[AsyncSession, None],
) -> None:
    """
    Testing to post forward messages to chat where message is not part of the chat.

    This test checks that the message being forwarded is not applicable to the chat
    from which the message originated.
    """
    response = await authorized_client.post(
        f"/api/chats/{direct_chat_with_users.id }/messages/forward",
        json={
            "to_chat_id": f"{message_in_chat.chat.id}",
            "messages": [
                f"{message.id}",
            ],
        },
    )
    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert response.json() == {
        "detail": f"Message {message.id} is not from chat {direct_chat_with_users.id}",
    }


@pytest.mark.anyio
async def test_post_forwarding_messages_with_not_existent_message(
    authorized_client: AsyncClient,
    message_in_chat: MessageFactory,
    dbsession: AsyncSession,
    override_get_async_session: AsyncGenerator[AsyncSession, None],
) -> None:
    """Testing to post forward messages from non-existent message."""
    response = await authorized_client.post(
        f"/api/chats/{message_in_chat.chat.id}/messages/forward",
        json={
            "to_chat_id": f"{message_in_chat.chat.id}",
            "messages": [
                f"{uuid.uuid4()}",
            ],
        },
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {"detail": "Message not found, it is none"}
