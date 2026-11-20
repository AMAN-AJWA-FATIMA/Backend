
from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, HttpUrl, model_validator


class CurriculumRead(BaseModel):
    id: UUID
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class GradeCreate(BaseModel):
    name: str = Field(min_length=1, max_length=100)


class GradeUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=100)


class GradeRead(CurriculumRead):
    name: str


class SubjectCreate(BaseModel):
    grade_id: UUID
    name: str = Field(min_length=1, max_length=150)


class SubjectUpdate(BaseModel):
    grade_id: UUID | None = None
    name: str | None = Field(default=None, min_length=1, max_length=150)


class SubjectRead(CurriculumRead):
    grade_id: UUID
    name: str


class BookCreate(BaseModel):
    subject_id: UUID
    title: str = Field(min_length=1, max_length=200)
    description: str | None = None
    published: bool = False


class BookUpdate(BaseModel):
    subject_id: UUID | None = None
    title: str | None = Field(default=None, min_length=1, max_length=200)
    description: str | None = None
    published: bool | None = None


class BookRead(CurriculumRead):
    subject_id: UUID
    title: str
    description: str | None
    published: bool


class ChapterCreate(BaseModel):
    book_id: UUID
    chapter_no: int = Field(gt=0)
    title: str = Field(min_length=1, max_length=200)


class ChapterUpdate(BaseModel):
    book_id: UUID | None = None
    chapter_no: int | None = Field(default=None, gt=0)
    title: str | None = Field(default=None, min_length=1, max_length=200)


class ChapterRead(CurriculumRead):
    book_id: UUID
    chapter_no: int
    title: str


class PageCreate(BaseModel):
    book_id: UUID
    chapter_id: UUID
    page_no: int = Field(gt=0)
    image_url: HttpUrl | None = None
    text: str | None = None


class PageUpdate(BaseModel):
    book_id: UUID | None = None
    chapter_id: UUID | None = None
    page_no: int | None = Field(default=None, gt=0)
    image_url: HttpUrl | None = None
    text: str | None = None


class PageRead(CurriculumRead):
    book_id: UUID
    chapter_id: UUID
    page_no: int
    image_url: str | None
    text: str | None


class TopicCreate(BaseModel):
    chapter_id: UUID
    tag: str = Field(min_length=1, max_length=100)


class TopicUpdate(BaseModel):
    chapter_id: UUID | None = None
    tag: str | None = Field(default=None, min_length=1, max_length=100)


class TopicRead(CurriculumRead):
    chapter_id: UUID
    tag: str


class PaginatedResponse(BaseModel):
    items: list[dict]
    total: int
    page: int
    page_size: int
    pages: int


class UpdateValidation(BaseModel):
    @model_validator(mode="after")
    def validate_non_empty(self):
        if not self.model_fields_set:
            raise ValueError("At least one field must be provided.")
        return self
