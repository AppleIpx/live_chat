import uuid
from typing import AsyncGenerator
from unittest.mock import AsyncMock

import pytest
from fastapi import UploadFile
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from tests.factories import ChatFactory


@pytest.mark.anyio
async def test_upload_attachments(
    authorized_client: AsyncClient,
    fake_image: UploadFile,
    direct_chat_with_users: ChatFactory,
    override_get_async_session: AsyncGenerator[AsyncSession, None],
    upload_chat_attachments_mock: AsyncMock,
) -> None:
    """Testing upload chat attachments."""
    response = await authorized_client.post(
        f"/api/chats/{direct_chat_with_users.id}/upload-attachments",
        files={
            "uploaded_file": (
                fake_image.filename,
                fake_image.file,
                fake_image.content_type,
            ),
        },
    )

    upload_chat_attachments_mock.assert_called_once()
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {
        "file_name": upload_chat_attachments_mock.return_value.split("/")[-1],
        "file_path": upload_chat_attachments_mock.return_value,
    }


@pytest.mark.anyio
async def test_upload_attachments_unauthorized_user(
    client: AsyncClient,
    fake_image: UploadFile,
    direct_chat_with_users: ChatFactory,
    override_get_async_session: AsyncGenerator[AsyncSession, None],
    upload_chat_attachments_mock: AsyncMock,
) -> None:
    """Testing upload chat attachments from unauthorized user."""
    response = await client.post(
        f"/api/chats/{direct_chat_with_users.id}/upload-attachments",
        files={
            "uploaded_file": (
                fake_image.filename,
                fake_image.file,
                fake_image.content_type,
            ),
        },
    )

    upload_chat_attachments_mock.assert_not_called()
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.json() == {"detail": "Unauthorized"}


@pytest.mark.anyio
async def test_upload_attachments_nonexistent_chat(
    authorized_client: AsyncClient,
    fake_image: UploadFile,
    mocked_publish_message: AsyncMock,
    override_get_async_session: AsyncGenerator[AsyncSession, None],
    dbsession: AsyncSession,
    upload_chat_attachments_mock: AsyncMock,
) -> None:
    """Testing upload chat attachments with nonexistent chat."""
    response = await authorized_client.post(
        f"/api/chats/{uuid.uuid4()}/upload-attachments",
        files={
            "uploaded_file": (
                fake_image.filename,
                fake_image.file,
                fake_image.content_type,
            ),
        },
    )

    upload_chat_attachments_mock.assert_not_called()
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {"detail": "Chat not found"}


@pytest.mark.anyio
async def test_upload_attachments_nonexistent_user(
    authorized_client: AsyncClient,
    fake_image: UploadFile,
    chat: ChatFactory,
    override_get_async_session: AsyncGenerator[AsyncSession, None],
    upload_chat_attachments_mock: AsyncMock,
) -> None:
    """Testing upload chat attachments from nonexistent user."""
    response = await authorized_client.post(
        f"/api/chats/{chat.id}/upload-attachments",
        files={
            "uploaded_file": (
                fake_image.filename,
                fake_image.file,
                fake_image.content_type,
            ),
        },
    )

    upload_chat_attachments_mock.assert_not_called()
    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert response.json() == {"detail": "User is not part of the chat"}


@pytest.mark.anyio
async def test_upload_attachments_by_deleted_user(
    authorized_deleted_client: AsyncClient,
    fake_image: UploadFile,
    chat: ChatFactory,
    override_get_async_session: AsyncGenerator[AsyncSession, None],
    dbsession: AsyncSession,
    upload_chat_attachments_mock: AsyncMock,
) -> None:
    """Testing upload attachments by a deleted user."""
    response = await authorized_deleted_client.post(
        f"/api/chats/{chat.id}/upload-attachments",
        files={
            "uploaded_file": (
                fake_image.filename,
                fake_image.file,
                fake_image.content_type,
            ),
        },
    )
    upload_chat_attachments_mock.assert_not_called()
    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert response.json() == {"detail": "You are deleted."}
