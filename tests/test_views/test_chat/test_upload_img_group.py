import uuid
from typing import AsyncGenerator
from unittest.mock import patch

import pytest
from fastapi import UploadFile
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from live_chat.settings import settings
from live_chat.web.s3_client import S3Client
from tests.factories import ChatFactory


@pytest.mark.anyio
async def test_upload_img_group(
    authorized_client: AsyncClient,
    group_chat_with_users: ChatFactory,
    fake_image: UploadFile,
    override_get_async_session: AsyncGenerator[AsyncSession, None],
) -> None:
    """Testing upload image group."""
    with patch.object(
        S3Client,
        "upload_file",
        return_value=f"{settings.minio_url}group_images/{group_chat_with_users.id}.png",
    ) as mock_upload:
        response = await authorized_client.patch(
            f"/api/chats/{group_chat_with_users.id}/upload-image",
            files={
                "uploaded_image": (
                    fake_image.filename,
                    fake_image.file,
                    fake_image.content_type,
                ),
            },
        )

    assert response.status_code == 200
    assert response.json() == {
        "image_url": f"{settings.minio_url}group_images/{group_chat_with_users.id}.png",
    }
    mock_upload.assert_called_once()


@pytest.mark.anyio
async def test_upload_img_group_with_invalid_extension(
    authorized_client: AsyncClient,
    group_chat_with_users: ChatFactory,
    fake_image: UploadFile,
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
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json() == {
        "detail": "It is incorrect image extension. Required: ('png', 'jpg', 'jpeg')",
    }


@pytest.mark.anyio
async def test_upload_img_in_invalid_group(
    authorized_client: AsyncClient,
    fake_image: UploadFile,
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
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {"detail": "Group not found"}


@pytest.mark.anyio
async def test_upload_img_in_direct_chat(
    authorized_client: AsyncClient,
    direct_chat_with_users: ChatFactory,
    fake_image: UploadFile,
    override_get_async_session: AsyncGenerator[AsyncSession, None],
) -> None:
    """Testing upload image group in direct chat."""
    response = await authorized_client.patch(
        f"/api/chats/{direct_chat_with_users.id}/upload-image",
        files={
            "uploaded_image": (
                fake_image.filename,
                fake_image.file,
            ),
        },
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json() == {"detail": "You can't specify a photo for direct chat"}


@pytest.mark.anyio
async def test_upload_img_in_group_without_img(
    authorized_client: AsyncClient,
    group_chat_with_users: ChatFactory,
) -> None:
    """Testing upload image group with no image."""
    response = await authorized_client.patch(
        f"/api/chats/{group_chat_with_users.id}/upload-image",
    )
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
