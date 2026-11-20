
from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import (
    Boolean,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
    UniqueConstraint,
    Uuid,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class CurriculumTimestampMixin:
    id: Mapped[UUID] = mapped_column(
        Uuid(as_uuid=True), primary_key=True, default=uuid4
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )


class Grade(CurriculumTimestampMixin, Base):
    __tablename__ = "grades"

    name: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)


class Subject(CurriculumTimestampMixin, Base):
    __tablename__ = "subjects"

    grade_id: Mapped[UUID] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("grades.id", ondelete="CASCADE"), nullable=False
    )
    name: Mapped[str] = mapped_column(String(150), nullable=False)

    __table_args__ = (
        Index("ix_subjects_grade_id", "grade_id"),
        UniqueConstraint("grade_id", "name", name="uq_subjects_grade_name"),
    )


class Book(CurriculumTimestampMixin, Base):
    __tablename__ = "books"

    subject_id: Mapped[UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("subjects.id", ondelete="CASCADE"),
        nullable=False,
    )
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    published: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=False, server_default="false"
    )

    __table_args__ = (Index("ix_books_subject_id", "subject_id"),)


class Chapter(CurriculumTimestampMixin, Base):
    __tablename__ = "chapters"

    book_id: Mapped[UUID] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("books.id", ondelete="CASCADE"), nullable=False
    )
    chapter_no: Mapped[int] = mapped_column(Integer, nullable=False)
    title: Mapped[str] = mapped_column(String(200), nullable=False)

    __table_args__ = (
        Index("ix_chapters_book_id", "book_id"),
        UniqueConstraint("book_id", "chapter_no", name="uq_chapters_book_number"),
    )


class Page(CurriculumTimestampMixin, Base):
    __tablename__ = "pages"

    book_id: Mapped[UUID] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("books.id", ondelete="CASCADE"), nullable=False
    )
    chapter_id: Mapped[UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("chapters.id", ondelete="CASCADE"),
        nullable=False,
    )
    page_no: Mapped[int] = mapped_column(Integer, nullable=False)
    image_url: Mapped[str | None] = mapped_column(String(2048), nullable=True)
    text: Mapped[str | None] = mapped_column(Text, nullable=True)

    __table_args__ = (
        Index("ix_pages_book_id", "book_id"),
        Index("ix_pages_chapter_id", "chapter_id"),
        UniqueConstraint("book_id", "page_no", name="uq_pages_book_number"),
    )


class Topic(CurriculumTimestampMixin, Base):
    __tablename__ = "topics"

    chapter_id: Mapped[UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("chapters.id", ondelete="CASCADE"),
        nullable=False,
    )
    tag: Mapped[str] = mapped_column(String(100), nullable=False)

    __table_args__ = (Index("ix_topics_chapter_id", "chapter_id"),)
