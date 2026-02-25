from __future__ import annotations

from typing import Protocol


class MediaStorage(Protocol):
    def create_presigned_upload(
        self,
        *,
        project_id: str,
        key: str,
        content_type: str,
    ) -> str: ...

