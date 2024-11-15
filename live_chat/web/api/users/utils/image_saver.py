from pathlib import Path
from typing import Final
from uuid import UUID

import aiofiles
from fastapi import HTTPException, UploadFile
from starlette import status

from live_chat.settings import settings
from live_chat.web.s3_client import s3_client

DEFAULT_CHUNK_SIZE: Final = 1024 * 1024 * 1  # 1 MB
SUPPORTED_AVATAR_EXTENSIONS: Final = ("png", "jpg", "jpeg")


class ImageSaver:
    """Saving user avatar."""

    def __init__(self, user_id: UUID) -> None:
        self.user_id = user_id

    async def save_user_image(self, uploaded_image: UploadFile) -> str | None:
        """Save an avatar sent by the user."""
        if not uploaded_image.filename:
            return None

        # Generate a unique filename with the same extension
        ext = uploaded_image.filename.split(".")[-1]
        if ext not in SUPPORTED_AVATAR_EXTENSIONS:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"It is incorrect image extension. "
                f"Required: {SUPPORTED_AVATAR_EXTENSIONS}",
            )
        filename = f"{self.user_id}.{ext}"

        # If using S3, upload to S3, else save locally
        if settings.use_s3:
            return await s3_client.upload_file(
                uploaded_image.file,
                f"avatars/{filename}",
            )
        return await self._save_image_locally(uploaded_image, filename)

    async def _save_image_locally(
        self,
        uploaded_image: UploadFile,
        filename: str,
    ) -> str:
        """Save image locally."""
        folder_path = Path(settings.media_url_prefix)
        folder_path.mkdir(parents=True, exist_ok=True)
        file_path = folder_path / filename

        # Save image locally in chunks
        async with aiofiles.open(file_path, "wb") as f:
            while chunk := await uploaded_image.read(DEFAULT_CHUNK_SIZE):
                await f.write(chunk)

        return str(file_path)
