from __future__ import annotations

from datetime import date
from typing import List, Optional
import uuid

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from ...deps import get_db
from ...models import HealthEvent
from ...roles import require_role
from ...models.user import UserRole
from ...schemas.health import HealthEventCreate, HealthEventOut


router = APIRouter(prefix="/health", tags=["health"], responses={404: {"description": "Not found"}})


@router.post("/", response_model=HealthEventOut, status_code=status.HTTP_201_CREATED)
def create_health_event(payload: HealthEventCreate, db: Session = Depends(get_db), _=Depends(require_role(UserRole.VET, UserRole.WORKER, UserRole.OWNER))):
    if not payload.pig_id and not payload.pen:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Provide pig_id or pen")
    event = HealthEvent(**payload.model_dump())
    db.add(event)
    db.commit()
    db.refresh(event)
    return event


@router.get("/", response_model=List[HealthEventOut])
def list_health_events(
    db: Session = Depends(get_db),
    pig_id: Optional[uuid.UUID] = None,
    pen: Optional[str] = None,
    from_date: Optional[date] = Query(None, alias="from"),
    to_date: Optional[date] = Query(None, alias="to"),
):
    q = db.query(HealthEvent)
    if pig_id:
        q = q.filter(HealthEvent.pig_id == pig_id)
    if pen:
        q = q.filter(HealthEvent.pen == pen)
    if from_date:
        q = q.filter(HealthEvent.date >= from_date)
    if to_date:
        q = q.filter(HealthEvent.date <= to_date)
    return q.order_by(HealthEvent.date.desc()).all()

