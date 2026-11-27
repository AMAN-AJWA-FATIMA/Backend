from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.family import FamilyLink


def verify_parent_student_access(
    db: Session, parent_id: int, student_id: int
) -> FamilyLink:
    """Centralized authorization guard: parent may access only linked students."""
    link = db.scalar(
        select(FamilyLink).where(
            FamilyLink.parent_id == parent_id,
            FamilyLink.student_id == student_id,
        )
    )
    if link is None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not linked to this student.",
        )
    return link
