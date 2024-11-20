from typing import AsyncGenerator

import pytest
from fastapi import status
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from tests.factories import ChatFactory, MessageFactory, UserFactory


@pytest.mark.anyio
class TestChatViews:
    """Test chat views."""

    async def test_create_direct_chat(
        self,
        user: UserFactory,
        authorized_client: AsyncClient,
        override_get_async_session: AsyncGenerator[AsyncSession, None],
    ) -> None:
        """Test create and check user's direct chat."""
        payload = {
            "recipient_user_id": f"{user.id}",
        }
        response = await authorized_client.post(
            "/api/chats/create/direct/",
            json=payload,
        )
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert len(data["users"]) == 2
        assert (
            data["users"][0]["email"] == "user@example.com"
            and str(user.id) == data["users"][1]["id"]
        )
        assert "direct" in data["chat_type"]

    async def test_get_list_chats(
        self,
        authorized_client: AsyncClient,
        some_chats_with_users: ChatFactory,
        override_get_async_session: AsyncGenerator[AsyncSession, None],
    ) -> None:
        """Test get list of chats."""
        response = await authorized_client.get("/api/chats/")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data["chats"]) == len(some_chats_with_users)

    async def test_get_detail_chat(
        self,
        authorized_client: AsyncClient,
        chat_with_message: MessageFactory,
        override_get_async_session: AsyncGenerator[AsyncSession, None],
    ) -> None:
        """Test get detail chat."""
        chat = chat_with_message.chat
        response = await authorized_client.get(f"api/chats/{chat.id}/")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        sender = str(chat.users[0].id)
        recipient = str(chat.users[1].id)
        assert sender == data["users"][0]["id"] and recipient == data["users"][1]["id"]
        assert "messages" in data
        assert str(chat.id) == str(data["messages"][0]["chat_id"])
        assert sender == str(data["messages"][0]["user_id"])
