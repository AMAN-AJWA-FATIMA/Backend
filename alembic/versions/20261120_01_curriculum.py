
"""Create curriculum tables.

Revision ID: 20261120_01
Revises: 20261113_01
"""

import sqlalchemy as sa

from alembic import op

revision = "20261120_01"
down_revision = "20261113_01"
branch_labels = None
depends_on = None


def timestamp_columns():
    return [
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
    ]


def upgrade() -> None:
    op.create_table(
        "grades",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("name", sa.String(100), nullable=False, unique=True),
        *timestamp_columns(),
    )

    op.create_table(
        "subjects",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column(
            "grade_id",
            sa.Uuid(),
            sa.ForeignKey("grades.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("name", sa.String(150), nullable=False),
        *timestamp_columns(),
        sa.UniqueConstraint("grade_id", "name", name="uq_subjects_grade_name"),
    )
    op.create_index("ix_subjects_grade_id", "subjects", ["grade_id"])

    op.create_table(
        "books",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column(
            "subject_id",
            sa.Uuid(),
            sa.ForeignKey("subjects.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("title", sa.String(200), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column(
            "published",
            sa.Boolean(),
            nullable=False,
            server_default=sa.false(),
        ),
        *timestamp_columns(),
    )
    op.create_index("ix_books_subject_id", "books", ["subject_id"])

    op.create_table(
        "chapters",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column(
            "book_id",
            sa.Uuid(),
            sa.ForeignKey("books.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("chapter_no", sa.Integer(), nullable=False),
        sa.Column("title", sa.String(200), nullable=False),
        *timestamp_columns(),
        sa.UniqueConstraint("book_id", "chapter_no", name="uq_chapters_book_number"),
    )
    op.create_index("ix_chapters_book_id", "chapters", ["book_id"])

    op.create_table(
        "pages",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column(
            "book_id",
            sa.Uuid(),
            sa.ForeignKey("books.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "chapter_id",
            sa.Uuid(),
            sa.ForeignKey("chapters.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("page_no", sa.Integer(), nullable=False),
        sa.Column("image_url", sa.String(2048), nullable=True),
        sa.Column("text", sa.Text(), nullable=True),
        *timestamp_columns(),
        sa.UniqueConstraint("book_id", "page_no", name="uq_pages_book_number"),
    )
    op.create_index("ix_pages_book_id", "pages", ["book_id"])
    op.create_index("ix_pages_chapter_id", "pages", ["chapter_id"])

    op.create_table(
        "topics",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column(
            "chapter_id",
            sa.Uuid(),
            sa.ForeignKey("chapters.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("tag", sa.String(100), nullable=False),
        *timestamp_columns(),
    )
    op.create_index("ix_topics_chapter_id", "topics", ["chapter_id"])


def downgrade() -> None:
    op.drop_index("ix_topics_chapter_id", table_name="topics")
    op.drop_table("topics")
    op.drop_index("ix_pages_chapter_id", table_name="pages")
    op.drop_index("ix_pages_book_id", table_name="pages")
    op.drop_table("pages")
    op.drop_index("ix_chapters_book_id", table_name="chapters")
    op.drop_table("chapters")
    op.drop_index("ix_books_subject_id", table_name="books")
    op.drop_table("books")
    op.drop_index("ix_subjects_grade_id", table_name="subjects")
    op.drop_table("subjects")
    op.drop_table("grades")
