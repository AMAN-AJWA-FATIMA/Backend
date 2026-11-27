from datetime import date, datetime
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

Language = Literal["English", "Urdu"]


class StudentProfileCreate(BaseModel):
    name: str = Field(min_length=1, max_length=150)
    grade_id: str
    school: str | None = Field(default=None, max_length=200)
    exam_date: date | None = None
    preferred_language: Language = "English"
    date_of_birth: date | None = None


class StudentProfileUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=150)
    grade_id: str | None = None
    school: str | None = Field(default=None, max_length=200)
    exam_date: date | None = None
    preferred_language: Language | None = None
    date_of_birth: date | None = None


class StudentProfileRead(BaseModel):
    user_id: int
    name: str
    grade_id: UUID
    school: str | None
    exam_date: date | None
    preferred_language: Language
    date_of_birth: date | None
    parent_consent_given: bool
    parent_consent_date: datetime | None

    model_config = ConfigDict(from_attributes=True)


class ParentProfileCreate(BaseModel):
    name: str = Field(min_length=1, max_length=150)
    phone: str | None = Field(default=None, max_length=30)


class ParentProfileUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=150)
    phone: str | None = Field(default=None, max_length=30)


class ParentProfileRead(BaseModel):
    user_id: int
    name: str
    phone: str | None

    model_config = ConfigDict(from_attributes=True)


class InviteRead(BaseModel):
    code: str
    expires_at: datetime


class LinkByCode(BaseModel):
    code: str = Field(min_length=6, max_length=6)


class FamilyLinkRead(BaseModel):
    parent_id: int
    student_id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ConsentRequest(BaseModel):
    consent_given: Literal[True]


class ConsentRead(BaseModel):
    student_id: int
    consent_given: bool
    consent_date: datetime
    consent_parent_id: int
