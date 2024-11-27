from typing import AsyncGenerator

import pytest
from fastapi import UploadFile
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from live_chat.settings import settings
from tests.factories import ChatFactory


@pytest.mark.anyio
async def test_upload_img_group(
    authorized_client: AsyncClient,
    group_chat_with_users: ChatFactory,
    fake_image: UploadFile,
    override_get_async_session: AsyncGenerator[AsyncSession, None],
    dbsession: AsyncSession,
) -> None:
    """Testing upload image group."""
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
