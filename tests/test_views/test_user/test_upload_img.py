from typing import AsyncGenerator
from unittest.mock import patch

import pytest
from fastapi import UploadFile
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from live_chat.settings import settings
from live_chat.web.utils.s3_client import S3Client
from tests.utils import get_first_user_from_db


@pytest.mark.anyio
async def test_upload_img(
    authorized_client: AsyncClient,
    fake_image: UploadFile,
    override_get_async_session: AsyncGenerator[AsyncSession, None],
    dbsession: AsyncSession,
) -> None:
    """Testing upload image user."""
    auth_user = await get_first_user_from_db(dbsession)
    with patch.object(
        S3Client,
        "upload_file",
        return_value=f"{settings.minio_url}avatars/{auth_user.id}.png",
    ) as mock_upload:
        response = await authorized_client.patch(
            "/api/users/me/upload-image",
            files={
                "uploaded_image": (
                    fake_image.filename,
                    fake_image.file,
                    fake_image.content_type,
                ),
            },
        )

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {
        "image_url": f"{settings.minio_url}avatars/{auth_user.id}.png",
    }
    mock_upload.assert_called_once()


@pytest.mark.anyio
async def test_upload_incorrect_img(
    authorized_client: AsyncClient,
    fake_image: UploadFile,
) -> None:
    """Testing upload failed image user."""
    fake_image.filename = "invalid_image.xlsx"
    response = await authorized_client.patch(
        "/api/users/me/upload-image",
        files={
            "uploaded_image": (
                fake_image.filename,
                fake_image.file,
                fake_image.content_type,
            ),
        },
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json() == {
        "detail": "It is incorrect image extension. Required: ('png', 'jpg', 'jpeg')",
    }


@pytest.mark.anyio
async def test_upload_img_without_img(
    authorized_client: AsyncClient,
    fake_image: UploadFile,
) -> None:
    """Testing upload img without image."""
    response = await authorized_client.patch(
        "/api/users/me/upload-image",
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
