from __future__ import annotations

from typing import Annotated
import os
import uuid
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.application.use_cases.checks_notes_media import (
    CreatePresignedUpload,
    CreatePresignedUploadInput,
    CreatePresignedUploadOutput,
)
from app.domain.entities import Media
from app.infrastructure.media_s3 import S3MediaStorage
from app.infrastructure.repositories import SqlAlchemyMediaRepo, SqlAlchemyProjectRepo
from app.web.dependencies import get_current_user_id, get_db_session


router = APIRouter(prefix="/projects", tags=["media"])


class CreateMediaUploadBody(BaseModel):
    stage_id: str | None = None
    check_item_id: str | None = None
    filename: str
    content_type: str
    local_uri: str | None = None


class CreateMediaUploadResponse(BaseModel):
    upload_url: str
    storage_path: str


@router.post(
    "/{project_id}/media/upload",
    response_model=CreateMediaUploadResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_media_upload(
    project_id: str,
    body: CreateMediaUploadBody,
    user_id: Annotated[str, Depends(get_current_user_id)],
    db: Annotated[Session, Depends(get_db_session)],
) -> CreateMediaUploadResponse:
    project_repo = SqlAlchemyProjectRepo(db)
    media_repo = SqlAlchemyMediaRepo(db)

    # מצב פיתוח בלי S3 אמיתי – שומרים רק מטא־דאטה בדאטהבייס ומשתמשים ב‑URI המקומי
    has_bucket = os.getenv("MEDIA_S3_BUCKET") or os.getenv("S3_BUCKET_NAME")
    if not has_bucket:
        project = project_repo.get_by_id_for_owner(project_id, owner_user_id=user_id)
        if project is None:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Project not found for owner",
            )

        # אם קיבלנו URI מקומי מהמובייל – נשמור אותו כ‑storage_path לשימוש ב‑Image
        fake_key = body.local_uri or f"{project_id}/{uuid.uuid4()}_{body.filename}"

        media = Media(
            id=str(uuid.uuid4()),
            project_id=project_id,
            stage_id=body.stage_id,
            storage_path=fake_key,
            caption=None,
            taken_at=None,
            created_at=datetime.now(timezone.utc),
        )
        media_repo.add(media)

        return CreateMediaUploadResponse(
            upload_url=f"DEV_LOCAL://{fake_key}",
            storage_path=fake_key,
        )

    bucket = os.getenv("MEDIA_S3_BUCKET") or os.getenv("S3_BUCKET_NAME") or "dev-bucket"
    region = os.getenv("AWS_REGION")
    storage = S3MediaStorage(bucket_name=bucket, region=region)
    use_case = CreatePresignedUpload(
        project_repo=project_repo,
        media_repo=media_repo,
        storage=storage,
    )
    result: CreatePresignedUploadOutput = use_case.execute(
        CreatePresignedUploadInput(
            owner_user_id=user_id,
            project_id=project_id,
            stage_id=body.stage_id,
            filename=body.filename,
            content_type=body.content_type,
        )
    )
    return CreateMediaUploadResponse(
        upload_url=result.upload_url,
        storage_path=result.storage_path,
    )

