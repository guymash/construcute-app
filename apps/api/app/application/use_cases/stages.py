from __future__ import annotations

from dataclasses import dataclass

from app.application.ports.repositories import (
    CheckResultRepo,
    NotesRepo,
    ProjectRepo,
    ProjectStageView,
    StageRepo,
    StageStatusRepo,
    MediaRepo,
)
from app.domain.entities import Stage


@dataclass
class ListStagesOutput:
    stages: list[Stage]


class ListStages:
    def __init__(self, stage_repo: StageRepo) -> None:
        self._stages = stage_repo

    def execute(self) -> ListStagesOutput:
        stages = list(self._stages.list_all())
        stages.sort(key=lambda s: s.order_index)
        return ListStagesOutput(stages=stages)


@dataclass
class GetProjectStageViewInput:
    owner_user_id: str
    project_id: str
    stage_id: str


@dataclass
class GetProjectStageViewOutput:
    view: ProjectStageView


class GetProjectStageView:
    def __init__(
        self,
        project_repo: ProjectRepo,
        stage_repo: StageRepo,
        stage_status_repo: StageStatusRepo,
        check_result_repo: CheckResultRepo,
        notes_repo: NotesRepo,
        media_repo: MediaRepo,
    ) -> None:
        self._projects = project_repo
        self._stages = stage_repo
        self._stage_statuses = stage_status_repo
        self._check_results = check_result_repo
        self._notes = notes_repo
        self._media = media_repo

    def execute(self, data: GetProjectStageViewInput) -> GetProjectStageViewOutput:
        project = self._projects.get_by_id_for_owner(
            data.project_id, owner_user_id=data.owner_user_id
        )
        if project is None:
            raise PermissionError("Project not found for owner")

        stages = {s.id: s for s in self._stages.list_all()}
        stage = stages.get(data.stage_id)
        if stage is None:
            raise ValueError("Stage not found")

        check_items = [
            c for c in self._stages.list_check_items_for_stage_ids([data.stage_id])
            if c.stage_id == data.stage_id
        ]

        statuses = {
            s.stage_id: s for s in self._stage_statuses.get_for_project(data.project_id)
        }
        status = statuses.get(data.stage_id)

        check_results = [
            r
            for r in self._check_results.get_for_project(data.project_id)
            if r.check_item_id in {c.id for c in check_items}
        ]

        notes = [
            n
            for n in self._notes.list_for_project(data.project_id)
            if n.stage_id == data.stage_id
        ]
        media = [
            m
            for m in self._media.list_for_project(data.project_id)
            if m.stage_id == data.stage_id
        ]

        view = ProjectStageView(
            project=project,
            stage=stage,
            check_items=check_items,
            status=status,
            check_results=check_results,
            notes=notes,
            media=media,
        )
        return GetProjectStageViewOutput(view=view)

