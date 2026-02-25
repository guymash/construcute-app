from __future__ import annotations

from dataclasses import dataclass
import uuid

from app.application.ports.repositories import CheckItem, Stage, StageRepo


@dataclass
class AdminStageWithChecks:
  stage: Stage
  checks: list[CheckItem]


@dataclass
class ListAdminStagesOutput:
  stages: list[AdminStageWithChecks]


class ListAdminStages:
  def __init__(self, stage_repo: StageRepo) -> None:
      self._stages = stage_repo

  def execute(self) -> ListAdminStagesOutput:
      stages = list(self._stages.list_all())
      checks = self._stages.list_check_items_for_stage_ids([s.id for s in stages])
      checks_by_stage: dict[str, list[CheckItem]] = {s.id: [] for s in stages}
      for c in checks:
          checks_by_stage.setdefault(c.stage_id, []).append(c)
      return ListAdminStagesOutput(
          stages=[
              AdminStageWithChecks(stage=s, checks=checks_by_stage.get(s.id, []))
              for s in sorted(stages, key=lambda s: s.order_index)
          ]
      )


@dataclass
class UpsertStageInput:
  id: str | None
  slug: str
  title: str
  short_explanation: str
  common_mistakes: str
  must_document: str
  order_index: int


class UpsertStage:
  def __init__(self, stage_repo: StageRepo) -> None:
      self._stages = stage_repo

  def execute(self, data: UpsertStageInput) -> Stage:
      stage = Stage(
          id=data.id or str(uuid.uuid4()),
          slug=data.slug,
          title=data.title,
          short_explanation=data.short_explanation,
          common_mistakes=data.common_mistakes,
          must_document=data.must_document,
          order_index=data.order_index,
      )
      if data.id:
          return self._stages.update_stage(stage)
      return self._stages.create_stage(stage)


@dataclass
class UpsertCheckItemInput:
  id: str | None
  stage_id: str
  title: str
  description: str | None
  order_index: int


class UpsertCheckItem:
  def __init__(self, stage_repo: StageRepo) -> None:
      self._stages = stage_repo

  def execute(self, data: UpsertCheckItemInput) -> CheckItem:
      item = CheckItem(
          id=data.id or str(uuid.uuid4()),
          stage_id=data.stage_id,
          title=data.title,
          description=data.description,
          order_index=data.order_index,
      )
      if data.id:
          return self._stages.update_check_item(item)
      return self._stages.create_check_item(item)

