import uuid
from typing import AsyncGenerator

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from live_chat.web.api.messages.utils import get_draft_message_by_chat_and_user_ids
from tests.factories import ChatFactory
from tests.utils import get_first_user_from_db


@pytest.mark.anyio
async def test_create_draft_message(
    authorized_client: AsyncClient,
    any_chat_with_users: ChatFactory,
    override_get_async_session: AsyncGenerator[AsyncSession, None],
    dbsession: AsyncSession,
) -> None:
    """Test create draft message."""
    chat_id = any_chat_with_users.id
    response = await authorized_client.post(
        f"api/chats/{chat_id}/draft-message",
        json={
            "message_type": "text",
            "content": "privet",
            "file_name": None,
            "file_path": None,
        },
    )
    auth_user = await get_first_user_from_db(db_session=dbsession)
    draft_message = await get_draft_message_by_chat_and_user_ids(
        db_session=dbsession,
        chat_id=chat_id,
        user_id=auth_user.id,
    )
    assert response.status_code == status.HTTP_201_CREATED
    assert response.json() == {
        "id": str(draft_message.id),
        "user_id": str(auth_user.id),
        "chat_id": str(chat_id),
        "message_type": draft_message.message_type.value,
        "file_name": draft_message.file_name,
        "file_path": draft_message.file_path,
        "content": draft_message.content,
        "created_at": draft_message.created_at.isoformat().replace("+00:00", "Z"),
        "updated_at": draft_message.updated_at.isoformat().replace("+00:00", "Z"),
        "is_deleted": draft_message.is_deleted,
    }


@pytest.mark.anyio
async def test_create_draft_message_with_invalid_chat(
    authorized_client: AsyncClient,
    override_get_async_session: AsyncGenerator[AsyncSession, None],
    dbsession: AsyncSession,
) -> None:
    """Test create draft message with invalid chat."""
    response = await authorized_client.post(
        f"api/chats/{uuid.uuid4()}/draft-message",
        json={
            "message_type": "text",
            "content": "privet",
            "file_name": None,
            "file_path": None,
        },
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {"detail": "Chat not found"}


@pytest.mark.anyio
async def test_create_draft_message_with_deleted_user(
    authorized_deleted_client: AsyncClient,
    any_chat_with_users: ChatFactory,
    override_get_async_session: AsyncGenerator[AsyncSession, None],
    dbsession: AsyncSession,
) -> None:
    """Test create draft message with deleted user."""
    response = await authorized_deleted_client.post(
        f"api/chats/{any_chat_with_users.id}/draft-message",
        json={
            "message_type": "text",
            "content": "privet",
            "file_name": None,
            "file_path": None,
        },
    )
    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert response.json() == {"detail": "You are deleted."}


@pytest.mark.anyio
async def test_create_draft_message_without_auth(
    client: AsyncClient,
    any_chat_with_users: ChatFactory,
    override_get_async_session: AsyncGenerator[AsyncSession, None],
    dbsession: AsyncSession,
) -> None:
    """Test create draft message without auth."""
    response = await client.post(
        f"api/chats/{any_chat_with_users.id}/draft-message",
        json={
            "message_type": "text",
            "content": "privet",
            "file_name": None,
            "file_path": None,
        },
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.json() == {"detail": "Unauthorized"}


@pytest.mark.anyio
async def test_create_draft_message_non_participant(
    authorized_client: AsyncClient,
    chat: ChatFactory,
    override_get_async_session: AsyncGenerator[AsyncSession, None],
    dbsession: AsyncSession,
) -> None:
    """Test create draft message non-participant in chat."""
    response = await authorized_client.post(f"api/chats/{chat.id}/draft-message")
    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert response.json() == {"detail": "User is not part of the chat"}
