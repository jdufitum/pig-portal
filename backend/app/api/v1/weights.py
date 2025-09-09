from __future__ import annotations

from datetime import date
from typing import List, Optional
import uuid

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from ...deps import get_db
from ...models import WeightRecord, Pig
from ...roles import require_role
from ...models.user import UserRole
from ...schemas.weight import WeightCreate, WeightOut


router = APIRouter(prefix="/weights", tags=["weights"])


class WeightCreateWithPig(WeightCreate):
    pig_id: uuid.UUID


@router.post("/", response_model=WeightOut, status_code=status.HTTP_201_CREATED)
def create_weight(payload: WeightCreateWithPig, db: Session = Depends(get_db), _=Depends(require_role(UserRole.WORKER, UserRole.OWNER))):
    pig = db.get(Pig, payload.pig_id)
    if not pig:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Pig not found")
    if payload.date > date.today():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="date cannot be in the future")
    record = WeightRecord(pig_id=payload.pig_id, date=payload.date, weight_kg=payload.weight_kg, notes=payload.notes)
    db.add(record)
    db.commit()
    db.refresh(record)
    return record


@router.get("/", response_model=List[WeightOut])
def list_weights(
    db: Session = Depends(get_db),
    pig_id: Optional[uuid.UUID] = None,
    from_date: Optional[date] = Query(None, alias="from"),
    to_date: Optional[date] = Query(None, alias="to"),
):
    q = db.query(WeightRecord)
    if pig_id:
        q = q.filter(WeightRecord.pig_id == pig_id)
    if from_date:
        q = q.filter(WeightRecord.date >= from_date)
    if to_date:
        q = q.filter(WeightRecord.date <= to_date)
    return q.order_by(WeightRecord.date.asc()).all()

