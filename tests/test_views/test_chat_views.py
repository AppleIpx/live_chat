from typing import AsyncGenerator

import pytest
from fastapi import status
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from tests.factories import UserFactory


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
