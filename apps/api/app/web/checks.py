from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.application.use_cases.checks_notes_media import (
    UpdateCheckResult,
    UpdateCheckResultInput,
)
from app.infrastructure.repositories import (
    SqlAlchemyCheckResultRepo,
    SqlAlchemyProjectRepo,
    SqlAlchemyStageRepo,
)
from app.web.dependencies import get_current_user_id, get_db_session


router = APIRouter(prefix="/projects", tags=["checks"])


class UpdateCheckBody(BaseModel):
    is_done: bool
    note: str | None = None


@router.post(
    "/{project_id}/checks/{check_item_id}",
    status_code=status.HTTP_201_CREATED,
)
def update_check(
    project_id: str,
    check_item_id: str,
    body: UpdateCheckBody,
    user_id: Annotated[str, Depends(get_current_user_id)],
    db: Annotated[Session, Depends(get_db_session)],
) -> None:
    project_repo = SqlAlchemyProjectRepo(db)
    stage_repo = SqlAlchemyStageRepo(db)
    check_repo = SqlAlchemyCheckResultRepo(db)
    use_case = UpdateCheckResult(
        project_repo=project_repo,
        stage_repo=stage_repo,
        check_result_repo=check_repo,
    )
    use_case.execute(
        UpdateCheckResultInput(
            owner_user_id=user_id,
            project_id=project_id,
            check_item_id=check_item_id,
            is_done=body.is_done,
            note=body.note,
        )
    )

