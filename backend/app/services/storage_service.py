"""File storage service."""

import os
import uuid
from pathlib import Path
from typing import Optional

import aiofiles
import boto3
from botocore.exceptions import ClientError

from app.config import settings


class StorageService:
    """Service for file storage operations."""

    def __init__(self):
        self.storage_type = settings.STORAGE_TYPE
        self.local_path = Path(settings.STORAGE_LOCAL_PATH)

        if self.storage_type == "s3":
            self.s3_client = boto3.client("s3")
            self.bucket = os.getenv("AWS_S3_BUCKET")

    async def save_file(
        self,
        content: bytes,
        folder: str,
        filename: Optional[str] = None,
        extension: str = "",
    ) -> str:
        """Save a file and return the path/URL."""
        if not filename:
            filename = f"{uuid.uuid4()}{extension}"

        if self.storage_type == "local":
            return await self._save_local(content, folder, filename)
        else:
            return await self._save_s3(content, folder, filename)

    async def _save_local(self, content: bytes, folder: str, filename: str) -> str:
        """Save file to local filesystem."""
        folder_path = self.local_path / folder
        folder_path.mkdir(parents=True, exist_ok=True)

        file_path = folder_path / filename
        async with aiofiles.open(file_path, "wb") as f:
            await f.write(content)

        return str(file_path)

    async def _save_s3(self, content: bytes, folder: str, filename: str) -> str:
        """Save file to S3."""
        key = f"{folder}/{filename}"
        self.s3_client.put_object(
            Bucket=self.bucket,
            Key=key,
            Body=content,
        )
        return f"s3://{self.bucket}/{key}"

    async def get_file(self, path: str) -> Optional[bytes]:
        """Get a file by path."""
        if self.storage_type == "local":
            return await self._get_local(path)
        else:
            return await self._get_s3(path)

    async def _get_local(self, path: str) -> Optional[bytes]:
        """Get file from local filesystem."""
        try:
            async with aiofiles.open(path, "rb") as f:
                return await f.read()
        except FileNotFoundError:
            return None

    async def _get_s3(self, path: str) -> Optional[bytes]:
        """Get file from S3."""
        try:
            # Parse S3 path
            key = path.replace(f"s3://{self.bucket}/", "")
            response = self.s3_client.get_object(Bucket=self.bucket, Key=key)
            return response["Body"].read()
        except ClientError:
            return None

    async def delete_file(self, path: str) -> bool:
        """Delete a file."""
        if self.storage_type == "local":
            return await self._delete_local(path)
        else:
            return await self._delete_s3(path)

    async def _delete_local(self, path: str) -> bool:
        """Delete file from local filesystem."""
        try:
            os.remove(path)
            return True
        except FileNotFoundError:
            return False

    async def _delete_s3(self, path: str) -> bool:
        """Delete file from S3."""
        try:
            key = path.replace(f"s3://{self.bucket}/", "")
            self.s3_client.delete_object(Bucket=self.bucket, Key=key)
            return True
        except ClientError:
            return False
