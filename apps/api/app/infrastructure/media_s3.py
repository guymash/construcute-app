from __future__ import annotations

import os
from datetime import timedelta

import boto3

from app.application.ports.media import MediaStorage


class S3MediaStorage(MediaStorage):
    def __init__(self, bucket_name: str, region: str | None = None) -> None:
        self._bucket = bucket_name
        self._client = boto3.client("s3", region_name=region)

    def create_presigned_upload(
        self,
        *,
        project_id: str,
        key: str,
        content_type: str,
    ) -> str:
        expires_in = int(os.getenv("S3_PRESIGN_TTL_SECONDS", "3600"))
        return self._client.generate_presigned_url(
            "put_object",
            Params={
                "Bucket": self._bucket,
                "Key": key,
                "ContentType": content_type,
            },
            ExpiresIn=expires_in,
        )

