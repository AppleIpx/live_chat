import uuid
from typing import AsyncGenerator

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from live_chat.web.api.messages.utils import get_draft_message_by_chat_and_user_ids
from tests.factories import ChatFactory, DraftMessageFactory
from tests.utils import get_first_user_from_db


@pytest.mark.anyio
async def test_delete_draft_message(
    authorized_client: AsyncClient,
    draft_message: DraftMessageFactory,
    override_get_async_session: AsyncGenerator[AsyncSession, None],
    dbsession: AsyncSession,
) -> None:
    """Test delete draft message."""
    response = await authorized_client.delete(
        f"api/chats/{draft_message.chat_id}/draft-message",
    )
    auth_user = await get_first_user_from_db(db_session=dbsession)
    draft_message_db = await get_draft_message_by_chat_and_user_ids(
        db_session=dbsession,
        chat_id=draft_message.chat_id,
        user_id=auth_user.id,
    )
    assert response.status_code == status.HTTP_204_NO_CONTENT
    assert draft_message_db is None


@pytest.mark.anyio
async def test_delete_draft_message_without_auth(
    client: AsyncClient,
    chat: ChatFactory,
    override_get_async_session: AsyncGenerator[AsyncSession, None],
    dbsession: AsyncSession,
) -> None:
    """Test delete draft message without auth."""
    response = await client.delete(f"api/chats/{chat.id}/draft-message")
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.json() == {"detail": "Unauthorized"}


@pytest.mark.anyio
async def test_delete_non_existent_draft_message(
    authorized_client: AsyncClient,
    any_chat_with_users: ChatFactory,
    override_get_async_session: AsyncGenerator[AsyncSession, None],
    dbsession: AsyncSession,
) -> None:
    """Test delete non existent draft message."""
    response = await authorized_client.delete(
        f"api/chats/{any_chat_with_users.id}/draft-message",
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {"detail": "Draft message not found"}


@pytest.mark.anyio
async def test_delete_draft_message_with_non_existent_chat(
    authorized_client: AsyncClient,
    override_get_async_session: AsyncGenerator[AsyncSession, None],
    dbsession: AsyncSession,
) -> None:
    """Test delete draft message in non existent chat."""
    response = await authorized_client.delete(
        f"api/chats/{uuid.uuid4()}/draft-message",
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {"detail": "Chat not found"}


@pytest.mark.anyio
async def test_delete_draft_message_non_participant(
    authorized_client: AsyncClient,
    chat: ChatFactory,
    override_get_async_session: AsyncGenerator[AsyncSession, None],
    dbsession: AsyncSession,
) -> None:
    """Test delete draft message non participant in chat."""
    response = await authorized_client.delete(f"api/chats/{chat.id}/draft-message")
    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert response.json() == {"detail": "User is not part of the chat"}
