import secrets
from datetime import datetime, timedelta, timezone
from hashlib import sha256
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.dependencies.authentication import get_current_user
from app.dependencies.family_access import verify_parent_student_access
from app.dependencies.permissions import require_roles
from app.models.curriculum import Grade
from app.models.family import FamilyInvite, FamilyLink, ParentProfile, StudentProfile
from app.models.user import User
from app.schemas import family as schemas

router = APIRouter(tags=["Profiles & Family"])
DB = Annotated[Session, Depends(get_db)]
Student = Annotated[User, Depends(require_roles("student"))]
Parent = Annotated[User, Depends(require_roles("parent"))]
CurrentUser = Annotated[User, Depends(get_current_user)]


def now_utc() -> datetime:
    return datetime.now(timezone.utc)


def digest_code(code: str) -> str:
    return sha256(code.encode("utf-8")).hexdigest()


def require_student_profile(db: Session, user_id: int) -> StudentProfile:
    profile = db.get(StudentProfile, user_id)
    if profile is None:
        raise HTTPException(status_code=404, detail="Student profile not found.")
    return profile


def require_parent_profile(db: Session, user_id: int) -> ParentProfile:
    profile = db.get(ParentProfile, user_id)
    if profile is None:
        raise HTTPException(status_code=404, detail="Parent profile not found.")
    return profile


@router.post(
    "/profiles/student", response_model=schemas.StudentProfileRead, status_code=201
)
def create_student_profile(
    payload: schemas.StudentProfileCreate, db: DB, user: Student
):
    if db.get(StudentProfile, user.id):
        raise HTTPException(status_code=409, detail="Student profile already exists.")
    try:
        grade_uuid = UUID(payload.grade_id)
    except ValueError:
        raise HTTPException(
            status_code=422, detail="grade_id must be a valid UUID."
        ) from None
    if db.get(Grade, grade_uuid) is None:
        raise HTTPException(status_code=404, detail="Grade not found.")
    profile = StudentProfile(
        user_id=user.id,
        name=payload.name,
        grade_id=grade_uuid,
        school=payload.school,
        exam_date=payload.exam_date,
        preferred_language=payload.preferred_language,
        date_of_birth=payload.date_of_birth,
    )
    db.add(profile)
    db.commit()
    db.refresh(profile)
    return profile


@router.get("/profiles/student/me", response_model=schemas.StudentProfileRead)
def get_student_profile(db: DB, user: Student):
    return require_student_profile(db, user.id)


@router.patch("/profiles/student/me", response_model=schemas.StudentProfileRead)
def update_student_profile(
    payload: schemas.StudentProfileUpdate, db: DB, user: Student
):
    profile = require_student_profile(db, user.id)
    data = payload.model_dump(exclude_unset=True)
    if "grade_id" in data and data["grade_id"] is not None:
        try:
            grade_uuid = UUID(data["grade_id"])
        except ValueError:
            raise HTTPException(
                status_code=422, detail="grade_id must be a valid UUID."
            ) from None
        if db.get(Grade, grade_uuid) is None:
            raise HTTPException(status_code=404, detail="Grade not found.")
        data["grade_id"] = grade_uuid
    for key, value in data.items():
        setattr(profile, key, value)
    db.commit()
    db.refresh(profile)
    return profile


@router.post(
    "/profiles/parent", response_model=schemas.ParentProfileRead, status_code=201
)
def create_parent_profile(payload: schemas.ParentProfileCreate, db: DB, user: Parent):
    if db.get(ParentProfile, user.id):
        raise HTTPException(status_code=409, detail="Parent profile already exists.")
    profile = ParentProfile(user_id=user.id, name=payload.name, phone=payload.phone)
    db.add(profile)
    db.commit()
    db.refresh(profile)
    return profile


@router.get("/profiles/parent/me", response_model=schemas.ParentProfileRead)
def get_parent_profile(db: DB, user: Parent):
    return require_parent_profile(db, user.id)


@router.patch("/profiles/parent/me", response_model=schemas.ParentProfileRead)
def update_parent_profile(payload: schemas.ParentProfileUpdate, db: DB, user: Parent):
    profile = require_parent_profile(db, user.id)
    for key, value in payload.model_dump(exclude_unset=True).items():
        setattr(profile, key, value)
    db.commit()
    db.refresh(profile)
    return profile


