"""Add authentication fields and refresh token storage.

Revision ID: 20261113_01
Revises:
"""

import sqlalchemy as sa

from alembic import op

revision = "20261113_01"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Preserve existing users. Legacy rows have NULL password_hash and cannot
    # authenticate until a password-reset process is provided.
    op.add_column(
        "users", sa.Column("password_hash", sa.String(length=255), nullable=True)
    )
    op.add_column(
        "users",
        sa.Column(
            "role",
            sa.String(length=20),
            server_default="student",
            nullable=False,
        ),
    )

    op.create_table(
        "refresh_tokens",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column(
            "user_id",
            sa.Integer(),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("token_hash", sa.String(length=64), nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("revoked_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.UniqueConstraint("token_hash", name="uq_refresh_tokens_token_hash"),
    )
    op.create_index("ix_refresh_tokens_user_id", "refresh_tokens", ["user_id"])


def downgrade() -> None:
    op.drop_index("ix_refresh_tokens_user_id", table_name="refresh_tokens")
    op.drop_table("refresh_tokens")
    op.drop_column("users", "role")
    op.drop_column("users", "password_hash")
