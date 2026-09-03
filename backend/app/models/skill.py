import uuid
from datetime import datetime

from sqlalchemy import (
    CheckConstraint,
    DateTime,
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
    tags: Mapped[list[str]] = mapped_column(ARRAY(String), nullable=False, default=list)
    capabilities: Mapped[list[str]] = mapped_column(ARRAY(String), nullable=False, default=list)
    security_level: Mapped[str] = mapped_column(
        String(20),
        CheckConstraint("security_level IN ('safe', 'low', 'medium', 'high', 'critical')"),
        nullable=False,
        index=True,
    )
    security_score: Mapped[int] = mapped_column(Integer, nullable=False)
    security_report: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)
    install_command: Mapped[str] = mapped_column(Text, nullable=False)
    downloads: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    stars: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    content: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )

    __table_args__ = (
        Index("ix_skills_tags", "tags", postgresql_using="gin"),
        Index("ix_skills_capabilities", "capabilities", postgresql_using="gin"),
        Index("ix_skills_created_at_desc", "created_at", postgresql_ops={"created_at": "DESC"}),
    )