@router.post("/family/invites", response_model=schemas.InviteRead, status_code=201)
def generate_invite(db: DB, user: Student):
    require_student_profile(db, user.id)
    # Codes are returned once; only their SHA-256 digest is persisted.
    alphabet = "ABCDEFGHJKLMNPQRSTUVWXYZ23456789"
    for _ in range(10):
        code = "".join(secrets.choice(alphabet) for _ in range(6))
        digest = digest_code(code)
        if (
            db.scalar(select(FamilyInvite).where(FamilyInvite.code_digest == digest))
            is None
        ):
            break
    else:
        raise HTTPException(
            status_code=503, detail="Could not generate an invite code."
        )
    expires = now_utc() + timedelta(hours=48)
    invite = FamilyInvite(student_id=user.id, code_digest=digest, expires_at=expires)
    db.add(invite)
    db.commit()
    return {"code": code, "expires_at": expires}


@router.post("/family/link", response_model=schemas.FamilyLinkRead, status_code=201)
def link_student(payload: schemas.LinkByCode, db: DB, parent: Parent):
    require_parent_profile(db, parent.id)
    invite = db.scalar(
        select(FamilyInvite).where(
            FamilyInvite.code_digest == digest_code(payload.code)
        )
    )
    current = now_utc()

    if invite is None or invite.used_at is not None:
        raise HTTPException(
            status_code=400,
            detail="Invalid or expired invitation code",
        )

    expires = invite.expires_at

    # SQLite may return timezone-naive datetime values.
    if expires.tzinfo is None:
        expires = expires.replace(tzinfo=timezone.utc)

    if expires <= current:
        raise HTTPException(
            status_code=400,
            detail="Invalid or expired invitation code",
        )

    if invite.student_id == parent.id:
        raise HTTPException(status_code=400, detail="Cannot link a user to themselves.")
    if db.scalar(
        select(FamilyLink).where(
            FamilyLink.parent_id == parent.id,
            FamilyLink.student_id == invite.student_id,
        )
    ):
        raise HTTPException(status_code=409, detail="This student is already linked.")
    link = FamilyLink(parent_id=parent.id, student_id=invite.student_id)
    invite.used_at = current
    db.add(link)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail="Link already exists.") from None
    db.refresh(link)
    return link


@router.get("/family/children", response_model=list[schemas.StudentProfileRead])
def list_linked_children(db: DB, parent: Parent):
    require_parent_profile(db, parent.id)
    ids = db.scalars(
        select(FamilyLink.student_id).where(FamilyLink.parent_id == parent.id)
    ).all()
    return db.scalars(
        select(StudentProfile).where(StudentProfile.user_id.in_(ids))
    ).all()


@router.get("/family/children/{student_id}", response_model=schemas.StudentProfileRead)
def read_linked_student(student_id: int, db: DB, parent: Parent):
    require_parent_profile(db, parent.id)
    verify_parent_student_access(db, parent.id, student_id)
    return require_student_profile(db, student_id)


@router.post(
    "/family/children/{student_id}/consent",
    response_model=schemas.ConsentRead,
)
def record_parent_consent(
    student_id: int, payload: schemas.ConsentRequest, db: DB, parent: Parent
):
    require_parent_profile(db, parent.id)
    verify_parent_student_access(db, parent.id, student_id)
    profile = require_student_profile(db, student_id)
    if profile.date_of_birth is None:
        raise HTTPException(
            status_code=422,
            detail="Student date of birth is required to determine age.",
        )
    today = now_utc().date()
    age = (
        today.year
        - profile.date_of_birth.year
        - (
            (today.month, today.day)
            < (profile.date_of_birth.month, profile.date_of_birth.day)
        )
    )
    if age >= 18:
        raise HTTPException(
            status_code=400, detail="Consent is only required for students under 18."
        )
    profile.parent_consent_given = True
    profile.parent_consent_date = now_utc()
    profile.consent_parent_id = parent.id
    db.commit()
    return {
        "student_id": student_id,
        "consent_given": profile.parent_consent_given,
        "consent_date": profile.parent_consent_date,
        "consent_parent_id": profile.consent_parent_id,
    }
