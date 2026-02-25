from __future__ import annotations

from datetime import datetime
from typing import Annotated

from fastapi import APIRouter, Depends, Query, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.application.use_cases.checks_notes_media import (
    AddNote,
    AddNoteInput,
    ListNotesForProject,
    ListNotesForProjectInput,
)
from app.infrastructure.repositories import SqlAlchemyNotesRepo, SqlAlchemyProjectRepo
from app.web.dependencies import get_current_user_id, get_db_session


router = APIRouter(prefix="/projects", tags=["notes"])


class CreateNoteBody(BaseModel):
    stage_id: str | None = None
    body: str


class NoteOut(BaseModel):
    id: str
    stage_id: str | None
    body: str
    created_at: datetime


@router.post("/{project_id}/notes", status_code=status.HTTP_201_CREATED)
def create_note(
    project_id: str,
    body: CreateNoteBody,
    user_id: Annotated[str, Depends(get_current_user_id)],
    db: Annotated[Session, Depends(get_db_session)],
) -> None:
    project_repo = SqlAlchemyProjectRepo(db)
    notes_repo = SqlAlchemyNotesRepo(db)
    use_case = AddNote(project_repo=project_repo, notes_repo=notes_repo)
    use_case.execute(
        AddNoteInput(
            owner_user_id=user_id,
            project_id=project_id,
            stage_id=body.stage_id,
            body=body.body,
        )
    )


@router.get("/{project_id}/notes", response_model=list[NoteOut])
def list_notes(
    project_id: str,
    user_id: Annotated[str, Depends(get_current_user_id)],
    db: Annotated[Session, Depends(get_db_session)],
    stage_id: str | None = Query(default=None),
) -> list[NoteOut]:
    project_repo = SqlAlchemyProjectRepo(db)
    notes_repo = SqlAlchemyNotesRepo(db)
    use_case = ListNotesForProject(project_repo=project_repo, notes_repo=notes_repo)
    notes = use_case.execute(
        ListNotesForProjectInput(owner_user_id=user_id, project_id=project_id)
    )
    if stage_id is not None:
        notes = [n for n in notes if n.stage_id == stage_id]
    return [
        NoteOut(
            id=n.id,
            stage_id=n.stage_id,
            body=n.body,
            created_at=n.created_at,
        )
        for n in notes
    ]

