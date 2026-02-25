from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
import uuid

from app.application.ports.repositories import ProjectRepo
from app.domain.entities import Project


@dataclass
class CreateProjectInput:
    owner_user_id: str
    name: str
    location_text: str | None


@dataclass
class CreateProjectOutput:
    project: Project


class CreateProject:
    def __init__(self, project_repo: ProjectRepo) -> None:
        self._projects = project_repo

    def execute(self, data: CreateProjectInput) -> CreateProjectOutput:
        project = Project(
            id=str(uuid.uuid4()),
            owner_user_id=data.owner_user_id,
            name=data.name,
            location_text=data.location_text,
            created_at=datetime.now(timezone.utc),
        )
        saved = self._projects.create(project)
        return CreateProjectOutput(project=saved)


@dataclass
class ListProjectsInput:
    owner_user_id: str


@dataclass
class ListProjectsOutput:
    projects: list[Project]


class ListProjects:
    def __init__(self, project_repo: ProjectRepo) -> None:
        self._projects = project_repo

    def execute(self, data: ListProjectsInput) -> ListProjectsOutput:
        projects = list(self._projects.list_for_owner(data.owner_user_id))
        return ListProjectsOutput(projects=projects)

