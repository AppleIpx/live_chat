from typing import AsyncGenerator

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from live_chat.web.api.chat.utils import get_chat_by_id
from live_chat.web.api.users.utils.get_user_by_id import get_user_by_id
from tests.factories import ChatFactory, MessageFactory


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
    response = await authorized_client.get(f"api/chats/{chat_id}/")
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {
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
async def test_get_detail_chat_without_auth(
    client: AsyncClient,
    any_chat_with_users: ChatFactory,
) -> None:
    """Test get detail chat without auth."""
    response = await client.get(f"api/chats/{any_chat_with_users.id}/")
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.json() == {"detail": "Unauthorized"}
