from typing import AsyncGenerator, List

import pytest
from fastapi import status
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from live_chat.web.api.chat.utils.get_message_by_id import get_message_by_id
from live_chat.web.api.users.utils.get_user_by_id import get_user_by_id
from live_chat.web.websocket.utils import get_chat_by_id
from tests.factories import ChatFactory, MessageFactory, UserFactory
from tests.utils import get_first_chat_from_db, get_first_user_from_db


@pytest.mark.anyio
async def test_create_direct_chat(
    authorized_client: AsyncClient,
    user: UserFactory,
    override_get_async_session: AsyncGenerator[AsyncSession, None],
    dbsession: AsyncSession,
) -> None:
    """Test create and check user's direct chat."""
    recipient = user
    response = await authorized_client.post(
        "/api/chats/create/direct/",
        json={"recipient_user_id": f"{recipient.id}"},
    )
    chat = await get_first_chat_from_db(dbsession)
    sender = await get_first_user_from_db(dbsession)
    data = response.json()
    assert response.status_code == status.HTTP_201_CREATED
    assert data == {
        "id": str(chat.id),
        "chat_type": chat.chat_type.value,
        "created_at": chat.created_at.isoformat().replace("+00:00", "Z"),
        "updated_at": chat.updated_at.isoformat().replace("+00:00", "Z"),
        "users": [
            {
                "id": str(sender.id),
                "email": sender.email,
                "is_active": sender.is_active,
                "is_superuser": sender.is_superuser,
                "is_verified": sender.is_verified,
                "first_name": sender.first_name,
                "last_name": sender.last_name,
                "username": sender.username,
                "user_image": sender.user_image,
            },
            {
                "id": str(recipient.id),
                "email": recipient.email,
                "is_active": recipient.is_active,
                "is_superuser": recipient.is_superuser,
                "is_verified": recipient.is_verified,
                "first_name": recipient.first_name,
                "last_name": recipient.last_name,
                "username": recipient.username,
                "user_image": recipient.user_image,
            },
        ],
    }


@pytest.mark.anyio
async def test_get_list_chats(
    authorized_client: AsyncClient,
    some_chats_with_users: List[ChatFactory],
    override_get_async_session: AsyncGenerator[AsyncSession, None],
    dbsession: AsyncSession,
) -> None:
    """Test get list of chats."""
    sender = await get_first_user_from_db(dbsession)
    recipient_ids = [chat.users[1].id for chat in some_chats_with_users]
    recipients = {
        str(user_id): await get_user_by_id(user_id=user_id, db_session=dbsession)
        for user_id in recipient_ids
    }
    response = await authorized_client.get("/api/chats/")
    data = response.json()
    assert response.status_code == status.HTTP_200_OK
    for chat_api in data["chats"]:
        recipient = recipients[str(chat_api["users"][1]["id"])]
        chat = await get_chat_by_id(chat_id=chat_api["id"], db_session=dbsession)
        assert chat_api == {
            "id": str(chat.id),
            "chat_type": chat.chat_type.value,
            "created_at": chat.created_at.isoformat().replace("+00:00", "Z"),
            "updated_at": chat.updated_at.isoformat().replace("+00:00", "Z"),
            "users": [
                {
                    "id": str(sender.id),
                    "email": sender.email,
                    "is_active": sender.is_active,
                    "is_superuser": sender.is_superuser,
                    "is_verified": sender.is_verified,
                    "first_name": sender.first_name,
                    "last_name": sender.last_name,
                    "username": sender.username,
                    "user_image": sender.user_image,
                },
                {
                    "id": str(recipient.id),
                    "email": recipient.email,
                    "is_active": recipient.is_active,
                    "is_superuser": recipient.is_superuser,
                    "is_verified": recipient.is_verified,
                    "first_name": recipient.first_name,
                    "last_name": recipient.last_name,
                    "username": recipient.username,
                    "user_image": recipient.user_image,
                },
            ],
        }


@pytest.mark.anyio
async def test_get_detail_chat(
    authorized_client: AsyncClient,
    chat_with_message: MessageFactory,
    override_get_async_session: AsyncGenerator[AsyncSession, None],
    dbsession: AsyncSession,
) -> None:
    """Test get detail chat."""
    chat_id = chat_with_message.chat.id
    chat = await get_chat_by_id(chat_id=chat_id, db_session=dbsession)
    sender = await get_user_by_id(user_id=chat.users[0].id, db_session=dbsession)
    recipient = await get_user_by_id(user_id=chat.users[1].id, db_session=dbsession)
    message = await get_message_by_id(
        message_id=chat_with_message.id,
        db_session=dbsession,
    )
    response = await authorized_client.get(f"api/chats/{chat_id}/")
    data = response.json()
    assert response.status_code == status.HTTP_200_OK
    assert data == {
        "id": str(chat.id),
        "chat_type": chat.chat_type.value,
        "created_at": chat.created_at.isoformat().replace("+00:00", "Z"),
        "updated_at": chat.updated_at.isoformat().replace("+00:00", "Z"),
        "users": [
            {
                "id": str(sender.id),
                "email": sender.email,
                "is_active": sender.is_active,
                "is_superuser": sender.is_superuser,
                "is_verified": sender.is_verified,
                "first_name": sender.first_name,
                "last_name": sender.last_name,
                "username": sender.username,
                "user_image": sender.user_image,
            },
            {
                "id": str(recipient.id),
                "email": recipient.email,
                "is_active": recipient.is_active,
                "is_superuser": recipient.is_superuser,
                "is_verified": recipient.is_verified,
                "first_name": recipient.first_name,
                "last_name": recipient.last_name,
                "username": recipient.username,
                "user_image": recipient.user_image,
            },
        ],
        "messages": [
            {
                "message_id": str(message.id),
                "user_id": str(sender.id),
                "chat_id": str(chat.id),
                "content": message.content,
                "created_at": message.created_at.isoformat().replace("+00:00", "Z"),
            },
        ],
    }
