from __future__ import annotations

from datetime import datetime

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
    Index,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


class ProjectModel(Base):
    __tablename__ = "projects"

    id: Mapped[str] = mapped_column(UUID(as_uuid=False), primary_key=True)
    owner_user_id: Mapped[str] = mapped_column(Text, index=True)
    name: Mapped[str] = mapped_column(Text)
    location_text: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))

    stages_statuses: Mapped[list["ProjectStageStatusModel"]] = relationship(
        back_populates="project",
        cascade="all, delete-orphan",
    )


class StageModel(Base):
    __tablename__ = "stages"

    id: Mapped[str] = mapped_column(UUID(as_uuid=False), primary_key=True)
    slug: Mapped[str] = mapped_column(Text, unique=True)
    title: Mapped[str] = mapped_column(Text)
    short_explanation: Mapped[str] = mapped_column(Text)
    common_mistakes: Mapped[str] = mapped_column(Text)
    must_document: Mapped[str] = mapped_column(Text)
    order_index: Mapped[int] = mapped_column(Integer, index=True)

    check_items: Mapped[list["StageCheckItemModel"]] = relationship(
        back_populates="stage",
        cascade="all, delete-orphan",
    )


class StageCheckItemModel(Base):
    __tablename__ = "stage_check_items"

    id: Mapped[str] = mapped_column(UUID(as_uuid=False), primary_key=True)
    stage_id: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        ForeignKey("stages.id", ondelete="CASCADE"),
        index=True,
    )
    title: Mapped[str] = mapped_column(Text)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    order_index: Mapped[int] = mapped_column(Integer)

    stage: Mapped[StageModel] = relationship(back_populates="check_items")

    __table_args__ = (
        Index("ix_stage_check_items_stage_order", "stage_id", "order_index"),
    )


class ProjectStageStatusModel(Base):
    __tablename__ = "project_stage_status"

    id: Mapped[str] = mapped_column(UUID(as_uuid=False), primary_key=True)
    project_id: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        ForeignKey("projects.id", ondelete="CASCADE"),
        index=True,
    )
    stage_id: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        ForeignKey("stages.id", ondelete="CASCADE"),
        index=True,
    )
    status: Mapped[str] = mapped_column(String(length=32))
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))

    project: Mapped[ProjectModel] = relationship(back_populates="stages_statuses")


class ProjectCheckResultModel(Base):
    __tablename__ = "project_check_results"

    id: Mapped[str] = mapped_column(UUID(as_uuid=False), primary_key=True)
    project_id: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        ForeignKey("projects.id", ondelete="CASCADE"),
        index=True,
    )
    check_item_id: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        ForeignKey("stage_check_items.id", ondelete="CASCADE"),
        index=True,
    )
    is_done: Mapped[bool] = mapped_column(Boolean, default=False)
    note: Mapped[str | None] = mapped_column(Text, nullable=True)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))

    __table_args__ = (
        UniqueConstraint(
            "project_id",
            "check_item_id",
            name="uq_project_check_results_project_check_item",
        ),
    )


class ProjectNoteModel(Base):
    __tablename__ = "project_notes"

    id: Mapped[str] = mapped_column(UUID(as_uuid=False), primary_key=True)
    project_id: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        ForeignKey("projects.id", ondelete="CASCADE"),
        index=True,
    )
    stage_id: Mapped[str | None] = mapped_column(
        UUID(as_uuid=False),
        ForeignKey("stages.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    body: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))


class ProjectMediaModel(Base):
    __tablename__ = "project_media"

    id: Mapped[str] = mapped_column(UUID(as_uuid=False), primary_key=True)
    project_id: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        ForeignKey("projects.id", ondelete="CASCADE"),
        index=True,
    )
    stage_id: Mapped[str | None] = mapped_column(
        UUID(as_uuid=False),
        ForeignKey("stages.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    storage_path: Mapped[str] = mapped_column(Text)
    caption: Mapped[str | None] = mapped_column(Text, nullable=True)
    taken_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))


class AIConversationModel(Base):
    __tablename__ = "ai_conversations"

    id: Mapped[str] = mapped_column(UUID(as_uuid=False), primary_key=True)
    project_id: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        ForeignKey("projects.id", ondelete="CASCADE"),
        index=True,
    )
    stage_id: Mapped[str | None] = mapped_column(
        UUID(as_uuid=False),
        ForeignKey("stages.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    user_id: Mapped[str] = mapped_column(Text)
    user_message: Mapped[str] = mapped_column(Text)
    ai_answer: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))

