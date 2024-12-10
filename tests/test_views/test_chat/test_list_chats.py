from typing import AsyncGenerator, List

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from live_chat.web.api.chat.utils import get_chat_by_id
from live_chat.web.api.users.utils import get_user_by_id
from tests.factories import ChatFactory
from tests.utils import get_first_user_from_db


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
    response = await authorized_client.get("/api/chats")

    assert response.status_code == status.HTTP_200_OK
    for chat_data in response.json()["items"]:
        recipient = recipients[str(chat_data["users"][1]["id"])]
        chat = await get_chat_by_id(chat_id=chat_data["id"], db_session=dbsession)
        assert chat_data == {
            "id": str(chat.id),
            "chat_type": chat.chat_type.value,
            "image": chat.image,
            "name": chat.name,
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
async def test_get_list_chats_with_user(
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
    response = await authorized_client.get(
        f"/api/chats?user_id_exists={recipient_ids[1]}",
    )

    assert response.status_code == status.HTTP_200_OK
    for chat_data in response.json()["items"]:
        recipient = recipients[str(chat_data["users"][1]["id"])]
        chat = await get_chat_by_id(chat_id=chat_data["id"], db_session=dbsession)
        assert chat_data == {
            "id": str(chat.id),
            "chat_type": chat.chat_type.value,
            "image": chat.image,
            "name": chat.name,
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
async def test_get_list_chats_without_auth(
    client: AsyncClient,
    any_chat_with_users: ChatFactory,
) -> None:
    """Test get list of chats without auth."""
    response = await client.get("/api/chats")
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.json() == {"detail": "Unauthorized"}
