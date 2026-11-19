from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.dependencies.authentication import get_current_user
from app.models import Task, User
from app.schemas.task import TaskCreate, TaskRead, TaskUpdate

router = APIRouter(prefix="/tasks", tags=["Tasks"])


def authorize_task_access(current_user: User, task: Task) -> None:
    if current_user.role == "admin":
        return
    if current_user.role != "student" or task.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Access denied.")


@router.post("/", response_model=TaskRead, status_code=status.HTTP_201_CREATED)
def create_task(
    task_data: TaskCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if current_user.role not in {"student", "admin"}:
        raise HTTPException(status_code=403, detail="Access denied.")
    if current_user.role == "student" and task_data.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Cannot create tasks for others.")

    user = db.get(User, task_data.user_id)
    if user is None:
        raise HTTPException(
            status_code=404,
            detail="The specified user does not exist.",
        )

    task = Task(
        title=task_data.title,
        description=task_data.description,
        user_id=task_data.user_id,
        is_completed=task_data.is_completed,
    )
    db.add(task)
    db.commit()
    db.refresh(task)
    return task


@router.get("/", response_model=list[TaskRead])
def get_tasks(
    user_id: int | None = Query(default=None, gt=0),
    is_completed: bool | None = None,
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=100, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if current_user.role == "parent":
        raise HTTPException(status_code=403, detail="Access denied.")

    statement = select(Task)
    if current_user.role != "admin":
        statement = statement.where(Task.user_id == current_user.id)
    elif user_id is not None:
        statement = statement.where(Task.user_id == user_id)

    if is_completed is not None:
        statement = statement.where(Task.is_completed == is_completed)

    statement = statement.order_by(Task.id).offset(skip).limit(limit)
    return db.scalars(statement).all()


@router.get("/{task_id}", response_model=TaskRead)
def get_task(
    task_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    task = db.get(Task, task_id)
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found.")
    authorize_task_access(current_user, task)
    return task


@router.patch("/{task_id}", response_model=TaskRead)
def update_task(
    task_id: int,
    task_data: TaskUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    task = db.get(Task, task_id)
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found.")
    authorize_task_access(current_user, task)

    update_data = task_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(task, field, value)
    db.commit()
    db.refresh(task)
    return task


@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_task(
    task_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    task = db.get(Task, task_id)
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found.")
    authorize_task_access(current_user, task)
    db.delete(task)
    db.commit()
