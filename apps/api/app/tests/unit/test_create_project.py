from __future__ import annotations

from datetime import datetime

from app.application.use_cases.projects import (
    CreateProject,
    CreateProjectInput,
)
from app.domain.entities import Project


class InMemoryProjectRepo:
    def __init__(self) -> None:
        self.items: list[Project] = []

    def list_for_owner(self, owner_user_id: str) -> list[Project]:
        return [p for p in self.items if p.owner_user_id == owner_user_id]

    def create(self, project: Project) -> Project:
        self.items.append(project)
        return project

    def get_by_id_for_owner(self, project_id: str, owner_user_id: str) -> Project | None:
        for p in self.items:
            if p.id == project_id and p.owner_user_id == owner_user_id:
                return p
        return None


def test_create_project_persists_in_repo() -> None:
    repo = InMemoryProjectRepo()
    use_case = CreateProject(project_repo=repo)

    result = use_case.execute(
        CreateProjectInput(
            owner_user_id="user-1",
            name="My House",
            location_text="Somewhere",
        )
    )

    assert result.project in repo.items
    assert result.project.owner_user_id == "user-1"
    assert result.project.name == "My House"

