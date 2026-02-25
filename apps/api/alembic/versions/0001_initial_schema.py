from __future__ import annotations

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql as pg

# revision identifiers, used by Alembic.
revision = "0001_initial_schema"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "projects",
        sa.Column("id", pg.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("owner_user_id", sa.Text(), nullable=False),
        sa.Column("name", sa.Text(), nullable=False),
        sa.Column("location_text", sa.Text(), nullable=True),
        sa.Column("created_at", sa.TIMESTAMP(timezone=True), nullable=False),
    )
    op.create_index(
        "ix_projects_owner_user_id",
        "projects",
        ["owner_user_id"],
    )

    op.create_table(
        "stages",
        sa.Column("id", pg.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("slug", sa.Text(), nullable=False, unique=True),
        sa.Column("title", sa.Text(), nullable=False),
        sa.Column("short_explanation", sa.Text(), nullable=False),
        sa.Column("common_mistakes", sa.Text(), nullable=False),
        sa.Column("must_document", sa.Text(), nullable=False),
        sa.Column("order_index", sa.Integer(), nullable=False),
    )
    op.create_index(
        "ix_stages_order_index",
        "stages",
        ["order_index"],
    )

    op.create_table(
        "stage_check_items",
        sa.Column("id", pg.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column(
            "stage_id",
            pg.UUID(as_uuid=True),
            sa.ForeignKey("stages.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("title", sa.Text(), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("order_index", sa.Integer(), nullable=False),
    )
    op.create_index(
        "ix_stage_check_items_stage_order",
        "stage_check_items",
        ["stage_id", "order_index"],
    )

    op.create_table(
        "project_stage_status",
        sa.Column("id", pg.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column(
            "project_id",
            pg.UUID(as_uuid=True),
            sa.ForeignKey("projects.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "stage_id",
            pg.UUID(as_uuid=True),
            sa.ForeignKey("stages.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("status", sa.Text(), nullable=False),
        sa.Column("updated_at", sa.TIMESTAMP(timezone=True), nullable=False),
    )

    op.create_table(
        "project_check_results",
        sa.Column("id", pg.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column(
            "project_id",
            pg.UUID(as_uuid=True),
            sa.ForeignKey("projects.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "check_item_id",
            pg.UUID(as_uuid=True),
            sa.ForeignKey("stage_check_items.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("is_done", sa.Boolean(), nullable=False),
        sa.Column("note", sa.Text(), nullable=True),
        sa.Column("updated_at", sa.TIMESTAMP(timezone=True), nullable=False),
    )
    op.create_unique_constraint(
        "uq_project_check_results_project_check_item",
        "project_check_results",
        ["project_id", "check_item_id"],
    )

    op.create_table(
        "project_notes",
        sa.Column("id", pg.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column(
            "project_id",
            pg.UUID(as_uuid=True),
            sa.ForeignKey("projects.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "stage_id",
            pg.UUID(as_uuid=True),
            sa.ForeignKey("stages.id", ondelete="SET NULL"),
            nullable=True,
        ),
        sa.Column("body", sa.Text(), nullable=False),
        sa.Column("created_at", sa.TIMESTAMP(timezone=True), nullable=False),
    )

    op.create_table(
        "project_media",
        sa.Column("id", pg.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column(
            "project_id",
            pg.UUID(as_uuid=True),
            sa.ForeignKey("projects.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "stage_id",
            pg.UUID(as_uuid=True),
            sa.ForeignKey("stages.id", ondelete="SET NULL"),
            nullable=True,
        ),
        sa.Column("storage_path", sa.Text(), nullable=False),
        sa.Column("caption", sa.Text(), nullable=True),
        sa.Column("taken_at", sa.TIMESTAMP(timezone=True), nullable=True),
        sa.Column("created_at", sa.TIMESTAMP(timezone=True), nullable=False),
    )

    op.create_table(
        "ai_conversations",
        sa.Column("id", pg.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column(
            "project_id",
            pg.UUID(as_uuid=True),
            sa.ForeignKey("projects.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "stage_id",
            pg.UUID(as_uuid=True),
            sa.ForeignKey("stages.id", ondelete="SET NULL"),
            nullable=True,
        ),
        sa.Column("user_id", sa.Text(), nullable=False),
        sa.Column("user_message", sa.Text(), nullable=False),
        sa.Column("ai_answer", sa.Text(), nullable=False),
        sa.Column("created_at", sa.TIMESTAMP(timezone=True), nullable=False),
    )


def downgrade() -> None:
    op.drop_table("ai_conversations")
    op.drop_table("project_media")
    op.drop_table("project_notes")
    op.drop_constraint(
        "uq_project_check_results_project_check_item",
        "project_check_results",
        type_="unique",
    )
    op.drop_table("project_check_results")
    op.drop_table("project_stage_status")
    op.drop_index("ix_stage_check_items_stage_order", table_name="stage_check_items")
    op.drop_table("stage_check_items")
    op.drop_index("ix_stages_order_index", table_name="stages")
    op.drop_table("stages")
    op.drop_index("ix_projects_owner_user_id", table_name="projects")
    op.drop_table("projects")

