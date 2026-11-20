
from sqlalchemy import select

from app.core.database import SessionLocal
from app.models.curriculum import Book, Chapter, Grade, Subject


def get_or_create(db, model, filters, defaults):
    record = db.scalar(select(model).filter_by(**filters))
    if record is None:
        record = model(**filters, **defaults)
        db.add(record)
        db.flush()
    return record


def seed_curriculum():
    with SessionLocal() as db:
        try:
            grade_6 = get_or_create(
                db, Grade, {"name": "Grade 6"}, {}
            )
            grade_7 = get_or_create(
                db, Grade, {"name": "Grade 7"}, {}
            )

            mathematics = get_or_create(
                db,
                Subject,
                {"grade_id": grade_6.id, "name": "Mathematics"},
                {},
            )
            science = get_or_create(
                db,
                Subject,
                {"grade_id": grade_6.id, "name": "Science"},
                {},
            )
            get_or_create(
                db,
                Subject,
                {"grade_id": grade_7.id, "name": "English"},
                {},
            )

            books_data = [
                (
                    mathematics,
                    "Grade 6 Mathematics",
                    "Mathematics textbook for Grade 6.",
                ),
                (
                    science,
                    "Grade 6 Science",
                    "Science textbook for Grade 6.",
                ),
            ]

            for subject, title, description in books_data:
                book = get_or_create(
                    db,
                    Book,
                    {"subject_id": subject.id, "title": title},
                    {"description": description, "published": True},
                )

                for number in range(1, 6):
                    get_or_create(
                        db,
                        Chapter,
                        {"book_id": book.id, "chapter_no": number},
                        {"title": f"Chapter {number}"},
                    )

            db.commit()
            print("Curriculum seed completed successfully.")
            print("Grades: 2 | Subjects: 3 | Books: 2 | Chapters: 10")

        except Exception:
            db.rollback()
            raise


if __name__ == "__main__":
    seed_curriculum()
