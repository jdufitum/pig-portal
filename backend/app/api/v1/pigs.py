from __future__ import annotations

import uuid
from datetime import date
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import and_, or_, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from ...deps import get_db, get_current_user
from ...models import Pig, WeightRecord
from ...roles import require_role
from ...models.user import UserRole
from ...schemas.pig import PigCreate, PigUpdate, PigOut
from ...schemas.weight import WeightCreate, WeightOut


router = APIRouter(prefix="/pigs", tags=["pigs"], responses={404: {"description": "Not found"}})


@router.post("/", response_model=PigOut, status_code=status.HTTP_201_CREATED)
def create_pig(payload: PigCreate, db: Session = Depends(get_db), _=Depends(require_role(UserRole.OWNER))):
    pig = Pig(
        ear_tag=payload.ear_tag.strip(),
        sex=payload.sex,
        breed=payload.breed,
        birth_date=payload.birth_date,
        pig_class=payload.pig_class,
        source=payload.source,
        status=payload.status or "active",
        current_pen=payload.current_pen,
        sire_id=payload.sire_id,
        dam_id=payload.dam_id,
    )
    db.add(pig)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Duplicate ear_tag")
    db.refresh(pig)
    return pig


@router.get("/", response_model=List[PigOut])
def list_pigs(
    db: Session = Depends(get_db),
    _user=Depends(get_current_user),
    search: Optional[str] = Query(None, description="Search by ear_tag"),
    status_filter: Optional[str] = Query(None, alias="status", pattern="^(active|sold|dead)$"),
    sex: Optional[str] = Query(None, pattern="^(M|F)$"),
    pen: Optional[str] = Query(None),
):
    query = db.query(Pig)
    conditions = []
    if search:
        like = f"%{search}%"
        conditions.append(Pig.ear_tag.ilike(like))
    if status_filter:
        conditions.append(Pig.status == status_filter)
    if sex:
        conditions.append(Pig.sex == sex)
    if pen:
        conditions.append(Pig.current_pen == pen)
    if conditions:
        query = query.filter(and_(*conditions))
    query = query.order_by(Pig.created_at.desc())
    return query.all()


@router.get("/{pig_id}", response_model=PigOut)
def get_pig(pig_id: uuid.UUID, db: Session = Depends(get_db), _user=Depends(get_current_user)):
    pig = db.get(Pig, pig_id)
    if not pig:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Pig not found")
    return pig


@router.patch("/{pig_id}", response_model=PigOut)
def update_pig(
    pig_id: uuid.UUID,
    payload: PigUpdate,
    db: Session = Depends(get_db),
    _=Depends(require_role(UserRole.OWNER)),
):
    pig = db.get(Pig, pig_id)
    if not pig:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Pig not found")

    data = payload.model_dump(exclude_unset=True, by_alias=True)
    # Map alias 'class' to model attribute 'pig_class' already configured via column name
    if "class" in data:
        data["pig_class"] = data.pop("class")
    for key, value in data.items():
        if hasattr(pig, key):
            setattr(pig, key, value)
    db.add(pig)
    db.commit()
    db.refresh(pig)
    return pig


# Weights sub-routes
@router.post("/{pig_id}/weights", response_model=WeightOut, status_code=status.HTTP_201_CREATED)
def add_weight(pig_id: uuid.UUID, payload: WeightCreate, db: Session = Depends(get_db), _=Depends(require_role(UserRole.WORKER, UserRole.OWNER))):
    pig = db.get(Pig, pig_id)
    if not pig:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Pig not found")

    record = WeightRecord(pig_id=pig_id, date=payload.date, weight_kg=payload.weight_kg, notes=payload.notes)
    db.add(record)
    db.commit()
    db.refresh(record)
    return record


@router.get("/{pig_id}/weights", response_model=List[WeightOut])
def list_weights(
    pig_id: uuid.UUID,
    db: Session = Depends(get_db),
    _user=Depends(get_current_user),
    from_date: Optional[date] = Query(None, alias="from"),
    to_date: Optional[date] = Query(None, alias="to"),
):
    pig = db.get(Pig, pig_id)
    if not pig:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Pig not found")

    query = db.query(WeightRecord).filter(WeightRecord.pig_id == pig_id)
    if from_date:
        query = query.filter(WeightRecord.date >= from_date)
    if to_date:
        query = query.filter(WeightRecord.date <= to_date)
    return query.order_by(WeightRecord.date.asc()).all()


@router.get("/{pig_id}/growth-curve")
def growth_curve(
    pig_id: uuid.UUID,
    db: Session = Depends(get_db),
    _user=Depends(get_current_user),
    from_date: Optional[date] = Query(None, alias="from"),
    to_date: Optional[date] = Query(None, alias="to"),
):
    pig = db.get(Pig, pig_id)
    if not pig:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Pig not found")

    query = db.query(WeightRecord).filter(WeightRecord.pig_id == pig_id)
    if from_date:
        query = query.filter(WeightRecord.date >= from_date)
    if to_date:
        query = query.filter(WeightRecord.date <= to_date)
    records = query.order_by(WeightRecord.date.asc()).all()
    return [{"date": r.date.isoformat(), "kg": float(r.weight_kg)} for r in records]

