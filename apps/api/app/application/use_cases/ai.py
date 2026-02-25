from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
import uuid

from app.application.ports.ai import AIClient
from app.application.ports.repositories import (
    NotesRepo,
    ProjectRepo,
    StageRepo,
)
from app.domain.entities import Note


@dataclass
class AskAIInput:
    owner_user_id: str
    project_id: str
    stage_id: str | None
    question: str


@dataclass
class AskAIOutput:
    answer: str


class AskAI:
    def __init__(
        self,
        project_repo: ProjectRepo,
        stage_repo: StageRepo,
        notes_repo: NotesRepo,
        ai_client: AIClient,
    ) -> None:
        self._projects = project_repo
        self._stages = stage_repo
        self._notes = notes_repo
        self._ai = ai_client

    def execute(self, data: AskAIInput) -> AskAIOutput:
        project = self._projects.get_by_id_for_owner(
            data.project_id, owner_user_id=data.owner_user_id
        )
        if project is None:
            raise PermissionError("Project not found for owner")

        stage = None
        if data.stage_id is not None:
            for s in self._stages.list_all():
                if s.id == data.stage_id:
                    stage = s
                    break

        project_context = f"Project: {project.name}. Location: {project.location_text or 'n/a'}."
        stage_context = None
        if stage is not None:
            stage_context = (
                f"Stage: {stage.title}. Explanation: {stage.short_explanation}. "
                f"Common mistakes: {stage.common_mistakes}. Must document: {stage.must_document}."
            )

        answer = self._ai.ask(
            question=data.question,
            project_context=project_context,
            stage_context=stage_context,
        )

        note = Note(
            id=str(uuid.uuid4()),
            project_id=data.project_id,
            stage_id=data.stage_id,
            body=f"Q: {data.question}\nA: {answer}",
            created_at=datetime.now(timezone.utc),
        )
        self._notes.add(note)

        return AskAIOutput(answer=answer)

