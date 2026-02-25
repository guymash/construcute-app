from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.application.use_cases.stages import (
    GetProjectStageView,
    GetProjectStageViewInput,
    ListStages,
)
from app.infrastructure.repositories import (
    SqlAlchemyCheckResultRepo,
    SqlAlchemyMediaRepo,
    SqlAlchemyNotesRepo,
    SqlAlchemyProjectRepo,
    SqlAlchemyStageRepo,
    SqlAlchemyStageStatusRepo,
)
from app.web.dependencies import get_current_user_id, get_db_session


router = APIRouter(prefix="/stages", tags=["stages"])


class StageOut(BaseModel):
    id: str
    slug: str
    title: str
    short_explanation: str
    common_mistakes: str
    must_document: str
    order_index: int


@router.get("", response_model=list[StageOut])
def list_stages(
    db: Annotated[Session, Depends(get_db_session)],
) -> list[StageOut]:
    stage_repo = SqlAlchemyStageRepo(db)
    use_case = ListStages(stage_repo=stage_repo)
    result = use_case.execute()
    return [StageOut(**vars(s)) for s in result.stages]


class CheckItemOut(BaseModel):
    id: str
    title: str
    description: str | None
    order_index: int
    is_done: bool
    note: str | None


class NoteOut(BaseModel):
    id: str
    body: str
    created_at: str


class MediaOut(BaseModel):
    id: str
    url: str
    caption: str | None


class ProjectStageViewOut(BaseModel):
    project_id: str
    stage: StageOut
    check_items: list[CheckItemOut]
    media: list[MediaOut]


@router.get("/projects/{project_id}/{stage_id}", response_model=ProjectStageViewOut)
def get_project_stage_view(
    project_id: str,
    stage_id: str,
    user_id: Annotated[str, Depends(get_current_user_id)],
    db: Annotated[Session, Depends(get_db_session)],
) -> ProjectStageViewOut:
    project_repo = SqlAlchemyProjectRepo(db)
    stage_repo = SqlAlchemyStageRepo(db)
    status_repo = SqlAlchemyStageStatusRepo(db)
    check_repo = SqlAlchemyCheckResultRepo(db)
    notes_repo = SqlAlchemyNotesRepo(db)
    media_repo = SqlAlchemyMediaRepo(db)

    use_case = GetProjectStageView(
        project_repo=project_repo,
        stage_repo=stage_repo,
        stage_status_repo=status_repo,
        check_result_repo=check_repo,
        notes_repo=notes_repo,
        media_repo=media_repo,
    )

    result = use_case.execute(
        GetProjectStageViewInput(
            owner_user_id=user_id,
            project_id=project_id,
            stage_id=stage_id,
        )
    )
    v = result.view
    results_by_check_id = {r.check_item_id: r for r in v.check_results}

    # בניית URL ציבורי/לצורכי תצוגה לתמונות (בהנחה שהבאקט מאפשר GET)
    import os

    bucket = os.getenv("MEDIA_S3_BUCKET") or os.getenv("S3_BUCKET_NAME")
    region = os.getenv("AWS_REGION") or "us-east-1"
    return ProjectStageViewOut(
        project_id=v.project.id,
        stage=StageOut(
            id=v.stage.id,
            slug=v.stage.slug,
            title=v.stage.title,
            short_explanation=v.stage.short_explanation,
            common_mistakes=v.stage.common_mistakes,
            must_document=v.stage.must_document,
            order_index=v.stage.order_index,
        ),
        check_items=[
            CheckItemOut(
                id=c.id,
                title=c.title,
                description=c.description,
                order_index=c.order_index,
                is_done=results_by_check_id.get(c.id).is_done
                if c.id in results_by_check_id
                else False,
                note=results_by_check_id.get(c.id).note
                if c.id in results_by_check_id
                else None,
            )
            for c in v.check_items
        ],
        media=[
            MediaOut(
                id=m.id,
                url=f"https://{bucket}.s3.{region}.amazonaws.com/{m.storage_path}"
                if bucket
                else m.storage_path,
                caption=m.caption,
            )
            for m in v.media
        ],
    )

