from typing import AsyncGenerator, List

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from live_chat.web.api.chat.utils import get_chat_by_id
from live_chat.web.api.users.utils import get_user_by_id
from tests.factories import DeletedMessageFactory
from tests.utils import get_first_user_from_db


@pytest.mark.anyio
async def test_get_chats_deleted(
    authorized_client: AsyncClient,
    some_deleted_messages: List[DeletedMessageFactory],
    override_get_async_session: AsyncGenerator[AsyncSession, None],
    dbsession: AsyncSession,
) -> None:
    """Testing the receipt of chats that have deleted messages."""
    response = await authorized_client.get("/api/chats/deleted")
    sender = await get_first_user_from_db(dbsession)
    recipient_ids = [message.chat.users[1].id for message in some_deleted_messages]
    recipients = {
        str(user_id): await get_user_by_id(user_id=user_id, db_session=dbsession)
        for user_id in recipient_ids
    }
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["total"] is None
    assert response.json()["current_page"] == "Pg%3D%3D"
    assert response.json()["current_page_backwards"] == "PA%3D%3D"
    assert response.json()["previous_page"] is None
    assert response.json()["next_page"] is None
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
                    "is_deleted": sender.is_deleted,
                    "is_banned": sender.is_banned,
                    "first_name": sender.first_name,
                    "last_name": sender.last_name,
                    "last_online": (
                        sender.last_online.isoformat().replace("+00:00", "Z")
                        if sender.last_online
                        else None
                    ),
                    "username": sender.username,
                    "user_image": sender.user_image,
                },
                {
                    "id": str(recipient.id),
                    "is_deleted": recipient.is_deleted,
                    "is_banned": recipient.is_banned,
                    "first_name": recipient.first_name,
                    "last_name": recipient.last_name,
                    "last_online": recipient.last_online.isoformat().replace(
                        "+00:00",
                        "Z",
                    ),
                    "username": recipient.username,
                    "user_image": recipient.user_image,
                },
            ],
        }


@pytest.mark.anyio
async def test_get_deleted_chats_by_deleted_user(
    authorized_deleted_client: AsyncClient,
) -> None:
    """Testing get deleted chats by a deleted user."""
    response = await authorized_deleted_client.get("/api/chats/deleted")
    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert response.json() == {"detail": "You are deleted."}


@pytest.mark.anyio
async def test_get_deleted_chats_by_banned_user(
    authorized_banned_client: AsyncClient,
) -> None:
    """Testing get deleted chats by a banned user."""
    response = await authorized_banned_client.get("/api/chats/banned")
    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert response.json() == {
        "detail": {
            "reason": None,
            "status": "banned",
        },
    }
