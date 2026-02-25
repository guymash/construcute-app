from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Protocol, Sequence

from app.domain.entities import (
    CheckItem,
    CheckResult,
    Media,
    Note,
    Project,
    Stage,
    StageStatus,
)


class ProjectRepo(Protocol):
    def list_for_owner(self, owner_user_id: str) -> Sequence[Project]: ...

    def create(self, project: Project) -> Project: ...

    def get_by_id_for_owner(self, project_id: str, owner_user_id: str) -> Project | None: ...


class StageRepo(Protocol):
    def list_all(self) -> Sequence[Stage]: ...

    def list_check_items_for_stage_ids(
        self, stage_ids: Iterable[str]
    ) -> Sequence[CheckItem]: ...

    # Admin operations
    def create_stage(self, stage: Stage) -> Stage: ...

    def update_stage(self, stage: Stage) -> Stage: ...

    def create_check_item(self, item: CheckItem) -> CheckItem: ...

    def update_check_item(self, item: CheckItem) -> CheckItem: ...


class StageStatusRepo(Protocol):
    def get_for_project(self, project_id: str) -> Sequence[StageStatus]: ...

    def upsert(self, status: StageStatus) -> StageStatus: ...


class CheckResultRepo(Protocol):
    def get_for_project(self, project_id: str) -> Sequence[CheckResult]: ...

    def upsert(self, result: CheckResult) -> CheckResult: ...


class NotesRepo(Protocol):
    def add(self, note: Note) -> Note: ...

    def list_for_project(self, project_id: str) -> Sequence[Note]: ...


class MediaRepo(Protocol):
    def add(self, media: Media) -> Media: ...

    def list_for_project(self, project_id: str) -> Sequence[Media]: ...


@dataclass(frozen=True)
class ProjectStageView:
    project: Project
    stage: Stage
    check_items: Sequence[CheckItem]
    status: StageStatus | None
    check_results: Sequence[CheckResult]
    notes: Sequence[Note]
    media: Sequence[Media]

