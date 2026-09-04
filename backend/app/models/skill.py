import uuid
from datetime import datetime

from pgvector.sqlalchemy import Vector
from sqlalchemy import (
    CheckConstraint,
    DateTime,
    Float,
    Index,
    Integer,
    String,
    Text,
    func,
)
from sqlalchemy.dialects.postgresql import ARRAY, JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class Skill(Base):
    __tablename__ = "skills"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    slug: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    author: Mapped[str] = mapped_column(String(255), nullable=False)
    version: Mapped[str | None] = mapped_column(String(50), nullable=True)
    registry: Mapped[str | None] = mapped_column(String(255), nullable=True)
    source_url: Mapped[str | None] = mapped_column(Text, nullable=True)
    tags: Mapped[list[str]] = mapped_column(ARRAY(String), nullable=False, default=list)
    capabilities: Mapped[list[str]] = mapped_column(ARRAY(String), nullable=False, default=list)
    risk_level: Mapped[str] = mapped_column(
        String(20),
        CheckConstraint("risk_level IN ('safe', 'low', 'medium', 'high', 'critical', 'pending')"),
        nullable=False,
        index=True,
    )
    security_score: Mapped[int] = mapped_column(Integer, nullable=False)
    security_report: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)
    install_command: Mapped[str | None] = mapped_column(Text, nullable=True)
    downloads: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    stars: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    install_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    trending_score: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    content: Mapped[str | None] = mapped_column(Text, nullable=True)
    skill_md: Mapped[str | None] = mapped_column(Text, nullable=True)
    embedding = mapped_column(Vector(1536), nullable=True)
    reviewed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    review_version: Mapped[str | None] = mapped_column(String(50), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )

    __table_args__ = (
        Index("ix_skills_tags", "tags", postgresql_using="gin"),
        Index("ix_skills_capabilities", "capabilities", postgresql_using="gin"),
        Index("ix_skills_created_at_desc", "created_at", postgresql_ops={"created_at": "DESC"}),
    )
