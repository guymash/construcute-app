from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.application.use_cases.admin_stages import (
    AdminStageWithChecks,
    ListAdminStages,
    UpsertCheckItem,
    UpsertCheckItemInput,
    UpsertStage,
    UpsertStageInput,
)
from app.infrastructure.repositories import SqlAlchemyStageRepo
from app.web.dependencies import get_admin_token, get_db_session


router = APIRouter(prefix="/admin", tags=["admin"])


class AdminCheckItemBody(BaseModel):
    id: str | None = None
    stage_id: str
    title: str
    description: str | None = None
    order_index: int


class AdminStageBody(BaseModel):
    id: str | None = None
    slug: str
    title: str
    short_explanation: str
    common_mistakes: str
    must_document: str
    order_index: int
    checks: list[AdminCheckItemBody] = []


class AdminStageOut(AdminStageBody):
    id: str


@router.get("/stages", response_model=list[AdminStageOut])
def list_admin_stages(
    _admin: Annotated[str, Depends(get_admin_token)],
    db: Annotated[Session, Depends(get_db_session)],
) -> list[AdminStageOut]:
    repo = SqlAlchemyStageRepo(db)
    use_case = ListAdminStages(stage_repo=repo)
    result = use_case.execute()
    out: list[AdminStageOut] = []
    for sc in result.stages:
        s = sc.stage
        out.append(
            AdminStageOut(
                id=s.id,
                slug=s.slug,
                title=s.title,
                short_explanation=s.short_explanation,
                common_mistakes=s.common_mistakes,
                must_document=s.must_document,
                order_index=s.order_index,
                checks=[
                    AdminCheckItemBody(
                        id=c.id,
                        stage_id=c.stage_id,
                        title=c.title,
                        description=c.description,
                        order_index=c.order_index,
                    )
                    for c in sc.checks
                ],
            )
        )
    return out


@router.post("/stages", response_model=AdminStageOut)
def upsert_admin_stage(
    body: AdminStageBody,
    _admin: Annotated[str, Depends(get_admin_token)],
    db: Annotated[Session, Depends(get_db_session)],
) -> AdminStageOut:
    repo = SqlAlchemyStageRepo(db)
    upsert_stage = UpsertStage(stage_repo=repo)
    saved_stage = upsert_stage.execute(
        UpsertStageInput(
            id=body.id,
            slug=body.slug,
            title=body.title,
            short_explanation=body.short_explanation,
            common_mistakes=body.common_mistakes,
            must_document=body.must_document,
            order_index=body.order_index,
        )
    )

    upsert_check = UpsertCheckItem(stage_repo=repo)
    for check in body.checks:
        upsert_check.execute(
            UpsertCheckItemInput(
                id=check.id,
                stage_id=saved_stage.id,
                title=check.title,
                description=check.description,
                order_index=check.order_index,
            )
        )

    # re-use listing use-case to include updated checks
    list_use_case = ListAdminStages(stage_repo=repo)
    stages = list_use_case.execute().stages
    sc: AdminStageWithChecks | None = next(
        (s for s in stages if s.stage.id == saved_stage.id), None
    )
    if sc is None:
        raise RuntimeError("Stage saved but not found")

    s = sc.stage
    return AdminStageOut(
        id=s.id,
        slug=s.slug,
        title=s.title,
        short_explanation=s.short_explanation,
        common_mistakes=s.common_mistakes,
        must_document=s.must_document,
        order_index=s.order_index,
        checks=[
            AdminCheckItemBody(
                id=c.id,
                stage_id=c.stage_id,
                title=c.title,
                description=c.description,
                order_index=c.order_index,
            )
            for c in sc.checks
        ],
    )

