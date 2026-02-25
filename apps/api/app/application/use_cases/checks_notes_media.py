from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
import uuid

from app.application.ports.media import MediaStorage
from app.application.ports.repositories import (
    CheckResultRepo,
    MediaRepo,
    NotesRepo,
    ProjectRepo,
    StageRepo,
)
from app.domain.entities import CheckResult, Media, Note
from app.domain.entities import StageStatusValue


@dataclass
class UpdateCheckResultInput:
    owner_user_id: str
    project_id: str
    check_item_id: str
    is_done: bool
    note: str | None


class UpdateCheckResult:
    def __init__(
        self,
        project_repo: ProjectRepo,
        stage_repo: StageRepo,
        check_result_repo: CheckResultRepo,
    ) -> None:
        self._projects = project_repo
        self._stages = stage_repo
        self._results = check_result_repo

    def execute(self, data: UpdateCheckResultInput) -> None:
        project = self._projects.get_by_id_for_owner(
            data.project_id, owner_user_id=data.owner_user_id
        )
        if project is None:
            raise PermissionError("Project not found for owner")

        all_checks = self._stages.list_check_items_for_stage_ids([])
        known_check_ids = {c.id for c in all_checks}
        if data.check_item_id not in known_check_ids:
            raise ValueError("Unknown check item")

        result = CheckResult(
            id=str(uuid.uuid4()),
            project_id=data.project_id,
            check_item_id=data.check_item_id,
            is_done=data.is_done,
            note=data.note,
            updated_at=datetime.now(timezone.utc),
        )
        self._results.upsert(result)


@dataclass
class AddNoteInput:
    owner_user_id: str
    project_id: str
    stage_id: str | None
    body: str


class AddNote:
    def __init__(self, project_repo: ProjectRepo, notes_repo: NotesRepo) -> None:
        self._projects = project_repo
        self._notes = notes_repo

    def execute(self, data: AddNoteInput) -> Note:
        project = self._projects.get_by_id_for_owner(
            data.project_id, owner_user_id=data.owner_user_id
        )
        if project is None:
            raise PermissionError("Project not found for owner")

        note = Note(
            id=str(uuid.uuid4()),
            project_id=data.project_id,
            stage_id=data.stage_id,
            body=data.body,
            created_at=datetime.now(timezone.utc),
        )
        return self._notes.add(note)


@dataclass
class CreatePresignedUploadInput:
    owner_user_id: str
    project_id: str
    stage_id: str | None
    filename: str
    content_type: str


@dataclass
class CreatePresignedUploadOutput:
    upload_url: str
    storage_path: str


class CreatePresignedUpload:
    def __init__(
        self,
        project_repo: ProjectRepo,
        media_repo: MediaRepo,
        storage: MediaStorage,
    ) -> None:
        self._projects = project_repo
        self._media = media_repo
        self._storage = storage

    def execute(self, data: CreatePresignedUploadInput) -> CreatePresignedUploadOutput:
        project = self._projects.get_by_id_for_owner(
            data.project_id, owner_user_id=data.owner_user_id
        )
        if project is None:
            raise PermissionError("Project not found for owner")

        key = f"{data.project_id}/{uuid.uuid4()}_{data.filename}"
        upload_url = self._storage.create_presigned_upload(
            project_id=data.project_id,
            key=key,
            content_type=data.content_type,
        )

        media = Media(
            id=str(uuid.uuid4()),
            project_id=data.project_id,
            stage_id=data.stage_id,
            storage_path=key,
            caption=None,
            taken_at=None,
            created_at=datetime.now(timezone.utc),
        )
        self._media.add(media)
        return CreatePresignedUploadOutput(upload_url=upload_url, storage_path=key)


@dataclass
class ListNotesForProjectInput:
    owner_user_id: str
    project_id: str


class ListNotesForProject:
    def __init__(self, project_repo: ProjectRepo, notes_repo: NotesRepo) -> None:
        self._projects = project_repo
        self._notes = notes_repo

    def execute(self, data: ListNotesForProjectInput) -> list[Note]:
        project = self._projects.get_by_id_for_owner(
            data.project_id, owner_user_id=data.owner_user_id
        )
        if project is None:
            raise PermissionError("Project not found for owner")
        return list(self._notes.list_for_project(data.project_id))

