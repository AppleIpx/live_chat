from enum import StrEnum


class UploadFileDirectoryEnum(StrEnum):
    """Enum for uploading files to a directory in S3."""

    group_images = "group_images"
    avatars = "avatars"
    chat_attachments = "chat_attachments"
