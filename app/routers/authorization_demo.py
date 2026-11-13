from fastapi import APIRouter, Depends

from app.dependencies.permissions import require_roles
from app.models.user import User

router = APIRouter(tags=["Role-Based Access"])


@router.get("/admin/dashboard")
def admin_dashboard(
    current_user: User = Depends(require_roles("admin")),
):
    return {
        "message": "Admin access granted.",
        "user_id": current_user.id,
        "role": current_user.role,
    }


@router.get("/parent/dashboard")
def parent_dashboard(
    current_user: User = Depends(require_roles("parent", "admin")),
):
    return {
        "message": "Parent access granted.",
        "user_id": current_user.id,
        "role": current_user.role,
    }
