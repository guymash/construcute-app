from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Optional


class StageStatusValue(str, Enum):
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    DONE = "done"


@dataclass(frozen=True)
class Project:
    id: str
    owner_user_id: str
    name: str
    location_text: Optional[str]
    created_at: datetime


@dataclass(frozen=True)
class Stage:
    id: str
    slug: str
    title: str
    short_explanation: str
    common_mistakes: str
    must_document: str
    order_index: int


@dataclass(frozen=True)
class CheckItem:
    id: str
    stage_id: str
    title: str
    description: Optional[str]
    order_index: int


@dataclass(frozen=True)
class StageStatus:
    id: str
    project_id: str
    stage_id: str
    status: StageStatusValue
    updated_at: datetime


@dataclass(frozen=True)
class CheckResult:
    id: str
    project_id: str
    check_item_id: str
    is_done: bool
    note: Optional[str]
    updated_at: datetime


@dataclass(frozen=True)
class Note:
    id: str
    project_id: str
    stage_id: Optional[str]
    body: str
    created_at: datetime


@dataclass(frozen=True)
class Media:
    id: str
    project_id: str
    stage_id: Optional[str]
    storage_path: str
    caption: Optional[str]
    taken_at: Optional[datetime]
    created_at: datetime

