from pathlib import Path
from uuid import uuid4

import aiofiles
import boto3
from fastapi import UploadFile

from live_chat.settings import settings

DEFAULT_CHUNK_SIZE = 1024 * 1024 * 1  # 1 MB


class ImageSaver:
    """Saving user avatar."""

    async def save_user_image(self, uploaded_image: UploadFile) -> str | None:
        """Save an avatar sent by the user."""
        if not uploaded_image.filename:
            return None

        # Generate a unique filename with the same extension
        ext = uploaded_image.filename.split(".")[-1]
        filename = f"{uuid4().hex}.{ext}"

        # If using S3, upload to S3, else save locally
        if settings.use_s3:
            return await self._upload_image_to_s3(uploaded_image, filename)
        return await self._save_image_locally(uploaded_image, filename)

    async def _upload_image_to_s3(
        self,
        uploaded_image: UploadFile,
        filename: str,
    ) -> str:
        """Upload image to S3 bucket."""
        bucket_name = settings.aws_bucket_name
        s3_client = boto3.client(
            "s3",
            endpoint_url=settings.aws_s3_endpoint_url,
            aws_access_key_id=settings.aws_access_key_id,
            aws_secret_access_key=settings.aws_secret_access_key,
            region_name=settings.aws_region_name,
            verify=False,
        )

        s3_client.upload_fileobj(
            uploaded_image.file,
            bucket_name,
            f"avatars/{filename}",
        )

        return f"{settings.minio_url}avatars/{filename}"

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
