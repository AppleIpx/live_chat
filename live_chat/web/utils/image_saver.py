import uuid
from typing import Final
from uuid import UUID

from fastapi import HTTPException, UploadFile
from starlette import status

from live_chat.settings import settings
from live_chat.web.enums import UploadFileDirectoryEnum
from live_chat.web.utils.s3_client import s3_client

DEFAULT_CHUNK_SIZE: Final = 1024 * 1024 * 1  # 1 MB
SUPPORTED_AVATAR_EXTENSIONS: Final = ("png", "jpg", "jpeg")


class FileSaver:
    """Saving files in s3."""

    def __init__(self, object_id: UUID | None = None) -> None:
        self.object_id = object_id if object_id else uuid.uuid4()

    async def save_file(
        self,
        uploaded_file: UploadFile,
        directory: UploadFileDirectoryEnum | str,
    ) -> str | None:
        """Save an avatar sent by the user."""
        if not uploaded_file.filename:
            return None

        ext = uploaded_file.filename.split(".")[-1]
        if (
            directory
            in frozenset(
                [
                    UploadFileDirectoryEnum.avatars,
                    UploadFileDirectoryEnum.group_images,
                ],
            )
            and ext not in SUPPORTED_AVATAR_EXTENSIONS
        ):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"It is incorrect image extension. "
                f"Required: {SUPPORTED_AVATAR_EXTENSIONS}",
            )
        filename = f"{self.object_id}.{ext}"

        # If using S3, upload to S3, else return None
        if settings.use_s3:
            return await s3_client.upload_file(
                uploaded_file.file,
                f"{directory}/{filename}",
            )
        return None
