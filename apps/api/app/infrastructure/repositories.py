from __future__ import annotations

from typing import Iterable, Sequence

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.application.ports.repositories import (
    CheckItem,
    CheckResult,
    CheckResultRepo,
    Media,
    MediaRepo,
    Note,
    NotesRepo,
    Project,
    ProjectRepo,
    Stage,
    StageRepo,
    StageStatus,
    StageStatusRepo,
)
from app.domain.entities import StageStatusValue
from app.infrastructure.db.models import (
    ProjectCheckResultModel,
    ProjectMediaModel,
    ProjectModel,
    ProjectNoteModel,
    ProjectStageStatusModel,
    StageCheckItemModel,
    StageModel,
)


class SqlAlchemyProjectRepo(ProjectRepo):
    def __init__(self, session: Session) -> None:
        self._session = session

    def list_for_owner(self, owner_user_id: str) -> Sequence[Project]:
        rows = self._session.scalars(
            select(ProjectModel).where(ProjectModel.owner_user_id == owner_user_id)
        ).all()
        return [
            Project(
                id=row.id,
                owner_user_id=row.owner_user_id,
                name=row.name,
                location_text=row.location_text,
                created_at=row.created_at,
            )
            for row in rows
        ]

    def create(self, project: Project) -> Project:
        model = ProjectModel(
            id=project.id,
            owner_user_id=project.owner_user_id,
            name=project.name,
            location_text=project.location_text,
            created_at=project.created_at,
        )
        self._session.add(model)
        return project

    def get_by_id_for_owner(self, project_id: str, owner_user_id: str) -> Project | None:
        row = self._session.scalar(
            select(ProjectModel).where(
                ProjectModel.id == project_id,
                ProjectModel.owner_user_id == owner_user_id,
            )
        )
        if row is None:
            return None
        return Project(
            id=row.id,
            owner_user_id=row.owner_user_id,
            name=row.name,
            location_text=row.location_text,
            created_at=row.created_at,
        )


class SqlAlchemyStageRepo(StageRepo):
    def __init__(self, session: Session) -> None:
        self._session = session

    def list_all(self) -> Sequence[Stage]:
        rows = self._session.scalars(select(StageModel)).all()
        return [
            Stage(
                id=row.id,
                slug=row.slug,
                title=row.title,
                short_explanation=row.short_explanation,
                common_mistakes=row.common_mistakes,
                must_document=row.must_document,
                order_index=row.order_index,
            )
            for row in rows
        ]

    def list_check_items_for_stage_ids(
        self, stage_ids: Iterable[str]
    ) -> Sequence[CheckItem]:
        stmt = select(StageCheckItemModel)
        if stage_ids:
            stmt = stmt.where(StageCheckItemModel.stage_id.in_(list(stage_ids)))
        rows = self._session.scalars(stmt).all()
        return [
            CheckItem(
                id=row.id,
                stage_id=row.stage_id,
                title=row.title,
                description=row.description,
                order_index=row.order_index,
            )
            for row in rows
        ]

    def create_stage(self, stage: Stage) -> Stage:
        model = StageModel(
            id=stage.id,
            slug=stage.slug,
            title=stage.title,
            short_explanation=stage.short_explanation,
            common_mistakes=stage.common_mistakes,
            must_document=stage.must_document,
            order_index=stage.order_index,
        )
        self._session.add(model)
        return stage

    def update_stage(self, stage: Stage) -> Stage:
        row = self._session.get(StageModel, stage.id)
        if row is None:
            return self.create_stage(stage)
        row.slug = stage.slug
        row.title = stage.title
        row.short_explanation = stage.short_explanation
        row.common_mistakes = stage.common_mistakes
        row.must_document = stage.must_document
        row.order_index = stage.order_index
        return stage

    def create_check_item(self, item: CheckItem) -> CheckItem:
        model = StageCheckItemModel(
            id=item.id,
            stage_id=item.stage_id,
            title=item.title,
            description=item.description,
            order_index=item.order_index,
        )
        self._session.add(model)
        return item

    def update_check_item(self, item: CheckItem) -> CheckItem:
        row = self._session.get(StageCheckItemModel, item.id)
        if row is None:
            return self.create_check_item(item)
        row.title = item.title
        row.description = item.description
        row.order_index = item.order_index
        return item


