from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.application.use_cases.projects import (
    CreateProject,
    CreateProjectInput,
    ListProjects,
    ListProjectsInput,
)
from app.infrastructure.repositories import SqlAlchemyProjectRepo
from app.web.dependencies import get_current_user_id, get_db_session


router = APIRouter(prefix="/projects", tags=["projects"])


class ProjectOut(BaseModel):
    id: str
    name: str
    location_text: str | None

    class Config:
        from_attributes = True


class CreateProjectBody(BaseModel):
    name: str
    location_text: str | None = None


@router.get("", response_model=list[ProjectOut])
def list_projects(
    user_id: Annotated[str, Depends(get_current_user_id)],
    db: Annotated[Session, Depends(get_db_session)],
) -> list[ProjectOut]:
    repo = SqlAlchemyProjectRepo(db)
    use_case = ListProjects(project_repo=repo)
    result = use_case.execute(ListProjectsInput(owner_user_id=user_id))
    return [
        ProjectOut(id=p.id, name=p.name, location_text=p.location_text)
        for p in result.projects
    ]


@router.post("", response_model=ProjectOut, status_code=status.HTTP_201_CREATED)
def create_project(
    body: CreateProjectBody,
    user_id: Annotated[str, Depends(get_current_user_id)],
    db: Annotated[Session, Depends(get_db_session)],
) -> ProjectOut:
    repo = SqlAlchemyProjectRepo(db)
    use_case = CreateProject(project_repo=repo)
    result = use_case.execute(
        CreateProjectInput(
            owner_user_id=user_id,
            name=body.name,
            location_text=body.location_text,
        )
    )
    project = result.project
    return ProjectOut(
        id=project.id,
        name=project.name,
        location_text=project.location_text,
    )

