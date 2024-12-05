import uuid
from typing import AsyncGenerator

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from live_chat.web.api.chat.utils import get_deleted_message_by_id, get_message_by_id
from tests.factories import DeletedMessageFactory, MessageFactory, UserFactory


@pytest.mark.anyio
async def test_recover_deleted_message(
    authorized_client: AsyncClient,
    deleted_message_in_chat: DeletedMessageFactory,
    override_get_async_session: AsyncGenerator[AsyncSession, None],
    dbsession: AsyncSession,
) -> None:
    """Testing recover_deleted_message."""
    chat = deleted_message_in_chat.chat
    response = await authorized_client.post(
        f"/api/chats/{chat.id}/messages/{deleted_message_in_chat.id}/recover",
    )
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {"detail": "Сообщение восстановлено"}


@pytest.mark.anyio
async def test_entry_deleted_message(
    authorized_client: AsyncClient,
    deleted_message_in_chat: DeletedMessageFactory,
    override_get_async_session: AsyncGenerator[AsyncSession, None],
    dbsession: AsyncSession,
) -> None:
    """Testing deleting an entry in DeleteMesage when restoring a message."""
    chat = deleted_message_in_chat.chat
    response = await authorized_client.post(
        f"/api/chats/{chat.id}/messages/{deleted_message_in_chat.id}/recover",
    )
    deleted_mesage_db = await get_deleted_message_by_id(
        db_session=dbsession,
        deleted_message_id=deleted_message_in_chat.id,
    )
    assert response.status_code == status.HTTP_200_OK
    assert deleted_mesage_db is None


@pytest.mark.anyio
async def test_change_status_in_orig_message(
    authorized_client: AsyncClient,
    deleted_message_in_chat: DeletedMessageFactory,
    override_get_async_session: AsyncGenerator[AsyncSession, None],
    dbsession: AsyncSession,
) -> None:
    """Testing change_status_in_original_message on recover_deleted_message."""
    chat = deleted_message_in_chat.chat
    response = await authorized_client.post(
        f"/api/chats/{chat.id}/messages/{deleted_message_in_chat.id}/recover",
    )
    orig_message = await get_message_by_id(
        db_session=dbsession,
        message_id=deleted_message_in_chat.original_message_id,
    )
    assert response.status_code == status.HTTP_200_OK
    assert orig_message is not None
    assert orig_message.is_deleted is False


@pytest.mark.anyio
async def test_invalid_deleted_message(
    authorized_client: AsyncClient,
    message_in_chat: MessageFactory,
    override_get_async_session: AsyncGenerator[AsyncSession, None],
    dbsession: AsyncSession,
) -> None:
    """
    Testing the error.

    That occurs when restoring a message if there is no entry
    about it in the DeletedMessage
    """
    chat = message_in_chat.chat
    response = await authorized_client.post(
        f"/api/chats/{chat.id}/messages/{message_in_chat.id}/recover",
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {"detail": "Instance is not deleted message"}


@pytest.mark.anyio
async def test_recover_message_with_failed_chat(
    authorized_client: AsyncClient,
    deleted_message_in_chat: DeletedMessageFactory,
    override_get_async_session: AsyncGenerator[AsyncSession, None],
    dbsession: AsyncSession,
) -> None:
    """Testing recovery of a message indicating the wrong chat."""
    response = await authorized_client.post(
        f"/api/chats/{uuid.uuid4()}/messages/{deleted_message_in_chat.id}/recover",
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {"detail": "Chat not found"}


@pytest.mark.anyio
async def test_recover_message_with_failed_message(
    authorized_client: AsyncClient,
    deleted_message_in_chat: DeletedMessageFactory,
    override_get_async_session: AsyncGenerator[AsyncSession, None],
    dbsession: AsyncSession,
) -> None:
    """Testing recovery of a message indicating the wrong message."""
    response = await authorized_client.post(
        f"/api/chats/{deleted_message_in_chat.chat.id}/messages/{uuid.uuid4()}/recover",
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {"detail": "Message not found"}


@pytest.mark.anyio
async def test_recover_message_for_non_member(
    authorized_client: AsyncClient,
    deleted_message_in_chat: DeletedMessageFactory,
    override_get_async_session: AsyncGenerator[AsyncSession, None],
    dbsession: AsyncSession,
) -> None:
    """Test for recover a message by a user who is not a member of the group."""
    del deleted_message_in_chat.chat.users[0]
    chat = deleted_message_in_chat.chat
    response = await authorized_client.post(
        f"/api/chats/{chat.id}/messages/{deleted_message_in_chat.id}/recover",
    )
    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert response.json() == {"detail": "User is not part of the chat"}


@pytest.mark.anyio
async def test_recover_message_with_non_author(
    authorized_client: AsyncClient,
    deleted_message_in_chat: DeletedMessageFactory,
    user: UserFactory,
    override_get_async_session: AsyncGenerator[AsyncSession, None],
    dbsession: AsyncSession,
) -> None:
    """Test for recover a message by a user who is not a author message."""
    deleted_message_in_chat.user = user
    chat = deleted_message_in_chat.chat
    response = await authorized_client.post(
        f"/api/chats/{chat.id}/messages/{deleted_message_in_chat.id}/recover",
    )
    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert response.json() == {"detail": "User is not the author of this message"}
