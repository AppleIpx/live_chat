from typing import BinaryIO

import boto3

from live_chat.settings import settings


class S3Client:
    """Client for work with S3 bucket."""

    def __init__(self) -> None:
        self.bucket_name = settings.aws_bucket_name
        self.s3_client = boto3.client(
            "s3",
            endpoint_url=settings.aws_s3_endpoint_url,
            aws_access_key_id=settings.aws_access_key_id,
            aws_secret_access_key=settings.aws_secret_access_key,
            region_name=settings.aws_region_name,
            verify=False,
        )

    async def upload_file(self, file: BinaryIO, path: str) -> str:
        """Upload a file to an S3 bucket."""
        self.s3_client.upload_fileobj(file, self.bucket_name, path)
        return f"{settings.minio_url}{path}"


s3_client = S3Client()