class SqlAlchemyStageStatusRepo(StageStatusRepo):
    def __init__(self, session: Session) -> None:
        self._session = session

    def get_for_project(self, project_id: str) -> Sequence[StageStatus]:
        rows = self._session.scalars(
            select(ProjectStageStatusModel).where(
                ProjectStageStatusModel.project_id == project_id
            )
        ).all()
        return [
            StageStatus(
                id=row.id,
                project_id=row.project_id,
                stage_id=row.stage_id,
                status=StageStatusValue(row.status),
                updated_at=row.updated_at,
            )
            for row in rows
        ]

    def upsert(self, status: StageStatus) -> StageStatus:
        existing = self._session.scalar(
            select(ProjectStageStatusModel).where(
                ProjectStageStatusModel.project_id == status.project_id,
                ProjectStageStatusModel.stage_id == status.stage_id,
            )
        )
        if existing is None:
            existing = ProjectStageStatusModel(
                id=status.id,
                project_id=status.project_id,
                stage_id=status.stage_id,
                status=status.status.value,
                updated_at=status.updated_at,
            )
            self._session.add(existing)
        else:
            existing.status = status.status.value
            existing.updated_at = status.updated_at
        return status


class SqlAlchemyCheckResultRepo(CheckResultRepo):
    def __init__(self, session: Session) -> None:
        self._session = session

    def get_for_project(self, project_id: str) -> Sequence[CheckResult]:
        rows = self._session.scalars(
            select(ProjectCheckResultModel).where(
                ProjectCheckResultModel.project_id == project_id
            )
        ).all()
        return [
            CheckResult(
                id=row.id,
                project_id=row.project_id,
                check_item_id=row.check_item_id,
                is_done=row.is_done,
                note=row.note,
                updated_at=row.updated_at,
            )
            for row in rows
        ]

    def upsert(self, result: CheckResult) -> CheckResult:
        existing = self._session.scalar(
            select(ProjectCheckResultModel).where(
                ProjectCheckResultModel.project_id == result.project_id,
                ProjectCheckResultModel.check_item_id == result.check_item_id,
            )
        )
        if existing is None:
            existing = ProjectCheckResultModel(
                id=result.id,
                project_id=result.project_id,
                check_item_id=result.check_item_id,
                is_done=result.is_done,
                note=result.note,
                updated_at=result.updated_at,
            )
            self._session.add(existing)
        else:
            existing.is_done = result.is_done
            existing.note = result.note
            existing.updated_at = result.updated_at
        return result


class SqlAlchemyNotesRepo(NotesRepo):
    def __init__(self, session: Session) -> None:
        self._session = session

    def add(self, note: Note) -> Note:
        model = ProjectNoteModel(
            id=note.id,
            project_id=note.project_id,
            stage_id=note.stage_id,
            body=note.body,
            created_at=note.created_at,
        )
        self._session.add(model)
        return note

    def list_for_project(self, project_id: str) -> Sequence[Note]:
        rows = self._session.scalars(
            select(ProjectNoteModel).where(ProjectNoteModel.project_id == project_id)
        ).all()
        return [
            Note(
                id=row.id,
                project_id=row.project_id,
                stage_id=row.stage_id,
                body=row.body,
                created_at=row.created_at,
            )
            for row in rows
        ]


class SqlAlchemyMediaRepo(MediaRepo):
    def __init__(self, session: Session) -> None:
        self._session = session

    def add(self, media: Media) -> Media:
        model = ProjectMediaModel(
            id=media.id,
            project_id=media.project_id,
            stage_id=media.stage_id,
            storage_path=media.storage_path,
            caption=media.caption,
            taken_at=media.taken_at,
            created_at=media.created_at,
        )
        self._session.add(model)
        return media

    def list_for_project(self, project_id: str) -> Sequence[Media]:
        rows = self._session.scalars(
            select(ProjectMediaModel).where(
                ProjectMediaModel.project_id == project_id
            )
        ).all()
        return [
            Media(
                id=row.id,
                project_id=row.project_id,
                stage_id=row.stage_id,
                storage_path=row.storage_path,
                caption=row.caption,
                taken_at=row.taken_at,
                created_at=row.created_at,
            )
            for row in rows
        ]

