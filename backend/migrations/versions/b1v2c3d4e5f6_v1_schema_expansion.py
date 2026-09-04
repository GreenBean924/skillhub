"""v1 schema expansion

Revision ID: b1v2c3d4e5f6
Revises: 9ac69da99dd0
Create Date: 2026-09-04 10:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
from pgvector.sqlalchemy import Vector

revision: str = "b1v2c3d4e5f6"
down_revision: Union[str, None] = "9ac69da99dd0"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("CREATE EXTENSION IF NOT EXISTS vector")

    op.drop_index("ix_skills_security_level", table_name="skills")

    op.alter_column(
        "skills",
        "security_level",
        new_column_name="risk_level",
        existing_type=sa.String(20),
        nullable=False,
    )

    op.create_check_constraint(
        "skills_risk_level_check",
        "skills",
        "risk_level IN ('safe', 'low', 'medium', 'high', 'critical', 'pending')",
    )
    op.create_index("ix_skills_risk_level", "skills", ["risk_level"], unique=False)

    op.alter_column("skills", "install_command", existing_type=sa.Text(), nullable=True)

    op.add_column("skills", sa.Column("version", sa.String(50), nullable=True))
    op.add_column("skills", sa.Column("registry", sa.String(255), nullable=True))
    op.add_column("skills", sa.Column("source_url", sa.Text(), nullable=True))
    op.add_column("skills", sa.Column("skill_md", sa.Text(), nullable=True))
    op.add_column("skills", sa.Column("install_count", sa.Integer(), nullable=False, server_default="0"))
    op.add_column("skills", sa.Column("trending_score", sa.Float(), nullable=False, server_default="0"))
    op.add_column("skills", sa.Column("reviewed_at", sa.DateTime(timezone=True), nullable=True))
    op.add_column("skills", sa.Column("review_version", sa.String(50), nullable=True))
    op.add_column("skills", sa.Column("embedding", Vector(1536), nullable=True))

    op.execute("CREATE INDEX ix_skills_embedding ON skills USING hnsw (embedding vector_cosine_ops)")

    op.create_table(
        "install_logs",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("skill_id", sa.UUID(), nullable=False),
        sa.Column("source", sa.String(50), nullable=False, server_default="cli"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(["skill_id"], ["skills.id"], ondelete="CASCADE"),
    )
    op.create_index("ix_install_logs_skill_id", "install_logs", ["skill_id"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_install_logs_skill_id", table_name="install_logs")
    op.drop_table("install_logs")

    op.execute("DROP INDEX IF EXISTS ix_skills_embedding")
    op.drop_column("skills", "embedding")
    op.drop_column("skills", "review_version")
    op.drop_column("skills", "reviewed_at")
    op.drop_column("skills", "trending_score")
    op.drop_column("skills", "install_count")
    op.drop_column("skills", "skill_md")
    op.drop_column("skills", "source_url")
    op.drop_column("skills", "registry")
    op.drop_column("skills", "version")

    op.alter_column("skills", "install_command", existing_type=sa.Text(), nullable=False)

    op.drop_index("ix_skills_risk_level", table_name="skills")
    op.alter_column(
        "skills",
        "risk_level",
        new_column_name="security_level",
        existing_type=sa.String(20),
        nullable=False,
    )
    op.create_index("ix_skills_security_level", "skills", ["security_level"], unique=False)
