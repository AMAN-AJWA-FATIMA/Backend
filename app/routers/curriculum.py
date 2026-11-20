
from math import ceil
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import ValidationError
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.dependencies.permissions import require_roles
from app.models.curriculum import Book, Chapter, Grade, Page, Subject, Topic
from app.models.user import User
from app.schemas import curriculum as schemas

router = APIRouter(prefix="/curriculum", tags=["Curriculum"])

DB = Annotated[Session, Depends(get_db)]
Admin = Annotated[User, Depends(require_roles("admin"))]

RESOURCES = {
    "grades": (Grade, schemas.GradeCreate, schemas.GradeUpdate),
    "subjects": (Subject, schemas.SubjectCreate, schemas.SubjectUpdate),
    "books": (Book, schemas.BookCreate, schemas.BookUpdate),
    "chapters": (Chapter, schemas.ChapterCreate, schemas.ChapterUpdate),
    "pages": (Page, schemas.PageCreate, schemas.PageUpdate),
    "topics": (Topic, schemas.TopicCreate, schemas.TopicUpdate),
}

REQUIRED_UPDATE_FIELDS = {
    "grades": {"name"},
    "subjects": {"grade_id", "name"},
    "books": {"subject_id", "title", "published"},
    "chapters": {"book_id", "chapter_no", "title"},
    "pages": {"book_id", "chapter_id", "page_no"},
    "topics": {"chapter_id", "tag"},
}


def paginate(db: Session, statement, page: int, page_size: int):
    total = db.scalar(select(func.count()).select_from(statement.subquery())) or 0
    items = db.scalars(
        statement.offset((page - 1) * page_size).limit(page_size)
    ).all()

    return {
        "items": items,
        "total": total,
        "page": page,
        "page_size": page_size,
        "pages": ceil(total / page_size) if total else 0,
    }


def get_resource(resource: str):
    if resource not in RESOURCES:
        raise HTTPException(
            status_code=404,
            detail="Curriculum resource not found.",
        )
    return RESOURCES[resource]


def get_record(db: Session, model, record_id: UUID):
    record = db.get(model, record_id)

    if record is None:
        raise HTTPException(
            status_code=404,
            detail="Record not found.",
        )

    return record


def validate_relationships(db: Session, resource: str, data: dict):
    checks = {
        "subjects": [("grade_id", Grade)],
        "books": [("subject_id", Subject)],
        "chapters": [("book_id", Book)],
        "pages": [("book_id", Book), ("chapter_id", Chapter)],
        "topics": [("chapter_id", Chapter)],
    }

    for field, model in checks.get(resource, []):
        value = data.get(field)

        if value is not None and db.get(model, value) is None:
            raise HTTPException(
                status_code=404,
                detail=f"Referenced {field} record not found.",
            )

    if resource == "pages" and data.get("book_id") and data.get("chapter_id"):
        chapter = db.get(Chapter, data["chapter_id"])

        if chapter.book_id != data["book_id"]:
            raise HTTPException(
                status_code=422,
                detail="The chapter must belong to the specified book.",
            )


@router.get("/grades")
def list_grades(
    db: DB,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
):
    return paginate(
        db,
        select(Grade).order_by(Grade.name),
        page,
        page_size,
    )


@router.get("/grades/{grade_id}/subjects")
def list_subjects(
    grade_id: UUID,
    db: DB,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
):
    get_record(db, Grade, grade_id)

    return paginate(
        db,
        select(Subject)
        .where(Subject.grade_id == grade_id)
        .order_by(Subject.name),
        page,
        page_size,
    )


@router.get("/subjects/{subject_id}/books")
def list_books(
    subject_id: UUID,
    db: DB,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
):
    get_record(db, Subject, subject_id)

    return paginate(
        db,
        select(Book)
        .where(
            Book.subject_id == subject_id,
            Book.published.is_(True),
        )
        .order_by(Book.title),
        page,
        page_size,
    )


@router.get("/books/{book_id}/chapters")
def list_chapters(
    book_id: UUID,
    db: DB,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
):
    book = get_record(db, Book, book_id)

    if not book.published:
        raise HTTPException(
            status_code=404,
            detail="Book not found.",
        )

    return paginate(
        db,
        select(Chapter)
        .where(Chapter.book_id == book_id)
        .order_by(Chapter.chapter_no),
        page,
        page_size,
    )


@router.get("/chapters/{chapter_id}/pages")
def list_pages(
    chapter_id: UUID,
    db: DB,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
):
    chapter = get_record(db, Chapter, chapter_id)
    book = get_record(db, Book, chapter.book_id)

    if not book.published:
        raise HTTPException(
            status_code=404,
            detail="Book not found.",
        )

    return paginate(
        db,
        select(Page)
        .where(Page.chapter_id == chapter_id)
        .order_by(Page.page_no),
        page,
        page_size,
    )


@router.post(
    "/admin/{resource}",
    status_code=status.HTTP_201_CREATED,
)
def create_curriculum_record(
    resource: str,
    payload: dict,
    db: DB,
    admin: Admin,
):
    model, create_schema, _ = get_resource(resource)

    try:
        data = create_schema.model_validate(payload).model_dump()

        if data.get("image_url") is not None:
            data["image_url"] = str(data["image_url"])

    except ValidationError as exc:
        raise HTTPException(
            status_code=422,
            detail=exc.errors(include_context=False),
        ) from exc

    validate_relationships(db, resource, data)

    record = model(**data)
    db.add(record)
    db.commit()
    db.refresh(record)

    return record


@router.patch("/admin/{resource}/{record_id}")
def update_curriculum_record(
    resource: str,
    record_id: UUID,
    payload: dict,
    db: DB,
    admin: Admin,
):
    model, _, update_schema = get_resource(resource)
    record = get_record(db, model, record_id)

    try:
        data = update_schema.model_validate(payload).model_dump(
            exclude_unset=True
        )

        if data.get("image_url") is not None:
            data["image_url"] = str(data["image_url"])

    except ValidationError as exc:
        raise HTTPException(
            status_code=422,
            detail=exc.errors(include_context=False),
        ) from exc

    if not data:
        raise HTTPException(
            status_code=422,
            detail="No update fields provided.",
        )

    null_fields = [
        field
        for field in REQUIRED_UPDATE_FIELDS[resource]
        if field in data and data[field] is None
    ]

    if null_fields:
        raise HTTPException(
            status_code=422,
            detail=(
                "These fields cannot be null: "
                f"{', '.join(null_fields)}"
            ),
        )

    if resource == "pages":
        merged = {
            "book_id": record.book_id,
            "chapter_id": record.chapter_id,
        }
        merged.update(data)
        validate_relationships(db, resource, merged)
    else:
        validate_relationships(db, resource, data)

    for field, value in data.items():
        setattr(record, field, value)

    db.commit()
    db.refresh(record)

    return record


@router.delete(
    "/admin/{resource}/{record_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_curriculum_record(
    resource: str,
    record_id: UUID,
    db: DB,
    admin: Admin,
):
    model, _, _ = get_resource(resource)
    record = get_record(db, model, record_id)

    db.delete(record)
    db.commit()

    return None

