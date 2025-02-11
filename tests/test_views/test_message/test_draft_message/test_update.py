import uuid
from typing import AsyncGenerator

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from live_chat.web.api.messages.utils import get_draft_message_by_chat_and_user_ids
from tests.factories import ChatFactory, DraftMessageFactory

json_data = {
    "message_type": "text",
    "content": "тестируем штуку",
    "file_name": None,
    "file_path": None,
}


@pytest.mark.anyio
async def test_update_draft_message(
    authorized_client: AsyncClient,
    draft_message: DraftMessageFactory,
    override_get_async_session: AsyncGenerator[AsyncSession, None],
    dbsession: AsyncSession,
) -> None:
    """Test update draft message."""
    response = await authorized_client.put(
        f"api/chats/{draft_message.chat_id}/draft-message",
        json=json_data,
    )
    draft_message = await get_draft_message_by_chat_and_user_ids(
        db_session=dbsession,
        chat_id=draft_message.chat_id,
        user_id=draft_message.user_id,
    )
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {
        "id": str(draft_message.id),
        "user_id": str(draft_message.user_id),
        "chat_id": str(draft_message.chat_id),
        "message_type": draft_message.message_type.value,
        "file_name": draft_message.file_name,
        "file_path": draft_message.file_path,
        "content": draft_message.content,
        "created_at": draft_message.created_at.isoformat().replace("+00:00", "Z"),
        "updated_at": draft_message.updated_at.isoformat().replace("+00:00", "Z"),
        "is_deleted": draft_message.is_deleted,
    }


@pytest.mark.anyio
async def test_update_draft_message_non_participant(
    authorized_client: AsyncClient,
    chat: ChatFactory,
    override_get_async_session: AsyncGenerator[AsyncSession, None],
    dbsession: AsyncSession,
) -> None:
    """Test update draft message non participant in chat."""
    response = await authorized_client.put(
        f"api/chats/{chat.id}/draft-message",
        json=json_data,
    )
    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert response.json() == {"detail": "User is not part of the chat"}


@pytest.mark.anyio
async def test_update_draft_message_with_non_existent_chat(
    authorized_client: AsyncClient,
    override_get_async_session: AsyncGenerator[AsyncSession, None],
    dbsession: AsyncSession,
) -> None:
    """Test update draft message non non existent chat."""
    response = await authorized_client.put(
        f"api/chats/{uuid.uuid4()}/draft-message",
        json=json_data,
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {"detail": "Chat not found"}


@pytest.mark.anyio
async def test_update_non_existent_draft_message(
    authorized_client: AsyncClient,
    any_chat_with_users: ChatFactory,
    override_get_async_session: AsyncGenerator[AsyncSession, None],
    dbsession: AsyncSession,
) -> None:
    """Test update draft message non existent draft message."""
    response = await authorized_client.put(
        f"api/chats/{any_chat_with_users.id}/draft-message",
        json=json_data,
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {"detail": "Draft message not found"}
