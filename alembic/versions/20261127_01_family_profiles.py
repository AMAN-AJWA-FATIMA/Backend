"""Add student/parent profiles and family linking.

Revision ID: 20261127_01
Revises: 20261120_01
"""

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

revision = "20261127_01"
down_revision = "20261120_01"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "student_profiles",
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=150), nullable=False),
        sa.Column("grade_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("school", sa.String(length=200), nullable=True),
        sa.Column("exam_date", sa.Date(), nullable=True),
        sa.Column("preferred_language", sa.String(length=10), nullable=False),
        sa.Column("date_of_birth", sa.Date(), nullable=True),
        sa.Column(
            "parent_consent_given",
            sa.Boolean(),
            nullable=False,
            server_default=sa.false(),
        ),
        sa.Column("parent_consent_date", sa.DateTime(timezone=True), nullable=True),
        sa.Column("consent_parent_id", sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["grade_id"], ["grades.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(
            ["consent_parent_id"], ["users.id"], ondelete="SET NULL"
        ),
        sa.PrimaryKeyConstraint("user_id"),
    )
    op.create_table(
        "parent_profiles",
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=150), nullable=False),
        sa.Column("phone", sa.String(length=30), nullable=True),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("user_id"),
    )
    op.create_table(
        "family_links",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("parent_id", sa.Integer(), nullable=False),
        sa.Column("student_id", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["parent_id"], ["users.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["student_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("parent_id", "student_id", name="uq_family_parent_student"),
    )
    op.create_index("ix_family_links_parent_id", "family_links", ["parent_id"])
    op.create_index("ix_family_links_student_id", "family_links", ["student_id"])
    op.create_table(
        "family_invites",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("student_id", sa.Integer(), nullable=False),
        sa.Column("code_digest", sa.String(length=64), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("used_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["student_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("code_digest"),
    )
    op.create_index("ix_family_invites_student_id", "family_invites", ["student_id"])
    op.create_index("ix_family_invites_code_digest", "family_invites", ["code_digest"])


def downgrade() -> None:
    op.drop_index("ix_family_invites_code_digest", table_name="family_invites")
    op.drop_index("ix_family_invites_student_id", table_name="family_invites")
    op.drop_table("family_invites")
    op.drop_index("ix_family_links_student_id", table_name="family_links")
    op.drop_index("ix_family_links_parent_id", table_name="family_links")
    op.drop_table("family_links")
    op.drop_table("parent_profiles")
    op.drop_table("student_profiles")
