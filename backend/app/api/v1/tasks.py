from __future__ import annotations

from datetime import date, datetime, timedelta
from typing import List, Optional
import uuid

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from ...deps import get_db
from ...models import Task
from ...roles import require_role
from ...models.user import UserRole
from ...schemas.task import TaskCreate, TaskUpdate, TaskOut


router = APIRouter(prefix="/tasks", tags=["tasks"])


@router.post("/", response_model=TaskOut, status_code=status.HTTP_201_CREATED)
def create_task(payload: TaskCreate, db: Session = Depends(get_db), _=Depends(require_role(UserRole.WORKER, UserRole.OWNER))):
    task = Task(**payload.model_dump(exclude_none=True))
    db.add(task)
    db.commit()
    db.refresh(task)
    return task


@router.get("/", response_model=List[TaskOut])
def list_tasks(
    db: Session = Depends(get_db),
    status_filter: Optional[str] = Query(None, alias="status", pattern="^(open|done)$"),
    due_before: Optional[date] = None,
    assigned_to: Optional[uuid.UUID] = None,
):
    q = db.query(Task)
    if status_filter:
        q = q.filter(Task.status == status_filter)
    if due_before:
        q = q.filter(Task.due_date <= due_before)
    if assigned_to:
        q = q.filter(Task.assigned_to == assigned_to)
    return q.order_by(Task.due_date.asc()).all()


@router.patch("/{task_id}", response_model=TaskOut)
def update_task(task_id: uuid.UUID, payload: TaskUpdate, db: Session = Depends(get_db), _=Depends(require_role(UserRole.WORKER, UserRole.OWNER))):
    task = db.get(Task, task_id)
    if not task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
    for k, v in payload.model_dump(exclude_unset=True).items():
        setattr(task, k, v)
    db.add(task)
    db.commit()
    db.refresh(task)
    return task


@router.get("/summary")
def task_summary(db: Session = Depends(get_db)) -> dict[str, int]:
    today = date.today()
    next_week = today + timedelta(days=7)

    open_count = db.query(Task).filter(Task.status == "open").count()
    overdue_count = db.query(Task).filter(Task.status == "open", Task.due_date < today).count()
    due_next_7 = db.query(Task).filter(Task.status == "open", Task.due_date >= today, Task.due_date <= next_week).count()
    return {"open": open_count, "overdue": overdue_count, "due_next_7_days": due_next_7}

