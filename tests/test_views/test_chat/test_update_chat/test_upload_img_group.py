import json
import uuid
from typing import AsyncGenerator
from unittest.mock import AsyncMock, patch

import pytest
from fastapi import UploadFile
from fastapi.encoders import jsonable_encoder
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from live_chat.web.api.messages.constants import REDIS_CHANNEL_PREFIX
from live_chat.web.utils.s3_client import S3Client
from tests.factories import ChatFactory


@pytest.mark.anyio
async def test_upload_img_group(
    authorized_client: AsyncClient,
    group_chat_with_users: ChatFactory,
    fake_image: UploadFile,
    override_get_async_session: AsyncGenerator[AsyncSession, None],
    mocked_publish_message: AsyncMock,
    upload_mock: AsyncMock,
) -> None:
    """Testing upload image group."""
    chat_id = group_chat_with_users.id
    recipient = group_chat_with_users.users[-1]
    target_channel = f"{REDIS_CHANNEL_PREFIX}:{chat_id!s}:{recipient.id!s}"
    event_data = jsonable_encoder({"image_url": upload_mock.return_value})
    response = await authorized_client.patch(
        f"/api/chats/{chat_id}/upload-image",
        files={
            "uploaded_image": (
                fake_image.filename,
                fake_image.file,
                fake_image.content_type,
            ),
        },
    )

    mocked_publish_message.assert_called_with(
        json.dumps({"event": "update_image_group", "data": json.dumps(event_data)}),
        channel=target_channel,
    )
    upload_mock.assert_called_once()
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {"image_url": upload_mock.return_value}


@pytest.mark.anyio
async def test_upload_img_group_with_invalid_extension(
    authorized_client: AsyncClient,
    group_chat_with_users: ChatFactory,
    fake_image: UploadFile,
    mocked_publish_message: AsyncMock,
    override_get_async_session: AsyncGenerator[AsyncSession, None],
    dbsession: AsyncSession,
) -> None:
    """Testing upload image group with invalid image extension."""
    fake_image.filename = "invalid_image.xlsx"
    response = await authorized_client.patch(
        f"/api/chats/{group_chat_with_users.id}/upload-image",
        files={
            "uploaded_image": (
                fake_image.filename,
                fake_image.file,
            ),
        },
    )

    mocked_publish_message.assert_not_called()
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json() == {
        "detail": "It is incorrect image extension. Required: ('png', 'jpg', 'jpeg')",
    }


@pytest.mark.anyio
async def test_upload_img_in_invalid_group(
    authorized_client: AsyncClient,
    fake_image: UploadFile,
    mocked_publish_message: AsyncMock,
    override_get_async_session: AsyncGenerator[AsyncSession, None],
    dbsession: AsyncSession,
    upload_mock: AsyncMock,
) -> None:
    """Testing upload image group with invalid group."""
    response = await authorized_client.patch(
        f"/api/chats/{uuid.uuid4()}/upload-image",
        files={
            "uploaded_image": (
                fake_image.filename,
                fake_image.file,
            ),
        },
    )

    mocked_publish_message.assert_not_called()
    upload_mock.assert_not_called()
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {"detail": "Chat not found"}


@pytest.mark.anyio
async def test_upload_img_in_direct_chat(
    authorized_client: AsyncClient,
    direct_chat_with_users: ChatFactory,
    fake_image: UploadFile,
    override_get_async_session: AsyncGenerator[AsyncSession, None],
    mocked_publish_message: AsyncMock,
    dbsession: AsyncSession,
) -> None:
    """Testing upload image group in direct chat."""
    with patch.object(S3Client, "upload_file"):
        response = await authorized_client.patch(
            f"/api/chats/{direct_chat_with_users.id}/upload-image",
            files={"uploaded_image": (fake_image.filename, fake_image.file)},
        )

    mocked_publish_message.assert_not_called()
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json() == {"detail": "You can't specify a photo for direct chat"}


@pytest.mark.anyio
async def test_upload_img_in_group_without_img(
    authorized_client: AsyncClient,
    group_chat_with_users: ChatFactory,
    override_get_async_session: AsyncGenerator[AsyncSession, None],
    mocked_publish_message: AsyncMock,
    dbsession: AsyncSession,
) -> None:
    """Testing upload image group with no image."""
    response = await authorized_client.patch(
        f"/api/chats/{group_chat_with_users.id}/upload-image",
    )

    mocked_publish_message.assert_not_called()
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    assert response.json() == {
        "detail": [
            {
                "input": None,
                "loc": [
                    "body",
                    "uploaded_image",
                ],
                "msg": "Field required",
                "type": "missing",
            },
        ],
    }
