import uuid
from typing import AsyncGenerator, List

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from tests.factories import DeletedMessageFactory


@pytest.mark.anyio
async def test_get_deleted_message_in_chat(
    authorized_client: AsyncClient,
    deleted_message_in_chat: DeletedMessageFactory,
    some_deleted_messages: List[DeletedMessageFactory],
    override_get_async_session: AsyncGenerator[AsyncSession, None],
    dbsession: AsyncSession,
) -> None:
    """Testing the receipt of deleted messages in a specific chat."""
    response = await authorized_client.get(
        f"/api/chats/{deleted_message_in_chat.chat_id}/deleted-messages",
    )
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {
        "items": [
            {
                "id": str(deleted_message_in_chat.id),
                "user_id": str(deleted_message_in_chat.user_id),
                "chat_id": str(deleted_message_in_chat.chat_id),
                "content": deleted_message_in_chat.content,
                "message_type": deleted_message_in_chat.message_type.value,
                "file_name": deleted_message_in_chat.file_name,
                "file_path": deleted_message_in_chat.file_path,
                "created_at": deleted_message_in_chat.created_at.isoformat().replace(
                    "+00:00",
                    "Z",
                ),
                "updated_at": deleted_message_in_chat.updated_at.isoformat().replace(
                    "+00:00",
                    "Z",
                ),
                "is_deleted": True,
            },
        ],
        "total": None,
        "current_page": "Pg%3D%3D",
        "current_page_backwards": "PA%3D%3D",
        "previous_page": None,
        "next_page": None,
    }


@pytest.mark.anyio
async def test_get_deleted_message_in_failed_chat(
    authorized_client: AsyncClient,
    deleted_message_in_chat: DeletedMessageFactory,
    override_get_async_session: AsyncGenerator[AsyncSession, None],
    dbsession: AsyncSession,
) -> None:
    """Testing get a deleted message indicating the wrong chat."""
    response = await authorized_client.get(
        f"/api/chats/{uuid.uuid4()}/deleted-messages",
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {"detail": "Chat not found"}


@pytest.mark.anyio
async def test_get_deleted_message_for_non_member(
    authorized_client: AsyncClient,
    deleted_message_in_chat: DeletedMessageFactory,
    override_get_async_session: AsyncGenerator[AsyncSession, None],
    dbsession: AsyncSession,
) -> None:
    """Test for getting a deleted message by a user who is not a member of the group."""
    del deleted_message_in_chat.chat.users[0]
    response = await authorized_client.get(
        f"/api/chats/{deleted_message_in_chat.chat_id}/deleted-messages",
    )
    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert response.json() == {"detail": "User is not part of the chat"}
